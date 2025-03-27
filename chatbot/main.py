import json
import sys
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from chatbot.openai_client import summarize_history, llamar_api_openai
from chatbot.functions import funciones_disponibles
from chatbot.function_descriptions import function_descriptions_multiple
from chatbot.utils import (
    cargar_instrucciones_start,
    cargar_instrucciones_end,
    revisar
)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

max_tokens = 1500


class AskRequest(BaseModel):
    question: str
    conversation: list
    language: str = "es"


@app.post("/ask")
async def ask(data: AskRequest):
    question = data.question
    conversation = data.conversation
    language = data.language
    answer = pregunta_respuesta(question, conversation, language=language)
    return {"answer": answer}


def pregunta_respuesta(user_message, conversation_history, language='es', mensaje_final=''):
    conversation_start = cargar_instrucciones_start(language)
    conversation_end = cargar_instrucciones_end(language)

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

    response = llamar_api_openai(
        conversation_start,
        functions=function_descriptions_multiple,
        function_call="auto"
    )

    if hasattr(response, 'function_call') and response.function_call is not None:
        function_name = response.function_call.name
        parameters = json.loads(response.function_call.arguments)
        print(parameters)

        if function_name in funciones_disponibles:
            function_result = funciones_disponibles[function_name](
                **parameters)
            print(function_result)

            conversation_end.append({
                "role": "assistant",
                "name": function_name,
                "content": json.dumps(function_result)
            })

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
                    language=language,
                    mensaje_final=mensaje_final
                )
            mensaje_final = final_response.content + mensaje_final
            return mensaje_final

    print(response.content)
    return response.content if response.content else "No se obtuvo respuesta."

# Para correr: uvicorn main:app --reload
