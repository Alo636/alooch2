"""
disque
"""
import json
import sys
import os
from chatbot.openai_client import summarize_history, llamar_api_openai
from chatbot.functions import funciones_disponibles
from chatbot.function_descriptions import function_descriptions_multiple
from chatbot.utils import cargar_instrucciones_start, cargar_instrucciones_end

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


conversations_history_start = cargar_instrucciones_start()
conversations_history_end = cargar_instrucciones_end()
max_tokens = 4096


def pregunta_respuesta(user_message, conversation_history_start, conversation_history_end):
    # Si el historial es muy largo, lo resumimos
    if len(str(conversation_history_start)) > max_tokens:
        conversation_history_start = summarize_history(conversation_history_start)
    if len(str(conversation_history_end)) > max_tokens:
        conversation_history_end = summarize_history(conversation_history_end)

    # Añadimos el mensaje del usuario al historial
    conversation_history_start.append({"role": "user", "content": user_message})
    conversation_history_end.append({"role": "user", "content": user_message})

    # Primera llamada al modelo con las funciones disponibles
    response = llamar_api_openai(
        conversation_history_start,
        functions=function_descriptions_multiple,
        function_call="auto"  # Permitimos que el modelo llame funciones si lo requiere
    )

    # Si el modelo ha decidido llamar a una función
    if hasattr(response, 'function_call') and response.function_call is not None:
        function_name = response.function_call.name
        print(function_name)
        parameters = json.loads(response.function_call.arguments)

        # Ejecutamos la función correspondiente
        if function_name in funciones_disponibles:
            function_result = funciones_disponibles[function_name](
                **parameters)

            # Añadimos el resultado de la función como un mensaje del asistente (rol function)
            conversation_history_start.append({
                "role": "assistant",
                "name": function_name,
                "content": json.dumps(function_result)
            })
            conversation_history_end.append({
                "role": "assistant",
                "name": function_name,
                "content": json.dumps(function_result)
            })
            # Ahora volvemos a llamar a la API para que el modelo dé su respuesta final al usuario
            final_response = llamar_api_openai(
                conversation_history_end,
                functions=function_descriptions_multiple,
                function_call="none"  # Esta vez no queremos que llame otra función; debe resolver
            )
            conversation_history_start.append({
                "role": "assistant",
                "name": function_name,
                "content": final_response.content
            })
            conversation_history_end.append({
                "role": "assistant",
                "name": function_name,
                "content": final_response.content
            })
            return final_response.content

    # Si no hay function_call, el modelo ya dio una respuesta directa
    return response.content if response.content else "No se obtuvo respuesta."


user_prompt = input()

while user_prompt != ".":
    print(pregunta_respuesta(user_prompt, conversations_history_start, conversations_history_end))
    user_prompt = input()