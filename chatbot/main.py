import json
import sys
import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from passlib.hash import bcrypt
from chatbot.openai_client import summarize_history, llamar_api_openai
from chatbot.functions import funciones_disponibles
from chatbot.function_descriptions import function_descriptions_multiple
from chatbot.utils import (
    cargar_instrucciones_start,
    cargar_instrucciones_end,
    revisar, get_connection
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
    user_id: Optional[int] = None


class RegisterInput(BaseModel):
    username: str
    password: str
    email: EmailStr
    telefono: Optional[str] = None


class LoginInput(BaseModel):
    username: str
    password: str


class UpdateUserRequest(BaseModel):
    user_id: int
    email: str
    telefono: str | None = None


@app.post("/ask")
async def ask(data: AskRequest):
    question = data.question
    conversation = data.conversation
    language = data.language
    answer = pregunta_respuesta(question, conversation, language=language)
    if data.user_id:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO conversaciones (user_id, contenido) VALUES (%s, %s)",
            (data.user_id, json.dumps(data.conversation +
             [{"role": "assistant", "content": answer}]))
        )
        conn.commit()
        conn.close()

    return {"answer": answer}


@app.post("/register")
def register(user: RegisterInput):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM usuarios WHERE username = %s", (user.username,))
    if cursor.fetchone():
        raise HTTPException(
            status_code=400, detail="El nombre de usuario ya está en uso.")

    hashed_pw = bcrypt.hash(user.password)
    cursor.execute(
        "INSERT INTO usuarios (username, password, email, telefono) VALUES (%s, %s, %s, %s)",
        (user.username, hashed_pw, user.email, user.telefono)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    return {
        "user_id": user_id,
        "username": user.username,
        "email": user.email,
        "telefono": user.telefono
    }


@app.post("/login")
def login(user: LoginInput):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email, telefono, password FROM usuarios WHERE username = %s", (user.username,))
    result = cursor.fetchone()
    if not result or not bcrypt.verify(user.password, result[4]):
        raise HTTPException(status_code=400, detail="Credenciales inválidas")

    return {
        "user_id": result[0],
        "username": result[1],
        "email": result[2],
        "telefono": result[3]
    }


@app.post("/update_user")
async def update_user(data: UpdateUserRequest):
    try:
        print("Datos recibidos para actualizar:", data)
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            UPDATE usuarios
            SET email = %s, telefono = %s
            WHERE id = %s
        """
        cursor.execute(query, (data.email, data.telefono, data.user_id))
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "message": "Perfil actualizado correctamente."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
        print(function_name)
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
