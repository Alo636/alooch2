from openai import OpenAI
import os
from dotenv import load_dotenv
from chatbot.function_descriptions import function_descriptions_multiple
import json
from chatbot.utils import instrucciones_segun_intencion

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


def procesar_respuesta_openai(historial, prompt):

    instrucciones = instrucciones_segun_intencion(prompt)

    data_texto = str(prompt).strip("{").strip("}")

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "assistant",
                "content": f"este es el historial de la conversación: {historial}"},
            {"role": "user", "content": f"Tengo la siguiente información:\n\n{data_texto}\n\nSigue estas instrucciones: {instrucciones}\n"},
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


def detectar_intenciones(text, historial):
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
                Quiero que leas el último mensaje del historial para obtener las intenciones del texto. Historial: {historial}.
                Ejemplo: 
                - Último mensaje del historial: 

                Ejemplo 1:
                - "Quiero saber el menú, reservar, saber la música que se va a pinchar y cuánta gente va a haber el domingo que viene" -> 
                  [
                    {{"intencion": "info_menú", "detalle": "El domingo que viene"}},
                    {{"intencion": "hacer_reserva", "detalle": "El domingo que viene"}},
                    {{"intencion": "saber_música", "detalle": "El domingo que viene"}},
                    {{"intencion": "saber_gente", "detalle": "El domingo que viene"}}
                  ]
                Ejemplo 2:
                - "Quiero eliminar una reserva y poner una reclamación" -> 
                  [
                    {{"intencion": "eliminar_reserva", "detalle": ""}},
                    {{"intencion": "poner_reclamación", "detalle": ""}},
                  ]
                Ejemplo 3:
                - "Hola que tal, quiero saber la disponibilidad para reservar que tenéis para mañana." -> 
                  [
                    {{"intencion": "saludar", "detalle": "Hola, que tal"}},
                    {{"intencion": "info_reservas", "detalle": "para mañana"}},
                  ]
                Ejemplo 4:
                - "Hasta luego" -> 
                  [
                    {{"intencion": "despedir", "detalle": "Hasta luego"}},
                  ]
                Ejemplo 5:
                - "Gracias" -> 
                  [
                    {{"intencion": "agradecer", "detalle": "Gracias"}},
                  ]
                Ejemplo 6:
                - "Quiero saber la disponibilidad para reservar mañana" -> 
                  [
                    {{"intencion": "info_reservas", "detalle": "para mañana"}},
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
