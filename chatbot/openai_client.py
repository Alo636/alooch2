from openai import OpenAI
import os
from dotenv import load_dotenv
from chatbot.function_descriptions import function_descriptions_multiple
from datetime import datetime

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("La clave OPENAI_API_KEY no está configurada")

hoy = datetime.now()

client = OpenAI(
    # Defaults to os.environ.get("OPENAI_API_KEY")
)

def llamar_api_openai(conversation_history, functions=None, function_call="auto", model="gpt-4o-mini", temperature=0):
    """
    Llama a la API de OpenAI para generar una respuesta a partir del historial de conversación dado.

    Args:
        conversation_history (list): Lista de mensajes en el formato [{ "role": "user"|"assistant"|"system"|"function", "content": str, "name": Optional[str] }, ...].
        functions (list): Lista de funciones disponibles en el formato requerido por la API.
        function_call (str|dict): Puede ser:
            - "auto": Permite al modelo decidir si llama o no una función.
            - "none": Evita que el modelo llame funciones.
            - {"name": "nombre_de_funcion"}: Le indica al modelo que llame a esa función en particular.
        model (str): El modelo a utilizar, por defecto "gpt-4".
        temperature (float): Control de aleatoriedad. Por defecto 0.

    Returns:
        response_message: Un objeto con atributos .content y .function_call (si existe).
    """

    # Preparamos los argumentos para la llamada
    # El parámetro function_call se pasa de acuerdo con la documentación de OpenAI.
    # - Si es "auto" o "none", se pasa tal cual.
    # - Si es un dict con {"name": ...}, se pasa también directamente.
    request_params = {
        "model": model,
        "messages": conversation_history,
        "temperature": temperature,
    }

    if functions is not None:
        request_params["functions"] = function_descriptions_multiple

    if function_call is not None:
        request_params["function_call"] = function_call

    # Llamada a la API de OpenAI
    response = client.chat.completions.create(**request_params)

    # Extraemos el primer mensaje (asumiendo que siempre hay al menos una respuesta)
    return response.choices[0].message

def summarize_history(historial):
    # Envía el historial a la API para obtener un resumen
    summary_prompt = [
        {"role": "system", "content": "Resume el siguiente historial de conversación. Informa de que es un resumen de conversación:"},
        {"role": "user", "content": str(historial)}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=summary_prompt,
        temperature=0.7
    )
    summary = response.choices[0].message.content

    # Devuelve el resumen como un nuevo mensaje del sistema
    return [{"role": "system", "content": summary}]

def detectar_funciones(conversacion):

    summary_prompt = [
        {"role": "system", "content": "Devuelve solo el nombre sin nada más de todas las funciones que van a hacer falta para responder el mensaje del usuario separadas por comas y sin espacios."
        "No quiero que llames a ninguna función. Si no hay ninguna función a la que llamar, no devuelvas nada. No quiero que le respondas al usuario. Sigue las instrucciones."
        "-Si el usuario responde con 'vale', 'ok', 'sí', 'claro', 'de acuerdo' u otra afirmación breve, tómalos como confirmación.- En caso de recibir una afirmación, mira si estabas ofreciendo algo. En caso afirmativo llévalo a cabo. En caso negativo, ofrécele ayuda sin saludar."},
        
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=summary_prompt+conversacion,
        temperature=0,
        functions=function_descriptions_multiple,
    )
    return response.choices[0].message.content

#def revisar(mensaje):#

    prompt = [
        {"role": "system", "content": "Quiero que si ves la palabra 'procederé' o 'obtendré' en el siguiente mensaje devuelvas un punto '.'."
        "En caso de que no contengan ninguna palabra, no devuelvas nada."},
        {"role":"assistant", "content": mensaje}

    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt,
        temperature=0,
    )
    return response.choices[0].message.content
    