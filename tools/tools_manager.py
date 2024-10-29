from typing import List, Dict, Any, Tuple, Optional
from .tools import (
    SearchWebTool,
    GenerateImageTool,
    SearchGifTool,
    GetUrlTool,
    CalculateTool,
    QueryMagentoTool,
    ReminderTool
)

class ToolsManager:
    def __init__(self, app, openai_service, message_histories):
        self.tools = {
            "search_web": SearchWebTool(app, openai_service, message_histories),
            "generate_image": GenerateImageTool(app, openai_service, message_histories),
            "search_gif": SearchGifTool(app, openai_service, message_histories),
            "get_url": GetUrlTool(app, openai_service, message_histories),
            "calculate": CalculateTool(app, openai_service, message_histories),
            "query_magento": QueryMagentoTool(app, openai_service, message_histories),
            "set_reminder": ReminderTool(app, openai_service, message_histories),
        }

    @property
    def available_functions(self) -> List[Dict[str, Any]]:
        """Returns the list of available function configurations"""
        return [tool.function_config for tool in self.tools.values()]

    def execute(self, function_name: str, arguments: dict, channel_id: str, say) -> Tuple[Optional[str], bool]:
        """Execute the specified tool"""
        if function_name not in self.tools:
            raise ValueError(f"Unknown tool: {function_name}")
            
        return self.tools[function_name].execute(arguments, channel_id, say)