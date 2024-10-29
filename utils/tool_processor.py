import json
from config import Config

class ToolProcessor:
    def __init__(self, tools_manager, openai_service, message_histories):
        self.tools_manager = tools_manager
        self.openai_service = openai_service
        self.message_histories = message_histories

    def process_tools(self, channel_id, say) -> tuple[object, bool]:
        """
        Procesa las llamadas a herramientas y sus respuestas.
        Returns: (message, use_audio_response)
        Si se encuentra GenerationComplete, retorna (None, True)
        """
        use_audio_response = True
        functions = self.tools_manager.available_functions

        try:
            # Primera llamada a la API
            tool_response = self.openai_service.call_openai_api_with_tools(
                messages=self.message_histories[channel_id],
                tools=[{"type": "function", "function": func} for func in functions],
                tool_choice="auto"
            )

            message = tool_response.choices[0].message
            tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else None

            # Procesar llamadas a herramientas si existen
            while tool_calls:
                tool_responses = []
                
                # Procesar cada llamada
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)

                    print(f"Executing function: {function_name}")

                    function_response, audio_response = self.tools_manager.execute(
                        function_name, 
                        arguments, 
                        channel_id, 
                        say
                    )

                    # Verificar GenerationComplete
                    if function_response is None:
                        return None, True

                    # Actualizar flag de audio si la función lo indica
                    if audio_response is False:
                        use_audio_response = False

                    # Almacenar respuesta si existe
                    if function_response:
                        function_response = function_response[:Config.MAX_RESPONSE_CHARS]
                        tool_responses.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": function_response
                        })

                # Añadir mensaje del asistente con los tool_calls
                self.message_histories[channel_id].append({
                    "role": "assistant",
                    "content": message.content if message.content else None,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        } for tool_call in tool_calls
                    ]
                })

                # Añadir respuestas de las herramientas
                for tool_response in tool_responses:
                    self.message_histories[channel_id].append(tool_response)

                # Obtener siguiente respuesta
                tool_response = self.openai_service.call_openai_api_with_tools(
                    messages=self.message_histories[channel_id],
                    tools=[{"type": "function", "function": func} for func in functions],
                    tool_choice="auto"
                )
                
                message = tool_response.choices[0].message
                tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else None

            return message, use_audio_response

        except Exception as e:
            print(f"Error in tool processing: {str(e)}")
            raise