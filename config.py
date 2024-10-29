class Config:
    # Redis Configuration
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0

    # OpenAI Configuration
    OPENAI_API_KEY = "xxxx"
    MODEL_NAME = "gpt-4o-mini"
    MODEL_NAME_AUDIO = "gpt-4o-audio-preview"
    MODEL_VOICE = "fable"

    # Audio files paths
    MEDIA_DIR = "media"
    AUDIO_DIR = f"{MEDIA_DIR}/audio"
    SYSTEM_AUDIO_PATH = f"{AUDIO_DIR}/system_audio.mp3"
    RESPONSE_AUDIO_PATH = f"{AUDIO_DIR}/response_audio.mp3"
    TEMP_AUDIO_PATH = f"{AUDIO_DIR}/temp_audio.mp3"
    INPUT_AUDIO_PATH = f"{AUDIO_DIR}/input_audio.mp3"

    # Slack Configuration
    SLACK_APP_TOKEN = 'xapp-xxxx'
    SLACK_BOT_TOKEN = 'xoxb-xxxx'

    # Giphy Configuration
    GIPHY_API_KEY = "xxxx"

    # Google Search Configuration
    GOOGLE_API_KEY = "xxxx"
    GOOGLE_CSE_ID = "xxxx"

    # System Limits and Parameters
    WEB_SUMMARY_MAX_CHARS = 10000
    MAX_CONTEXT_CHARS = 5000
    MAX_RESPONSE_CHARS = 50000

    # System Messages
    SYSTEM_INITIAL_MESSAGE = """Eres un asistente de voz. Responde siempre con voz en español, 
    con un acento andaluz muy cerrado como de un pueblo de Cádiz, usando algunas expresiones coloquiales 
    andaluzas y hablando con arte. Se breve en tus respuestas dadas las circunstancias. La hora actual para ti como asistente será la última 
    hora registrada en el (current_timestamp) del último mensaje del historial de mensajes. 
    Utiliza esa información para saber a qué día y hora estamos. NUNCA menciones en tu respuesta tu nombre: SamuChatGPT.
    ¡Tampoco menciones el nombre del usuario al que le hablas! """

    USER_HELPER_MESSAGE = "Responde hablando muy ligero, todo lo rápido que puedas. NUNCA menciones en tu respuesta tu nombre: SamuChatGPT. ¡Tampoco menciones el nombre del usuario al que le hablas!"
