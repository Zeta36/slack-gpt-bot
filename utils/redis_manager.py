import redis
import json
from config import Config

class RedisManager:
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_client = redis.Redis(
            host=Config.REDIS_HOST,
            port=Config.REDIS_PORT,
            db=Config.REDIS_DB
        )

    def save_message_histories(self, message_histories):
        """Save message histories to Redis"""
        try:
            message_histories_str = {
                channel_id: json.dumps(history)
                for channel_id, history in message_histories.items()
            }
            self.redis_client.hset("message_histories", mapping=message_histories_str)
            return True
        except Exception as e:
            print(f"Error saving message histories: {e}")
            return False

    def load_message_histories(self):
        """Load message histories from Redis"""
        try:
            loaded_histories = self.redis_client.hgetall("message_histories")
            if loaded_histories:
                return {
                    channel_id.decode('utf-8'): json.loads(history)
                    for channel_id, history in loaded_histories.items()
                }
            return {}
        except Exception as e:
            print(f"Error loading message histories: {e}")
            return {}

    def clear_channel_context(self, channel_id):
        """Clear the context for a specific channel"""
        try:
            self.redis_client.hdel("message_histories", channel_id)
            return f"Contexto del chat con ID {channel_id} eliminado correctamente."
        except Exception as e:
            return f"Error al eliminar el contexto del chat: {e}"