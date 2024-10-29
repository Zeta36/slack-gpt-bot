import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import logging
import re
import warnings
import json
from utils import OpenAIService
from utils import RedisManager
from utils import *
from tools import ToolsManager
import os
from config import Config
import time

# Setup logging
logging.basicConfig(level=logging.CRITICAL)
logger = logging.getLogger("slack_bolt")
logger.setLevel(logging.CRITICAL)
warnings.filterwarnings("ignore", category=UserWarning, module="slack_sdk")

# Initialize Slack app
app = App(token=Config.SLACK_BOT_TOKEN)

# Initialize OpenAI client
client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

# Initialize Redis manager
redis_manager = RedisManager()

# Initialize OpenAIService
openai_service = OpenAIService()

@app.event("message")
def command_handler(body, say):
    global message_histories, bot_user_id
    event = body['event']
    channel_id = body['event']['channel']
    channel_type = event.get('channel_type')
    user_id = event.get('user')
    
    if user_id == bot_user_id:
        return

    if channel_type in ('channel', 'im'):
        if channel_id not in message_histories:
            message_histories[channel_id] = [{"role": "system", "content": Config.SYSTEM_INITIAL_MESSAGE}]

        try:
            current_timestamp = get_madrid_timestamp()
        except Exception as e:
            current_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"Error getting timestamp: {str(e)}")

        # Manejar el texto del mensaje
        text = event.get('text', '')
        username = get_username_from_id(app.client, user_id)
        
        if text:
            formatted_text = f"{username} ({current_timestamp}): {text}"
            message_histories[channel_id].append({"role": "user", "content": formatted_text})
        
        # Manejar el audio si existe
        if 'files' in event and len(event['files']) > 0:
            for file in event['files']:
                if file.get('subtype') == 'slack_audio' or file['mimetype'].startswith('audio') or file['filetype'] in ['mp3', 'webm', 'mov']:
                    headers = {"Authorization": f"Bearer {Config.SLACK_BOT_TOKEN}"}
                    audio_file = download_and_convert_audio(file['url_private'], headers)
                    transcript = openai_service.transcribe_audio(audio_file)
                    
                    if transcript:
                        formatted_audio = f"{username} ({current_timestamp}): {transcript}"
                        message_histories[channel_id].append({"role": "user", "content": formatted_audio})

        # Determinar si el bot debe responder
        should_respond = False
        contribution = None
        
        # Respuesta directa si es mensaje privado o mención
        if channel_type == 'im' or (channel_type == 'channel' and f'<@{bot_user_id}>' in text):
            should_respond = True
            print("\n💬 Respuesta directa - Mensaje privado o mención")
        else:
            # Evaluar si debería intervenir proactivamente
            print(f"\n🤔 Evaluando mensaje: {formatted_text[:500]}...")
            evaluator = RelevanceEvaluator(openai_service, message_histories, channel_id)
            should_respond, contribution = evaluator.should_intervene(formatted_text)       

        if should_respond:
            try:
                # Inicializar herramientas y procesadores
                tools_manager = ToolsManager(app, openai_service, message_histories)
                tool_processor = ToolProcessor(tools_manager, openai_service, message_histories)
                response_handler = ResponseHandler(app, openai_service, message_histories)

                # Trim history si es necesario
                message_histories = trim_message_history(message_histories, channel_id, Config.MAX_CONTEXT_CHARS)

                 # Si vamos a intervenir, añadir el contexto como mensaje adicional
                if contribution:
                    context_message = f"[Contexto: He decidido intervenir porque {contribution}]"
                    message_histories[channel_id].append({"role": "assistant", "content": context_message})

                # Procesar herramientas
                message, use_audio_response = tool_processor.process_tools(channel_id, say)
                
                # Verificar GenerationComplete
                if message is None:
                    message_histories[channel_id].pop()
                    return

                # Procesar y enviar respuesta
                answer = response_handler.handle_response(
                    channel_id, 
                    use_audio_response, 
                    current_timestamp, 
                    say
                )
                
                # Actualizar historial
                botusername = get_username_from_id(app.client, bot_user_id)
                formatted_answer = f"{botusername} ({current_timestamp}): {answer}"
                message_histories[channel_id].append({"role": "assistant", "content": formatted_answer})

                # Guardar en Redis
                redis_manager.save_message_histories(message_histories)

            except Exception as e:
                print(f"Error: {e}")
                say("Lo siento, no puedo responder en este momento.")

def start():
    global bot_user_id, message_histories
    auth_response = app.client.auth_test(token=Config.SLACK_BOT_TOKEN)
    bot_user_id = auth_response['user_id']
    message_histories = redis_manager.load_message_histories()
    handler = SocketModeHandler(app, Config.SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    start()