import json
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.openai_client import summarize_history, llamar_api_openai
from chatbot.functions import funciones_disponibles
from chatbot.function_descriptions import function_descriptions_multiple
from chatbot.utils import (
    cargar_instrucciones_start,
    cargar_instrucciones_end,
    revisar
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)  # Permite solicitudes desde tu cliente React (evitar error CORS)

max_tokens = 1500

def pregunta_respuesta(user_message, conversation_history, language='es', mensaje_final=''):
    """
    Función principal para gestionar la conversación.
    Ahora recibe un parámetro `language` para poder manejar
    la lógica multilingüe si lo necesitas.
    """
    print(language)
    # Cargar instrucciones iniciales en cada nueva conversación
    conversation_start = cargar_instrucciones_start(language)
    conversation_end = cargar_instrucciones_end(language)

    # Si el historial es muy largo, lo resumimos
    if len(str(conversation_history)) > max_tokens:
        conversation_history = summarize_history(conversation_history)

    # Podrías usar la variable `language` para modificar la forma en que
    # preparas las instrucciones, por ejemplo añadiendo un mensaje "sistema"
    # que indique al modelo el idioma en que debe responder.
    #
    # EJEMPLO rápido (opcional):
    # conversation_start.append({
    #     "role": "system",
    #     "content": f"El usuario quiere respuestas en el idioma: {language}."
    # })

    conversation_start = conversation_start + conversation_history
    conversation_end = conversation_end + conversation_history

    # Primera llamada al modelo con las funciones disponibles
    response = llamar_api_openai(
        conversation_start,
        functions=function_descriptions_multiple,
        function_call="auto"
    )

    # Si el modelo ha decidido llamar a una función
    if hasattr(response, 'function_call') and response.function_call is not None:
        function_name = response.function_call.name
        parameters = json.loads(response.function_call.arguments)
        print(parameters)

        # Ejecutamos la función correspondiente
        if function_name in funciones_disponibles:
            function_result = funciones_disponibles[function_name](**parameters)
            print(function_result)

            # Añadimos el resultado de la función al historial
            conversation_end.append({
                "role": "assistant",
                "name": function_name,
                "content": json.dumps(function_result)
            })

            # Segunda llamada para generar la respuesta final
            final_response = llamar_api_openai(
                conversation_end,
                functions=function_descriptions_multiple,
                function_call="none"
            )
            conversation_history.append({
                "role": "assistant",
                "content": final_response.content
            })

            revision = revisar(final_response.content)
            print(revision)
            if revision == 1:
                mensaje_final += pregunta_respuesta(
                    'obten la información',
                    conversation_history,
                    language=language,  # Reenvía el idioma si se repite
                    mensaje_final=mensaje_final
                )
            mensaje_final = final_response.content + mensaje_final
            return mensaje_final

    # Si no hay function_call, el modelo ya dio una respuesta directa
    print(response.content)
    return response.content if response.content else "No se obtuvo respuesta."


@app.route('/ask', methods=['POST'])
def ask():
    # 1) Recogemos JSON del body que envía React o tu cliente
    data = request.get_json()
    question = data.get("question", "")
    conversation = data.get("conversation", [])
    language = data.get("language", "es")  # Recogemos el idioma con un default "es"

    # 2) Llamamos a la función de chatbot pasando el idioma
    answer = pregunta_respuesta(question, conversation, language=language)

    # 3) Devolvemos la respuesta en formato JSON
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
