from openai import OpenAI
import os
from dotenv import load_dotenv
from chatbot.function_descriptions import function_descriptions_multiple
import json
from datetime import datetime

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("La clave OPENAI_API_KEY no está configurada")


client = OpenAI(
    # Defaults to os.environ.get("OPENAI_API_KEY")
)

max_tokens = 4096

intenciones = ["hacer una reserva", "eliminar una reserva", "informarse sobre reservas",
               "informarse sobre el menú", "saludar", "agradecer", "despedirse"]


def procesar_respuesta_openai(historial, data_texto):
    hoy = datetime.now()
    if len(str(historial)) > max_tokens:
        historial = summarize_history(historial)

    instrucciones = f"""
    Primero que todo, hoy es {str(hoy.strftime('%d-%m-%Y'))} ({str(hoy.strftime('%A'))}).
    Quiero que decidas cual es la función más adecuada según la intención del mensaje.  
    Quiero que tomes los argumentos valorando los detalles. Sigue estos apuntes fielmente:
    IMPORTANTE: No modifiques el texto. Ejemplo: Si pone "hola", como argumento "mensaje" será "hola".
    IMPORTANTE: Ten en cuenta qué día es hoy. Todas las fechas serán posteriores a hoy.
    1. Analízalo el tiempo que necesites y luego toma una decisión.
    2. Recuerda que los meses equivalen a números (enero = 1, febrero = 2..., diciembre = 12).
    3. De cara a tomar fechas como argumentos, cógelas con formato datetime (YYYY-MM-DD).
    4. Si en el texto se pregunta por un día que está por detrás del actual, ten en cuenta que hay que cambiar de mes, si no, ten en cuenta que es el mismo mes.
    5. Si en el texto se pregunta por un mes que está por detrás del actual, ten en cuenta que hay que cambiar de año.
    6. En caso de que no se específiquen las horas, tómalas como argumento "todas"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "assistant",
                "content": f"este es el historial de la conversación: {historial}"},
            {"role": "user", "content": f"Tengo la siguiente información:\n\n{data_texto}\n\n{instrucciones}\n"},
            {"role": "assistant", "content": instrucciones}],
        functions=function_descriptions_multiple,
        function_call="auto",
        temperature=0,
    )
    historial.append(
        {"role": "user", "content": data_texto})
    return completion.choices[0].message


def generar_respuesta_con_openai(data, historial, instrucciones=""):
    """
    Genera una respuesta en lenguaje natural basada en el contenido de 'data'.

    Args:
        data (dict): Diccionario con la información a procesar.
        historial (list): Lista de mensajes que contiene el historial de la conversación.
        instrucciones (str): Mensaje adicional que indica cómo se debe estructurar la respuesta.

    Returns:
        str: Respuesta generada en lenguaje natural.
    """

    # Convertir el diccionario en un formato de texto
    data_texto = json.dumps(data, indent=2, ensure_ascii=False)

    # Crear mensaje de sistema inicial para configurar el comportamiento
    mensaje_sistema = {
        "role": "system",
        "content": (
            "Eres un elaborador de respuestas con la información que le viene dada."
        )
    }

    # Añadir la nueva información como mensaje del usuario
    mensaje_usuario = {
        "role": "user",
        "content": (
            f"Tengo la siguiente información:\n\n"
            f"{data_texto}\n\n"
            f"{instrucciones}\n"
            "Por favor, responde siguiendo estas instrucciones."
        )
    }

    # Combinar mensajes del historial con el mensaje actual
    mensajes = [mensaje_sistema] + historial + [mensaje_usuario]

    # Llamada a la API de OpenAI para generar la respuesta
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=mensajes,
        max_tokens=300,
        temperature=0.5
    )

    # Extraer y retornar el texto generado
    respuesta_generada = response.choices[0].message.content

    # Agregar la respuesta generada al historial
    historial.append({"role": "assistant", "content": respuesta_generada})

    return respuesta_generada


def summarize_history(historial):
    # Envía el historial a la API para obtener un resumen
    summary_prompt = [
        {"role": "system", "content": "Resume el siguiente historial de conversación:"},
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


def detectar_intenciones(text):
    """
    Detecta todas las intenciones presentes en un texto, manteniendo el contexto.

    Args:
        text (str): Texto a analizar.

    Returns:
        list[dict]: Lista de intenciones detectadas, cada una con su detalle.
    """
    prompt = [
        {
            "role": "user",
            "content": (
                f"""Analiza el siguiente mensaje y detecta todas las intenciones presentes, 
                pero sin dividir el texto. Devuelve una lista de intenciones encontradas 
                y sus detalles, manteniendo el contexto compartido.

                Ejemplo:
                - "Quiero saber el menú, reservar, saber la música que se va a pinchar y cuánta gente va a haber el domingo que viene" -> 
                  [
                    {{"intencion": "saber_menú", "detalle": "El domingo que viene"}},
                    {{"intencion": "reservar", "detalle": "El domingo que viene"}},
                    {{"intencion": "saber_música", "detalle": "El domingo que viene"}},
                    {{"intencion": "saber_gente", "detalle": "El domingo que viene"}}
                  ]

                Texto: {text}
                """
            )
        }
    ]

    # Llamada al modelo de OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt,
        temperature=0
    )

    # Extraer y retornar las intenciones como JSON
    intentions = json.loads(response.choices[0].message.content)
    return intentions


def responde_sin_funcion(message):
    prompt = [
        {"role": "system", "content": "Responde a este mensaje como respondería una persona que trabaja en un restaurante."},
        {"role": "user", "content": message}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt,
        temperature=0.7,
    )
    texto = response.choices[0].message.content
    return texto
