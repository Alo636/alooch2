from chatbot.openai_client import procesar_respuesta_openai

texto = "quiero reservar para el 7 de diciembre"
conversation_history = [
    {"role": "system", "content": "Este es el historial de la conversación."},
]
print(procesar_respuesta_openai(texto, conversation_history))


def dividir_texto(text):
    prompt = [
        {
            "role": "user",
            "content": (
                f"""Analiza el mensaje y decide si debe ser dividido en frases. 
                No dividas el mensaje si hacerlo causa que las frases pierdan contexto 
                o se vuelvan confusas. Mantén las frases completas y significativas.
                Teniendo en cuenta estas intenciones: {intenciones}. Divídelo solo si:
                - Contiene varias intenciones separadas que no dependen entre sí.
                - Cada frase puede entenderse de manera independiente después de dividirla.
                - La división no afecta el significado original.

                Si no se cumplen estas condiciones, devuelve el texto tal cual sólamente, sin añadir nada más.
 

                Si el mensaje tiene una intención clara que se comunica en una sola frase, 
                no lo dividas. Por ejemplo:
                - "Quiero reservar para el 21 a la una" -> "Quiero reservar para el 21 a la una".
                - "Quiero saber el menú del domingo y reservar para ese día" -> 
                  "Quiero saber el menú del domingo". 
                  "Y reservar para ese día".
                - "Hola, buenos días" -> "Hola, buenos días".

                Devuelve el texto dividido sólo si es absolutamente necesario. 
                De lo contrario, devuélvelo tal cual.

                Texto: {text}
                """
            )
        }
    ]
