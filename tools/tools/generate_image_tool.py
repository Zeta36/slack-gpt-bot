from typing import Tuple, Optional, Dict, Any
from ..base_tool import BaseTool
import openai
from config import Config

class GenerateImageTool(BaseTool):
    def __init__(self, app, openai_service, message_histories):
        super().__init__(app, openai_service, message_histories)
        self.client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)

    @property
    def function_config(self) -> Dict[str, Any]:
        return {
            "name": "generate_image",
            "description": "Crea o genera imagenes o ilustraciones a partir de un prompt o petición dadas",
            "parameters": {
                "type": "object",
                "properties": {
                    "n": {
                        "type": "integer",
                        "description": "Número de imágenes (1 para DALL-E 3)"
                    },
                    "size": {
                        "type": "string",
                        "description": "Tamaño de las imágenes: '1024x1024' (cuadrado), '1792x1024' (paisaje), o '1024x1792' (retrato)",
                        "enum": ["1024x1024", "1792x1024", "1024x1792"]
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Prompt para generar imágenes"
                    }
                },
                "required": ["prompt"]
            }
        }

    def execute(self, arguments: dict, channel_id: str, say) -> Tuple[Optional[str], bool]:
        result = self.generate_image(
            channel_id,
            arguments.get("n", 1),
            arguments.get("size", "1024x1024"),
            arguments.get("prompt", "")
        )
        
        # En lugar de pop(), añadimos una respuesta de la herramienta
        if self.message_histories and channel_id in self.message_histories:
            # Obtenemos el último mensaje que debe ser el del asistente con tool_calls
            last_message = self.message_histories[channel_id][-1]
            if "tool_calls" in last_message:
                tool_call_id = last_message["tool_calls"][0]["id"]
                # Añadimos la respuesta de la herramienta
                self.message_histories[channel_id].append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": f"Imágenes generadas y enviadas al canal: {arguments.get('prompt')}"
                })

        return None, None

    def generate_image(self, channel_id: str, n: int = 1, size: str = "1024x1024", prompt: str = "") -> bool:
        """
        Generate images using OpenAI's DALL-E 3
        Returns: True if successful, False otherwise
        """
        try:
            # Validar y ajustar el tamaño si es necesario
            valid_sizes = ["1024x1024", "1792x1024", "1024x1792"]
            if size not in valid_sizes:
                size = "1024x1024"  # tamaño por defecto si no es válido
                
            # Nueva sintaxis para la API v1.0.0+
            image_response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=n,
                size=size,
                quality="standard"
            )

            # Extraer las URLs de las imágenes
            image_urls = [item.url for item in image_response.data]
            
            # Construir los bloques para Slack
            image_blocks = self._build_image_blocks(image_urls)

            # Enviar las imágenes al canal
            self.app.client.chat_postMessage(
                channel=channel_id,
                text=f"Aquí tienes {n} imagen(es) generada(s) en tamaño {size}",
                blocks=image_blocks
            )
            
            return True

        except Exception as e:
            print(f"Error generating image: {e}")
            self.app.client.chat_postMessage(
                channel=channel_id,
                text=f"Lo siento, hubo un error generando la imagen: {str(e)}"
            )
            return False

    def _build_image_blocks(self, image_urls: list) -> list:
        """Construye los bloques de Slack para mostrar imágenes"""
        blocks = []
        for url in image_urls:
            blocks.extend([
                {
                    "type": "image",
                    "image_url": url,
                    "alt_text": "Generated image"
                },
                {
                    "type": "divider"
                }
            ])
        return blocks