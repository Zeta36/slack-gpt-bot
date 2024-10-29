import threading
import time
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
from ..base_tool import BaseTool

class ReminderManager:
    """Maneja la lista de recordatorios y el hilo de verificación de tiempos."""
    
    def __init__(self, app):
        self.reminders = []  # Lista para almacenar los recordatorios
        self.app = app
        self.running = True

        # Iniciar el hilo de verificación en segundo plano
        threading.Thread(target=self._reminder_loop, daemon=True).start()

    def add_reminder(self, reminder_text: str, reminder_time: str, channel_id: str) -> str:
        """Agrega un recordatorio a la lista."""
        try:
            # Convertir reminder_time en un objeto datetime
            reminder_dt = datetime.strptime(reminder_time, "%H:%M").replace(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day
            )
            # Si el tiempo ya ha pasado hoy, ajustarlo para el día siguiente
            if reminder_dt < datetime.now():
                reminder_dt += timedelta(days=1)
                
            # Agregar recordatorio a la lista
            self.reminders.append({"time": reminder_dt, "text": reminder_text, "channel": channel_id})
            return f"Recordatorio establecido para las {reminder_time}."
        except ValueError:
            return "Formato de hora no válido. Usa HH:MM."

    def _reminder_loop(self):
        """Hilo que verifica continuamente los recordatorios."""
        while self.running:
            current_time = datetime.now()
            for reminder in self.reminders[:]:  # Crear una copia para modificar la lista mientras se itera
                if current_time >= reminder["time"]:
                    # Enviar el recordatorio y eliminarlo de la lista
                    self.app.client.chat_postMessage(channel=reminder["channel"], text=f"Recordatorio: {reminder['text']}")
                    self.reminders.remove(reminder)
            time.sleep(60)  # Esperar un minuto antes de la próxima verificación

class ReminderTool(BaseTool):
    """Herramienta para establecer recordatorios únicos."""
    
    def __init__(self, app, openai_service, message_histories):
        super().__init__(app, openai_service, message_histories)
        self.reminder_manager = ReminderManager(app)  # Usar app para manejar mensajes

    @property
    def function_config(self) -> dict:
        return {
            "name": "set_reminder",
            "description": "Establece un recordatorio único para una fecha y hora específicas",
            "parameters": {
                "type": "object",
                "properties": {
                    "reminder_text": {
                        "type": "string",
                        "description": "Texto del recordatorio",
                    },
                    "reminder_time": {
                        "type": "string",
                        "description": "Hora en formato HH:MM para el recordatorio",
                    },
                },
                "required": ["reminder_text", "reminder_time"],
            },
        }

    def execute(self, arguments: dict, channel_id: str, say) -> Tuple[Optional[str], bool]:
        """Establece un recordatorio utilizando ReminderManager."""
        reminder_text = arguments.get("reminder_text")
        reminder_time = arguments.get("reminder_time")
        response = self.reminder_manager.add_reminder(reminder_text, reminder_time, channel_id)
        return response, False
