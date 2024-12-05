from chatbot.openai_client import detectar_intenciones

# Texto de ejemplo
text = "reservar para el 20 del 12 y saber el menu"
texto = detectar_intenciones(text)
# intencion = json.dumps(texto)
texto = str(texto[0])

texto = texto.strip("{").strip("}")
print(texto)

# print(str(texto[0].get('intencion')) + " " + str(texto[0].get('detalle')))
