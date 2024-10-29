from typing import Tuple, Optional, Dict, Any
from ..base_tool import BaseTool
import requests
from bs4 import BeautifulSoup

class GetUrlTool(BaseTool):
    @property
    def function_config(self) -> Dict[str, Any]:
        return {
            "name": "get_url",
            "description": "Accede al contenido de una página web",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "La URL de la web",
                    },
                },
                "required": ["url"],
            },
        }

    def execute(self, arguments: dict, channel_id: str, say) -> Tuple[Optional[str], bool]:
        url = arguments.get("url", "")
        return self.get_url(url), False

    def get_url(self, url: str) -> str:
        """Fetch and summarize the content of a given URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, timeout=10, headers=headers)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Eliminar elementos no deseados
                for script in soup(["script", "style"]):
                    script.extract()
                    
                # Obtener texto y limpiarlo
                text = soup.get_text()
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
            else:
                print(f"Error fetching URL {url}: Status code {response.status_code}")
                return f"error Fetching the URL content failed (Status: {response.status_code})"
                
        except requests.Timeout:
            print(f"Timeout error fetching URL {url}")
            return "error Timeout fetching the URL content"
            
        except requests.RequestException as e:
            print(f"Request error fetching URL {url}: {str(e)}")
            return f"error Fetching the URL content failed: {str(e)}"
            
        except Exception as e:
            print(f"Unexpected error fetching URL {url}: {str(e)}")
            return "error Unexpected error fetching the URL content"