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

# print(str(texto[0].get('intencion')) + " " + str(texto[0].get('detalle')))

# instrucciones = f"""
#     Primero que todo, hoy es {str(hoy.strftime('%d-%m-%Y'))} ({str(hoy.strftime('%A'))}).
#     Quiero que decidas cual es la función más adecuada según la intención del mensaje.
#     Quiero que tomes los argumentos valorando los detalles. Sigue estos apuntes fielmente:
#     IMPORTANTE: No modifiques el texto. Ejemplo: Si pone "hola", como argumento "mensaje" será "hola".
#     IMPORTANTE: Ten en cuenta qué día es hoy. Todas las fechas serán posteriores a hoy.
#     1. Analízalo el tiempo que necesites y luego toma una decisión.
#     2. Recuerda que los meses equivalen a números (enero = 1, febrero = 2..., diciembre = 12).
#     3. De cara a tomar fechas como argumentos, cógelas con formato datetime (YYYY-MM-DD).
#     4. Si en el texto se pregunta por un día que está por detrás del actual, ten en cuenta que hay que cambiar de mes, si no, ten en cuenta que es el mismo mes.
#     5. Si en el texto se pregunta por un mes que está por detrás del actual, ten en cuenta que hay que cambiar de año.
#     6. En caso de que no se específiquen las horas, tómalas como argumento "".
#     7. En caso de que no se específique la fecha, tómala como argumento "".
#     8. En caso de que no se específique el nombre, tómalo como argumento ""."""
