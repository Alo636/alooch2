from chatbot.openai_client import procesar_respuesta_openai, detectar_intenciones
conversation_history = [
    {"role": "system", "content": "Este es el historial de la conversación."},
]
# Texto de ejemplo
text = "quiero eliminar mi reserva del lunes 2"
text = detectar_intenciones(text, conversation_history)
print(text)
texto = procesar_respuesta_openai(conversation_history, text[0])
# # intencion = json.dumps(texto)
# texto = str(texto[0])

# texto = texto.strip("{").strip("}")
print(texto)
