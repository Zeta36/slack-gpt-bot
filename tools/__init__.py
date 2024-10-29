"""
Tools package para el bot de Slack de Footdistrict
Proporciona todas las herramientas y utilidades necesarias para el funcionamiento del bot
"""

from .tools_manager import ToolsManager
from .base_tool import BaseTool
from .utils import MagentoDBConnection, clean_sql_query
from .tools import (
    SearchWebTool,
    GenerateImageTool,
    SearchGifTool,
    GetUrlTool,
    CalculateTool,
    QueryMagentoTool,
    ReminderTool
)

# Versión del paquete
__version__ = '1.0.0'

# Exportar las clases y funciones principales
__all__ = [
    # Clases principales
    'ToolsManager',
    'BaseTool',
    
    # Herramientas individuales
    'SearchWebTool',
    'GenerateImageTool',
    'SearchGifTool',
    'GetUrlTool',
    'CalculateTool',
    'QueryMagentoTool',
    'ReminderTool',
    
    # Utilidades
    'MagentoDBConnection',
    'clean_sql_query'
]

# Información adicional del paquete
__author__ = 'Footdistrict Development Team'
__description__ = 'Herramientas para el bot de Slack de Footdistrict'