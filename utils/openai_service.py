# openai_service.py

import openai
import base64
import io
from pydub import AudioSegment
from config import Config

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    def transcribe_audio(self, audio_file):
        """Transcribe audio using Whisper API"""
        try:
            with open(audio_file, "rb") as audio:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio,
                    response_format="text"
                )
            return transcript
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None
    
    def call_openai_api_with_audio(self, **kwargs):
        """Call OpenAI API with audio support"""

        # Add system message for audio responses if not present    
        if kwargs["messages"][0]["role"] == "system":
            kwargs["messages"][0]["content"] = Config.SYSTEM_INITIAL_MESSAGE
        
        try:
            # Intentar leer el archivo como MP4 primero
            audio = AudioSegment.from_file(Config.SYSTEM_AUDIO_PATH)
            
            # Si el formato real es MP4, convertir a MP3
            if audio.channels and audio.frame_rate:  # Verificación básica de que es un archivo de audio válido
                mp3_data = io.BytesIO()
                audio.export(mp3_data, format="mp3")
                audio_bytes = mp3_data.getvalue()
            else:
                raise Exception("Invalid audio format")
                
        except Exception as e:
            # Si ya es un MP3 válido, leerlo directamente
            try:
                with open(Config.SYSTEM_AUDIO_PATH, "rb") as f:
                    audio_bytes = f.read()
            except Exception as e:
                raise Exception(f"Error processing audio file: {str(e)}")

        # Codificar el MP3 en base64
        encoded_string = base64.b64encode(audio_bytes).decode('utf-8')

        # Add voice instruction message with system audio
        voice_instruction = {
            "role": "user",
            "content": [                        
                { 
                    "type": "text",
                    "text": Config.USER_HELPER_MESSAGE
                },
                {
                    "type": "input_audio",
                    "input_audio": {
                        "data": encoded_string,
                        "format": "mp3"
                    }
                }
            ]
        }
        
        # Crear una copia temporal de los mensajes para añadir la instrucción de voz
        temp_messages = kwargs["messages"].copy()
        temp_messages.append(voice_instruction)

        # Generate audio response
        completion = self.client.chat.completions.create(
            model=Config.MODEL_NAME_AUDIO,
            modalities=["text", "audio"],
            audio={"voice": Config.MODEL_VOICE, "format": "mp3"},
            messages=temp_messages
        )
        
        # Save audio if available
        if hasattr(completion.choices[0].message, 'audio') and completion.choices[0].message.audio and hasattr(completion.choices[0].message.audio, 'data'):
            audio_data = completion.choices[0].message.audio.data
            if audio_data:
                wav_bytes = base64.b64decode(audio_data)
                with open(Config.RESPONSE_AUDIO_PATH, "wb") as f:
                    f.write(wav_bytes)

        return completion

    def call_openai_api_with_tools(self, **kwargs):
        """Call OpenAI API with tools support"""

        api_params = {
            "model": Config.MODEL_NAME,
            "messages": kwargs["messages"]
        }

        # Add tools if present
        if "tools" in kwargs:
            api_params["tools"] = kwargs["tools"]
        if "tool_choice" in kwargs:
            api_params["tool_choice"] = kwargs["tool_choice"]

        return self.client.chat.completions.create(**api_params)
    
    def call_openai_api_without_tools(self, **kwargs):
        """Call OpenAI API with tools support"""

        api_params = {
            "model": Config.MODEL_NAME,
            "messages": kwargs["messages"]
        }

        return self.client.chat.completions.create(**api_params)

