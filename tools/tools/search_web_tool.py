from typing import Tuple, Optional, Dict, Any
from ..base_tool import BaseTool
import requests
from bs4 import BeautifulSoup
import json
from config import Config

class SearchWebTool(BaseTool):
    @property
    def function_config(self) -> Dict[str, Any]:
        return {
            "name": "search_web",
            "description": "Busca información en la web para una consulta dada, pero solo si no estás seguro de la respuesta o si es muy evidente que te piden explícitamente que busques la información en internet",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "La consulta que quieres buscar en la web",
                    },
                },
                "required": ["query"],
            },
        }

    def execute(self, arguments: dict, channel_id: str, say) -> Tuple[Optional[str], bool]:
        query = arguments.get("query", "")
        return self.search_web(query), False

    def search_web(self, query: str) -> str:
        """Search the web for a given query using Google Search API"""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'q': query,
            'key': Config.GOOGLE_API_KEY,
            'cx': Config.GOOGLE_CSE_ID,
        }

        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                search_results = response.json()
                processed_results = []
                for result in search_results["items"][:2]:
                    try:
                        page_response = requests.get(result["link"], timeout=10)
                        if page_response.status_code == 200:
                            soup = BeautifulSoup(page_response.content, "html.parser")
                            for script in soup(["script", "style"]):
                                script.extract()
                            text = soup.get_text()
                            text = self._web_summary(text, query, result["link"])
                            processed_results.append({
                                "title": result["title"],
                                "link": result["link"],
                                "content": text,
                            })
                    except Exception as e:
                        print(f"Error processing search result: {str(e)}")
                        continue
                return json.dumps({"results": processed_results})
            else:
                print(f"Google API error: {response.status_code}")
                return json.dumps({"error": "La búsqueda en la web falló"})
        except Exception as e:
            print(f"Search web error: {str(e)}")
            return json.dumps({"error": "La búsqueda en la web falló"})

    def _web_summary(self, text: str, query: str, url: str) -> str:
        """Generate a summary of web content"""
        message_history = [
            {
                "role": "system", 
                "content": "Eres un asistente especialista en resumir y hacer esquemas del contenido de un texto siempre atendiendo a lo interesante de acuerdo a la query que se especifique. Como máximo el resumen debe tener 5000 caracteres. Abarca toda la informacion que puedas sacar del mismo para el uso de este resumen en el futuro. Añade siempre la url de referencia para cada información."
            },
            {
                "role": "user", 
                "content": f"Por favor, resume el contenido de esta web {url} de acuerdo a la información directamente relacionada con la query: {query}. Añade siempre la url de referencia. El Contenido de la web: {text}"
            }
        ]

        try:
            response = self.openai_service.call_openai_api_with_tools(
                model=Config.MODEL_NAME,
                messages=message_history
            )

            summary = response.choices[0].message.content
            summary = ' '.join(summary.split()[:Config.WEB_SUMMARY_MAX_CHARS])
            return summary
        except Exception as e:
            print(f"Summary generation error: {str(e)}")
            return "Error generando el resumen del contenido."