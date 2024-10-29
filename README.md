# SamuChatGPT Lite

Un asistente de Slack avanzado potenciado por GPT que combina capacidades conversacionales con herramientas prácticas y funcionalidades proactivas. Diseñado para mejorar la productividad del equipo a través de la automatización inteligente y la asistencia contextual.

## 🌟 Características Principales

### Core Features
- **Integración Slack Avanzada**
  - Respuesta a mensajes directos y menciones
  - Procesamiento de hilos y conversaciones
  - Manejo de canales públicos y privados
  - Sistema de permisos y roles

- **Procesamiento de Audio**
  - Transcripción de mensajes de voz
  - Respuestas en audio con voz natural
  - Soporte para múltiples formatos (MP3, WAV, WebM)
  - Conversión automática de formatos

- **Sistema Proactivo**
  - Análisis de conversaciones en tiempo real
  - Detección de oportunidades de intervención
  - Evaluación de relevancia con puntuación
  - Intervenciones contextuales inteligentes

### 🛠️ Herramientas Integradas

1. **SearchWebTool**
   - Búsqueda web mediante Google Custom Search
   - Procesamiento y resumen de resultados
   - Extracción de información relevante
   - Citación de fuentes

2. **GenerateImageTool**
   - Generación de imágenes con DALL-E
   - Múltiples tamaños y estilos
   - Ajustes de calidad configurables
   - Procesamiento de prompts complejos

3. **SearchGifTool**
   - Integración con API de Giphy
   - Búsqueda contextual de GIFs
   - Filtros de contenido
   - Optimización de rendimiento

4. **QueryMagentoTool**
   - Consultas a base de datos Magento
   - Análisis de ventas y productos
   - Reportes en tiempo real
   - Seguridad y optimización de consultas

5. **CalculateTool**
   - Cálculos matemáticos avanzados
   - Soporte para expresiones complejas
   - Manejo de unidades y conversiones
   - Validación de entrada

6. **ReminderTool**
   - Sistema de recordatorios flexible
   - Programación temporal avanzada
   - Notificaciones personalizables
   - Persistencia de recordatorios

## 📋 Requisitos del Sistema

### Requisitos de Hardware
- CPU: 2 cores mínimo (4+ recomendado)
- RAM: 4GB mínimo (8GB+ recomendado)
- Almacenamiento: 1GB disponible
- Conexión a Internet estable

### Software Base
- Python 3.8 o superior
- Redis Server 5.0+
- FFmpeg para procesamiento de audio
- Certificados SSL para conexiones seguras

### Dependencias Python
```bash
# Core Dependencies
slack-bolt==1.18.0          # Framework Slack
openai==1.12.0             # API de OpenAI
redis==5.0.1               # Persistencia de datos

# Audio Processing
pydub==0.25.1              # Procesamiento de audio
ffmpeg-python==0.2.0       # Conversión de formatos

# Web & Network
requests==2.31.0           # Cliente HTTP
beautifulsoup4==4.12.3     # Web scraping
giphy-client==1.0.0        # Cliente Giphy

# Utils
python-dateutil==2.8.2     # Manejo de fechas
backoff==2.2.1            # Reintentos exponenciales
warnings2==0.4.1          # Gestión de warnings
zoneinfo                  # Zonas horarias
tzdata                    # Datos de zonas horarias

# Optional Development Dependencies
pytest==8.0.0             # Testing
black==24.2.0             # Formateo de código
pylint==3.0.3             # Análisis estático
```

## 🛠️ Instalación Detallada

### 1. Preparación del Sistema
```bash
# Instalar dependencias del sistema (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y python3.8 python3.8-venv python3.8-dev
sudo apt-get install -y redis-server ffmpeg

# Configurar Redis
sudo systemctl enable redis-server
sudo systemctl start redis-server
```

### 2. Configuración del Proyecto
```bash
# Clonar repositorio
git clone https://github.com/yourusername/SamuChatGPT_Lite.git
cd SamuChatGPT_Lite

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate

# Instalar dependencias
pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configuración de APIs y Servicios

#### Slack
1. Crear una nueva app en api.slack.com
2. Habilitar Socket Mode
3. Configurar permisos:
   - chat:write
   - files:read
   - files:write
   - im:history
   - im:read
   - im:write
   - channels:history
   - channels:read

#### OpenAI
1. Obtener API key en platform.openai.com
2. Habilitar acceso a modelos necesarios
3. Configurar límites de uso

#### Configuración del Archivo config.py
```python
class Config:
    # Slack Configuration
    SLACK_BOT_TOKEN = "xoxb-your-token"
    SLACK_APP_TOKEN = "xapp-your-token"
    
    # OpenAI Configuration
    OPENAI_API_KEY = "your-key"
    MODEL_NAME = "gpt-4-turbo-preview"
    MODEL_NAME_AUDIO = "gpt-4-voice"
    MODEL_VOICE = "shimmer"
    
    # Redis Configuration
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    
    # API Keys
    GIPHY_API_KEY = "your-key"
    GOOGLE_API_KEY = "your-key"
    GOOGLE_CSE_ID = "your-cse-id"

    # App Settings
    MAX_CONTEXT_CHARS = 12000
    MAX_RESPONSE_CHARS = 2000
    WEB_SUMMARY_MAX_CHARS = 5000
    
    # Media Settings
    MEDIA_DIR = "media"
    AUDIO_DIR = f"{MEDIA_DIR}/audio"
    SYSTEM_AUDIO_PATH = f"{AUDIO_DIR}/system_audio.mp3"
    TEMP_AUDIO_PATH = f"{AUDIO_DIR}/temp_audio.mp3"
    RESPONSE_AUDIO_PATH = f"{AUDIO_DIR}/response_audio.mp3"
```

## 🚀 Uso y Ejemplos

### Iniciar el Bot
```bash
# Modo normal
python samuchatgptlite.py

# Modo debug
DEBUG=1 python samuchatgptlite.py

# Modo producción
PRODUCTION=1 python samuchatgptlite.py
```

### Ejemplos de Uso por Herramienta

#### 1. SearchWebTool
```
# Búsqueda Simple
@bot busca información sobre Python

# Búsqueda Específica
@bot encuentra los últimos cambios en Python 3.11

# Búsqueda con Contexto
@bot busca ejemplos de async/await en Python
```

#### 2. GenerateImageTool
```
# Imagen Simple
@bot genera una imagen de un gato

# Imagen con Estilo
@bot genera una imagen estilo cyberpunk de un gato samurái

# Imagen con Especificaciones
@bot genera una imagen landscape de un atardecer en Tokio
```

#### 3. QueryMagentoTool
```
# Consultas de Ventas
@bot muestra las ventas de hoy
@bot cual fue el producto más vendido esta semana
@bot análisis de ventas por categoría

# Consultas de Inventario
@bot stock bajo en Nike
@bot productos sin stock
```

### Sistema Proactivo

El bot puede intervenir automáticamente en situaciones como:
- Corrección de información incorrecta
- Aporte de datos relevantes
- Respuesta a preguntas sin contestar
- Sugerencias contextuales

Ejemplo de intervención:
```
Usuario: Creo que las Jordan 1 salieron en 1982
Bot: [Intervención: Corrección histórica] Permíteme aclarar: Las Air Jordan 1 fueron lanzadas en 1985...
```

## 🏗️ Arquitectura del Sistema

### Estructura de Directorios
```
SamuChatGPT_Lite/
├── samuchatgptlite.py     # Entrada principal
├── config.py              # Configuración
├── requirements.txt       # Dependencias
├── media/                 # Archivos multimedia
│   └── audio/            # Archivos de audio
├── utils/                # Utilidades
│   ├── __init__.py
│   ├── helpers.py        # Funciones auxiliares
│   ├── openai_service.py # Servicio OpenAI
│   └── redis_manager.py  # Gestión de Redis
├── tools/                # Herramientas
│   ├── __init__.py
│   ├── base_tool.py     # Clase base
│   ├── tools_manager.py # Gestor de herramientas
│   └── tools/           # Implementaciones
└── tests/               # Tests unitarios
```

### Flujo de Datos
1. Recepción de mensaje en Slack
2. Procesamiento inicial (texto/audio)
3. Evaluación de intervención
4. Selección de herramientas
5. Ejecución de acciones
6. Generación de respuesta
7. Envío de respuesta
8. Persistencia en Redis

## 🔧 Troubleshooting

### Problemas Comunes

1. **Error de Conexión Redis**
```bash
# Verificar estado de Redis
sudo systemctl status redis-server

# Verificar conectividad
redis-cli ping
```

2. **Errores de Audio**
```bash
# Verificar FFmpeg
ffmpeg -version

# Verificar permisos
chmod 755 media/audio
```

3. **Errores de API**
```python
# Verificar rate limits
print(openai_service.get_rate_limits())
```

## 📝 Contribución

1. Fork del repositorio
2. Crear rama de feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

### Guía de Estilo
- Usar Black para formateo
- Documentar con docstrings
- Seguir PEP 8
- Añadir tests unitarios

## 📄 Licencia

MIT License

Copyright (c) 2024 Samuel G.P.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Autor

Samuel G.P.
