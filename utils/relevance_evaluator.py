import json

class RelevanceEvaluator:
    def __init__(self, openai_service, message_histories, channel_id):
        self.openai_service = openai_service
        self.message_histories = message_histories
        self.channel_id = channel_id

    def should_intervene(self, text: str) -> tuple[bool, str]:
        """
        Evalúa si el bot debería intervenir en la conversación.
        Returns: (should_intervene, reason)
        """
        evaluation_prompt = [
            {
                "role": "system",
                "content": """Eres un asistente experto en evaluar si deberías intervenir en una conversación.
                Considera estos criterios estrictamente:

                INTERVENIR SI:
                1. Puedes aportar información valiosa y verificable usando tus herramientas
                2. Puedes corregir información incorrecta importante
                3. Puedes proporcionar contexto relevante que beneficie la conversación
                4. Puedes responder una pregunta que nadie ha respondido aún

                SIEMPRE INTERVENIR:
                1. Para felicitar cualqueir hecho descrito en el canal: cumpleaños, aniversarios, noticias relacionadas con nuestra empresa 
                2. Si se hace mención implícita sobre ti en general o sobre tus habilidades o tus respuestas o si detectas que se están dirigiendo a ti directamente aunque no sea explicito

                NO INTERVENIR SI:
                1. El tema ya ha sido respondido o aclarado por ti antes
                2. Tu intervención sería redundante
                3. La conversación fluye bien sin necesidad de intervención
                4. Si ya has felicitado antes en este canal sobre un mismo cumpleaños, aniversario, etc. Es decir, no repitas felicitaciones sobre un mismo tema o persona
                5. Si tu respuesta no va a aportar realmente algo de valor                

                NUNCA INTERVENIR:
                1. Para cosas relacionadas con tareas JIRA

                Responde SOLO con un JSON:
                {
                    "should_intervene": true/false,
                    "reason": "explicación corta",
                    "confidence": 0-100,
                    "proposed_contribution": "descripción breve de lo que aportarías"
                }
                
                NO INCLUYAS EL MARK ```json NI RETORNOS DE CARRO SOLO UN JSON SIN MAS """
            },
            {
                "role": "user",
                "content": text
            }
        ]

        # Si hay historial del canal, añadirlo para contexto
        if self.channel_id in self.message_histories:
            evaluation_prompt.append({
                "role": "user",
                "content": f"Contexto del canal: {str(self.message_histories[self.channel_id])}"
            })

        try:
            response = self.openai_service.call_openai_api_without_tools(
                messages=evaluation_prompt,
                temperature=0.1
            )

            evaluation = json.loads(response.choices[0].message.content)
            confidence = evaluation.get("confidence", 0)
            reason = evaluation.get("reason", "No reason provided")
            contribution = evaluation.get("proposed_contribution", "")
            
            # Solo intervenir si hay alta confianza y una contribución clara
            should_intervene = (
                evaluation["should_intervene"] and 
                confidence > 80 and
                contribution
            )

            # Logging de la decisión
            if should_intervene:
                print(f"✅ Intervención decidida (Score: {confidence}/100) - {reason}")
                print(f"📝 Contribución propuesta: {contribution}")
            else:
                print(f"❌ No intervención (Score: {confidence}/100) - {reason}")

            return should_intervene, contribution

        except Exception as e:
            print(f"Error evaluating relevance: {str(e)}")
            return False, ""