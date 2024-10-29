from typing import Tuple, Optional

class BaseTool:
    def __init__(self, app=None, openai_service=None, message_histories=None):
        self.app = app
        self.openai_service = openai_service
        self.message_histories = message_histories

    def execute(self, arguments: dict, channel_id: str, say) -> Tuple[Optional[str], bool]:
        raise NotImplementedError("Each tool must implement execute method")

    @property
    def function_config(self) -> dict:
        raise NotImplementedError("Each tool must provide function_config")