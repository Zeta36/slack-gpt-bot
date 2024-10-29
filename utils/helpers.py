import re
from pydub import AudioSegment
import os
from config import Config
import requests
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

def get_madrid_timestamp():
    """
    Obtiene el timestamp actual en la zona horaria de Madrid de manera robusta
    """
    try:
        # Obtener el tiempo UTC actual
        utc_now = datetime.now(timezone.utc)
        
        # Convertir a timezone de Madrid
        madrid_tz = ZoneInfo("Europe/Madrid")
        madrid_time = utc_now.astimezone(madrid_tz)
        
        # Formatear la hora
        return madrid_time.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        try:
            # Fallback 1: Usar offset fijo
            utc_now = datetime.now(timezone.utc)
            # Determinar si estamos en horario de verano
            is_summer = utc_now.astimezone(ZoneInfo("Europe/Madrid")).dst() != timedelta(0)
            offset = 2 if is_summer else 1
            madrid_time = utc_now + timedelta(hours=offset)
            return madrid_time.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e2:
            # Fallback 2: Usar hora local + 2 horas
            print(f"Error getting Madrid timestamp with ZoneInfo: {str(e)}")
            print(f"Error in fallback 1: {str(e2)}")
            return (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S")

def trim_message_history(message_histories, channel_id, token_limit):
    """
    Trims the message history for a given channel if it exceeds the token limit.
    """
    while get_total_tokens(message_histories[channel_id]) > token_limit:
        if len(message_histories[channel_id]) > 1:
            message_histories[channel_id] = [message_histories[channel_id][0]]
        else:
            break
    return message_histories

def remove_weird_chars(text):
    return re.sub(r"[^a-zA-Z0-9\s.,ñ:áéíóú?+<@>!¡¿()&€@#_\-/*\"':;%=\\`~%\[\]{}^$@;:'\"+#.,°<>]", "", text)

def get_total_tokens(messages):
    total_tokens = 0
    for message in messages:
        if 'content' in message and message['content'] is not None and isinstance(message['content'], str) and message['content'].strip():
            total_tokens += len(message["content"].split())
    return total_tokens

def get_username_from_id(slack_client, user_id):
    response = slack_client.users_info(user=user_id)
    if response['ok']:
        user_profile = response['user']
        return user_profile.get('real_name', 'name')
    else:
        return None

def replace_user_ids_with_usernames(slack_client, text):
    user_ids = re.findall(r'<@([A-Z0-9]+)>', text)
    for user_id in user_ids:
        username = get_username_from_id(slack_client, user_id)
        if username:
            text = text.replace(f'<@{user_id}>', f'*{username}*')
    return text

def build_image_blocks(image_urls):
    blocks = []
    for url in image_urls:
        block = {
            "type": "image",
            "image_url": url,
            "alt_text": "Imagen generada"
        }
        blocks.append(block)
    return blocks

def download_and_convert_audio(url, headers):
    try:
        # Asegurar que el directorio existe
        os.makedirs(Config.AUDIO_DIR, exist_ok=True)
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Guardar primero como temporal
            with open(Config.TEMP_AUDIO_PATH, "wb") as f:
                f.write(response.content)
            
            try:
                # Convertir a MP3
                audio = AudioSegment.from_file(Config.TEMP_AUDIO_PATH)
                audio.export(Config.INPUT_AUDIO_PATH, format="mp3")  # Usamos INPUT en lugar de SYSTEM
                
                # Limpiar el archivo temporal
                os.remove(Config.TEMP_AUDIO_PATH)
                
                # Devolvemos la ruta del audio de entrada convertido
                return Config.INPUT_AUDIO_PATH
                
            except Exception as e:
                print(f"Error en la conversión de audio: {e}")
                if os.path.exists(Config.TEMP_AUDIO_PATH):
                    os.remove(Config.TEMP_AUDIO_PATH)
                return None
                
    except Exception as e:
        print(f"Error downloading or converting audio: {e}")
        if os.path.exists(Config.TEMP_AUDIO_PATH):
            os.remove(Config.TEMP_AUDIO_PATH)
        return None