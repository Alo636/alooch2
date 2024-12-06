"""
disque
"""
from chatbot.openai_client import procesar_respuesta_openai, generar_respuesta_con_openai, detectar_intenciones, responde_sin_funcion, summarize_history
from chatbot.utils import elegir_instruccion
from chatbot.functions import funciones_disponibles
from chatbot.function_descriptions import function_descriptions_multiple
import json
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

conversation_history = [
    {"role": "system", "content": "Este es el historial de la conversación."},
]

max_tokens = 4096


def pregunta_respuesta(prompt, history):

    if len(str(history)) > max_tokens:
        history = summarize_history(history)

    data_texto = str(prompt).strip("{").strip("}")

    if prompt.get("intencion") not in [func["name"] for func in function_descriptions_multiple]:
        return responde_sin_funcion(data_texto)

    output = procesar_respuesta_openai(
        history, prompt)
    print(output)
    if hasattr(output, 'function_call'):
        function_name = output.function_call.name
        parameters = json.loads(output.function_call.arguments)

        if function_name in funciones_disponibles:
            response = funciones_disponibles[function_name](**parameters)
            respuesta_openai = generar_respuesta_con_openai(
                response, conversation_history, elegir_instruccion(function_name))
            return respuesta_openai

    return output.content if output.content is not None else "No se obtuvo respuesta."


user_prompt = input()

while user_prompt != ".":
    intenciones = detectar_intenciones(user_prompt, conversation_history)

    print(intenciones)
    for intencion in intenciones:
        print(pregunta_respuesta(intencion, conversation_history))

    user_prompt = input()
