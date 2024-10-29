from typing import Tuple, Optional, Dict, Any
from ..base_tool import BaseTool
import giphy_client
from giphy_client.rest import ApiException
from config import Config

class SearchGifTool(BaseTool):
    def __init__(self, app, openai_service, message_histories):
        super().__init__(app, openai_service, message_histories)
        self.giphy_api_instance = giphy_client.DefaultApi()

    @property
    def function_config(self) -> Dict[str, Any]:
        return {
            "name": "search_gif",
            "description": "Busca un GIF a partir de una palabra clave",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "La palabra clave para buscar el GIF",
                    },
                },
                "required": ["keyword"],
            },
        }

    def execute(self, arguments: dict, channel_id: str, say) -> Tuple[Optional[str], bool]:
        keyword = arguments.get("keyword", "")
        gif_url = self.search_gif(keyword)
        
        if gif_url:
            say(f"Aquí tienes un GIF sobre {keyword}: {gif_url}")
        else:
            say(f"No pude encontrar un GIF sobre {keyword}.")
        
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
                    "content": f"GIF {'encontrado' if gif_url else 'no encontrado'} para: {keyword}"
                })
            
        return None, None

    def search_gif(self, keyword: str) -> Optional[str]:
        """
        Search for a GIF using GIPHY API
        """
        try:
            response = self.giphy_api_instance.gifs_search_get(
                api_key=Config.GIPHY_API_KEY,
                q=keyword,
                limit=1,
                rating='g'
            )
            if response.data:
                return response.data[0].images.fixed_height.url
            return None
        except ApiException as e:
            print(f"Error al buscar el GIF: {e}")
            return None
        except Exception as e:
            print(f"Error inesperado buscando GIF: {str(e)}")
            return None