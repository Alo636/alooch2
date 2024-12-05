from chatbot.openai_client import procesar_respuesta_openai

texto = "quiero reservar para el 7 de diciembre"
conversation_history = [
    {"role": "system", "content": "Este es el historial de la conversación."},
]
print(procesar_respuesta_openai(texto, conversation_history))
