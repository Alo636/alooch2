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

max_tokens = 4096

intenciones = ["hacer una reserva", "eliminar una reserva", "informarse sobre reservas",
               "informarse sobre el menú", "saludar", "agradecer", "despedirse"]


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


def revisador(mensaje):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": f"""
        Instrucciones:
                1- Quiero que revises que las fechas y la frase tienen sentido. En caso afirmativo devuelve la frase tal cual. En caso negativo corrígelo.
                2- Ten en cuenta que hoy es {hoy.strftime("%A")}, {hoy.day} del {hoy.month} de {hoy.year}.
                3- NO devuelvas tus razonamientos, solo la frase corregida o tal cual.
        """},
                  {"role": "user", "content": mensaje}],
        temperature=0,
        functions=None
    )
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
