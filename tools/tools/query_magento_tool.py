from typing import Tuple, Optional, Dict, Any, List
from ..base_tool import BaseTool
from ..utils.magento_db import MagentoDBConnection
from ..utils.sql_cleaner import clean_sql_query

class QueryMagentoTool(BaseTool):
    def __init__(self, app, openai_service, message_histories):
        super().__init__(app, openai_service, message_histories)
        self.magento_db = MagentoDBConnection()

    @property
    def function_config(self) -> Dict[str, Any]:
        return {
            "name": "query_magento",
            "description": "Consulta la base de datos de Magento de nuestra web (la web de la empresa Footdistrict) para obtener información sobre productos, pedidos, clientes, etc. Una pregunta única e independiente por cada llamada a esta tool.",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "La pregunta sobre nuestra web (la web de Footdistrict) que requiere consultar la base de datos de Magento. Una pregunta única e independiente por cada llamada a esta tool."
                    }
                },
                "required": ["question"]
            }
        }

    def execute(self, arguments: dict, channel_id: str, say) -> Tuple[Optional[str], bool]:
        question = arguments.get("question", "")
        return self._query_magento(question)

    def _query_magento(self, question: str) -> Tuple[str, bool]:
        """
        Genera y ejecuta una consulta SQL basada en la pregunta del usuario
        Returns: (response_text, use_audio)
        """
        message_history = [
            {
                "role": "system",
                "content": """Eres un experto en SQL y en la base de datos de Magento 2.4.
                Tu objetivo es generar consultas SQL altamente eficientes.
                NO INCLUYAS COMENTARIOS EN LAS CONSULTAS.
                
                REGLAS DE OPTIMIZACIÓN CRÍTICAS:
                1. SIEMPRE usa LIMIT en consultas que devuelven múltiples filas
                2. Minimiza el número de JOINs al mínimo necesario
                3. Usa índices efectivamente (entity_id, created_at, attribute_id)
                4. En consultas de ventas, filtra primero sales_order por fecha
                5. Para fechas usa CURDATE() o DATE_SUB(CURDATE(), INTERVAL N DAY)
                
                EJEMPLO DE CONSULTA MÚLTIPLE CORRECTA:
                SELECT COUNT(*) as today_count 
                FROM customer_entity 
                WHERE DATE(created_at) = CURDATE();
                
                SELECT COUNT(*) as yesterday_count 
                FROM customer_entity 
                WHERE DATE(created_at) = DATE_SUB(CURDATE(), INTERVAL 1 DAY);
                
                TABLAS PRINCIPALES:
                - customer_entity: Clientes (created_at, email)
                - sales_order: Pedidos (created_at, customer_id)
                - catalog_product_entity: Productos (entity_id, sku)
                - catalog_product_entity_varchar: Atributos de texto
                - eav_attribute: Definición de atributos
                    * attribute_id: ID del atributo (indexado)
                    * attribute_code: Código del atributo
                    * entity_type_id: Tipo de entidad (4 para productos)
                    
                RESPONDE ÚNICAMENTE CON LAS CONSULTAS SQL, SIN COMENTARIOS."""
            },
            {
                "role": "user",
                "content": question
            }
        ]

        try:
            # Generamos la consulta SQL
            response = self.openai_service.call_openai_api_without_tools(
                messages=message_history,
                temperature=0
            )
            
            sql_query = clean_sql_query(response.choices[0].message.content)
            print(f"SQL Query generated: {sql_query}")
            
            # Ejecutamos la consulta
            all_results = []
            
            # Si hay múltiples consultas, ejecutarlas en orden
            queries = [q.strip() for q in sql_query.split(';') if q.strip()]
            
            for query in queries:
                results = self.magento_db.execute_query(query)
                if results:
                    all_results.append(results)
            
            if not all_results:
                return "No se encontraron resultados para tu consulta.", False
            
            # Generar resumen de resultados
            summary_prompt = f"""
            Como experto en Magento 2.4, analiza estos resultados de múltiples consultas:
            
            Consultas ejecutadas:
            {sql_query}
            
            Resultados:
            {all_results}
            
            Por favor, genera un resumen que:
            1. Compare los diferentes resultados obtenidos
            2. Destaque patrones y tendencias
            3. Incluya porcentajes de cambio cuando sea relevante
            4. Use terminología específica de e-commerce
            """
            
            summary_response = self.openai_service.call_openai_api_without_tools(
                messages=[
                    {"role": "system", "content": "Eres un experto en e-commerce y Magento. Proporciona análisis comparativos claros."},
                    {"role": "user", "content": summary_prompt}
                ]
            )
            
            return summary_response.choices[0].message.content, False
            
        except Exception as e:
            print(f"Error in query_magento: {str(e)}")
            return f"Lo siento, hubo un error al consultar la base de datos: {str(e)}", False

    def _clean_results(self, results: List[Dict]) -> List[Dict]:
        """Limpia y formatea los resultados para presentación"""
        if not results:
            return []
            
        cleaned_results = []
        for row in results:
            cleaned_row = {}
            for key, value in row.items():
                # Convertir bytes a string si es necesario
                if isinstance(value, bytes):
                    try:
                        value = value.decode('utf-8')
                    except:
                        value = str(value)
                        
                # Formatear fechas si es necesario
                if 'datetime.datetime' in str(type(value)):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                    
                cleaned_row[key] = value
                
            cleaned_results.append(cleaned_row)
            
        return cleaned_results