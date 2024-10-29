import re

def clean_sql_query(query: str) -> str:
    """Limpia la consulta SQL de comentarios y formato markdown"""
    # Eliminar comentarios de una línea
    query = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
    
    # Eliminar comentarios multilínea
    query = re.sub(r'/\*.*?\*/', '', query, flags=re.DOTALL)
    
    # Eliminar bloques de código markdown
    query = re.sub(r'```sql\s*', '', query)
    query = re.sub(r'```\s*', '', query)
    
    # Eliminar espacios en blanco extra y líneas vacías
    lines = [line.strip() for line in query.split('\n')]
    lines = [line for line in lines if line and not line.startswith('--')]
    
    return ' '.join(lines)