"""
disque
"""
from chatbot.openai_client import summarize_history, llamar_api_openai
from chatbot.functions import funciones_disponibles
from chatbot.function_descriptions import function_descriptions_multiple
import json
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

hoy = datetime.now()


conversations_history = [{"role": "system", "content": "Eres un asistente de restaurante cordial. Saluda solo una vez al inicio de la conversación y no repitas saludos innecesariamente. "},
                         {"role": "system", "content": "Si el usuario responde con 'vale', 'ok', 'está bien', u otra confirmación breve tras haberte ofrecido más ayuda, simplemente reconoce su respuesta brevemente y no repitas la invitación."},
                         {"role": "system", "content": f"Hoy es {hoy.day} del {hoy.month} de {hoy.year}. Responde teniendo en cuenta esta fecha."},]

max_tokens = 4096


def pregunta_respuesta(user_message, conversation_history):
    # Si el historial es muy largo, lo resumimos
    if len(str(conversation_history)) > max_tokens:
        conversation_history = summarize_history(conversation_history)

    # Añadimos el mensaje del usuario al historial
    conversation_history.append({"role": "user", "content": user_message})

    # Primera llamada al modelo con las funciones disponibles
    response = llamar_api_openai(
        conversation_history,
        functions=function_descriptions_multiple,
        function_call="auto"  # Permitimos que el modelo llame funciones si lo requiere
    )

    # Si el modelo ha decidido llamar a una función
    if hasattr(response, 'function_call') and response.function_call is not None:
        function_name = response.function_call.name
        parameters = json.loads(response.function_call.arguments)

        # Ejecutamos la función correspondiente
        if function_name in funciones_disponibles:
            function_result = funciones_disponibles[function_name](
                **parameters)

            # Añadimos el resultado de la función como un mensaje del asistente (rol function)
            conversation_history.append({
                "role": "assistant",
                "name": function_name,
                "content": json.dumps(function_result)
            })

            # Ahora volvemos a llamar a la API para que el modelo dé su respuesta final al usuario
            final_response = llamar_api_openai(
                conversation_history,
                functions=function_descriptions_multiple,
                function_call="none"  # Esta vez no queremos que llame otra función; debe resolver
            )
            return final_response.content

    # Si no hay function_call, el modelo ya dio una respuesta directa
    return response.content if response.content else "No se obtuvo respuesta."


user_prompt = input()

while user_prompt != ".":
    print(pregunta_respuesta(user_prompt, conversations_history))
    user_prompt = input()
