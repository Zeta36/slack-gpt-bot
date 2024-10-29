import os
import re
from config import Config
from .helpers import replace_user_ids_with_usernames

class ResponseHandler:
    def __init__(self, app, openai_service, message_histories):
        self.app = app
        self.openai_service = openai_service
        self.message_histories = message_histories

    def handle_response(self, channel_id, use_audio_response, current_timestamp, say):
        """
        Maneja la generación y envío de respuestas.
        Retorna la respuesta procesada.
        """
        try:
            # Generar respuesta según tipo
            if use_audio_response:
                response = self.openai_service.call_openai_api_with_audio(
                    messages=self.message_histories[channel_id]
                )
            else:
                response = self.openai_service.call_openai_api_without_tools(
                    messages=self.message_histories[channel_id]
                )

            message = response.choices[0].message
            answer = self._get_answer_from_message(message)
            
            if answer is None:
                return "Lo siento, no pude generar una respuesta."
                
            # Formatear respuesta
            answer = self._format_answer(answer, current_timestamp)
            
            # Enviar respuesta de texto si corresponde
            if answer and not use_audio_response:
                say(answer)

            # Enviar respuesta de audio si está disponible
            if os.path.exists(Config.RESPONSE_AUDIO_PATH) and hasattr(message, 'audio') and hasattr(message.audio, 'transcript'):
                self._send_audio_response(channel_id)
                
            return answer

        except Exception as e:
            print(f"Error in response handling: {str(e)}")
            raise

    def _get_answer_from_message(self, message):
        """Extrae la respuesta del mensaje, ya sea de content o transcript"""
        if hasattr(message, 'content') and message.content:
            return message.content
        elif hasattr(message, 'audio') and hasattr(message.audio, 'transcript'):
            return message.audio.transcript
        return None

    def _format_answer(self, answer, current_timestamp):
        """Formatea la respuesta aplicando todas las transformaciones necesarias"""
        answer = answer.replace("(current_timestamp):", "")
        answer = answer.replace("(current_timestamp)", str(current_timestamp))
        answer = re.sub(r'^\w+\s\(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\): ', '', answer)
        answer = replace_user_ids_with_usernames(self.app.client, answer)
        return answer

    def _send_audio_response(self, channel_id):
        """Envía el archivo de audio de respuesta"""
        try:
            self.app.client.files_upload_v2(
                channels=channel_id,
                file=Config.RESPONSE_AUDIO_PATH,
                title="Respuesta en audio"
            )
        except Exception as e:
            print(f"Error sending audio response: {str(e)}")
            # No raise aquí - queremos continuar incluso si falla el envío de audio