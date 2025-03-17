"""
disque
"""
import json
import sys
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from chatbot.openai_client import summarize_history, llamar_api_openai
from chatbot.functions import funciones_disponibles
from chatbot.function_descriptions import function_descriptions_multiple
from chatbot.utils import cargar_instrucciones_start, cargar_instrucciones_end

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)  # Permite solicitudes desde tu cliente React (evitar error CORS)



max_tokens = 1500


def pregunta_respuesta(user_message, conversation_history):
    print(conversation_history)
    # Cargar instrucciones iniciales en cada nueva conversación
    conversation_start = cargar_instrucciones_start()
    conversation_end = cargar_instrucciones_end()
    print(user_message)
    # Si el historial es muy largo, lo resumimos
    if len(str(conversation_history)) > max_tokens:
        conversation_history = summarize_history(conversation_history)

    conversation_start = conversation_start + conversation_history
    conversation_end = conversation_end + conversation_history

    # Añadimos el mensaje del usuario al historial
    conversation_start.append({"role": "user", "content": user_message})
    conversation_end.append({"role": "user", "content": user_message})

    # Primera llamada al modelo con las funciones disponibles
    response = llamar_api_openai(
        conversation_start,
        functions=function_descriptions_multiple,
        function_call="auto"
    )
    # Si el modelo ha decidido llamar a una función
    if hasattr(response, 'function_call') and response.function_call is not None:
        print("ha entrado")
        function_name = response.function_call.name
        parameters = json.loads(response.function_call.arguments)

        # Ejecutamos la función correspondiente
        if function_name in funciones_disponibles:
            function_result = funciones_disponibles[function_name](**parameters)

            # Añadimos el resultado de la función al historial
            conversation_start.append({
                "role": "assistant",
                "name": function_name,
                "content": json.dumps(function_result)
            })
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

            #conversation_history.append({
            #    "role": "assistant",
            #    "content": final_response.content
            #})

            return final_response.content

    # Si no hay function_call, el modelo ya dio una respuesta directa
    return response.content if response.content else "No se obtuvo respuesta."



@app.route('/ask', methods=['POST'])
def ask():
    # 1) Recogemos JSON del body que envía React
    data = request.get_json()
    question = data.get("question", "")
    conversation = data.get("conversation", [])
    # 2) Llamamos a la función de chatbot
    answer = pregunta_respuesta(question, conversation)

    # 3) Devolvemos la respuesta en formato JSON
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True, port=5000)

#user_prompt = input()

#while user_prompt != ".":
#    print(pregunta_respuesta(user_prompt, conversations_history_start, conversations_history_end))
#    user_prompt = input()
