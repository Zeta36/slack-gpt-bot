import pymysql
from typing import List, Dict, Any

class MagentoDBConnection:
    def __init__(self):
        self.db_config = {
            'host': '127.0.0.1',
            'port': 3308,
            'user': 'footdistrict_m2_read_only_user',
            'password': 'DdvqLJUf4meSm45Uef1zN7aHKxOKAZOT',
            'database': 'footdistrict_m2_db',
            'cursorclass': pymysql.cursors.DictCursor
        }

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """Ejecuta una consulta SQL usando el túnel SSH existente"""
        try:
            with pymysql.connect(**self.db_config) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    return results
        except Exception as e:
            print(f"Error en la conexión o consulta: {str(e)}")
            raise Exception(f"Error executing query: {str(e)}")