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
    message = response.choices[0].message

    return message


def procesar_respuesta_openai(historial, prompt):

    instrucciones = instrucciones_segun_intencion(prompt)

    data_texto = str(prompt).strip("{").strip("}")

    historial.append({"role": "user", "content": data_texto})

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": f"Tengo la siguiente información:\n\n{historial}\n\n"},
            {"role": "assistant", "content": f"Sigue estas instrucciones: {instrucciones}\n"},],
        functions=function_descriptions_multiple,
        function_call="auto",
        temperature=0,
    )
    return completion.choices[0].message


def generar_respuesta_con_openai(data, historial, instrucciones):
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
                Este es el historial de la conversacion, quiero que lo uses para responder al mensaje. Historial: {historial}.
                Mensaje: {text}.
                Ejemplo historial 1: 
                - Últimos mensajes del historial:
                    - Usuario: Quiero reservar para hoy.
                    - Sistema: Estas son las horas disponibles: 12:00, 13:00.
                    - Usuario: a las 12 entonces.
                    - Sistema: Necesito que me proporciones un nombre.
                    - Usuario: alejandro.
                    -> [
                    {{"intencion": "hacer_reserva", "detalle": "hoy a las 12 nombre alejandro"}},
                  ]

                Ejemplo historial 2: 
                - Últimos mensajes del historial:
                    - Usuario: Quiero eliminar mi reserva.
                    - Sistema: ¿Podrías proporcionarme la fecha de tu reserva?
                    - Usuario: mañana
                    - Sistema: ¿A qué nombre está hecha su reserva?
                    - Usuario: alejandro.
                    -> [
                    {{"intencion": "eliminar_reserva", "detalle": "mañana, nombre alejandro"}},
                  ]

                Ejemplo 1:
                - Mensaje: "Quiero saber el menú, reservar, saber la música que se va a pinchar y cuánta gente va a haber el domingo que viene" -> Respuesta esperada:
                  [
                    {{"intencion": "info_menu", "detalle": "El domingo que viene"}},
                    {{"intencion": "hacer_reserva", "detalle": "El domingo que viene"}},
                    {{"intencion": "saber_música", "detalle": "El domingo que viene"}},
                    {{"intencion": "saber_gente", "detalle": "El domingo que viene"}}
                  ]
                Ejemplo 2:
                - Mensaje: "Quiero eliminar una reserva y poner una reclamación" -> Respuesta esperada:
                  [
                    {{"intencion": "eliminar_reserva", "detalle": ""}},
                    {{"intencion": "poner_reclamación", "detalle": ""}},
                  ]
                Ejemplo 3:
                - Mensaje: "Hola que tal, quiero saber la disponibilidad que tenéis para mañana." -> Respuesta esperada:
                  [
                    {{"intencion": "saludar", "detalle": "Hola, que tal"}},
                    {{"intencion": "info_reservas", "detalle": "para mañana"}},
                  ]
                Ejemplo 4:
                - Mensaje: "Hasta luego" -> Respuesta esperada:
                  [
                    {{"intencion": "despedir", "detalle": "Hasta luego"}},
                  ]
                Ejemplo 5:
                - Mensaje: "Gracias" -> Respuesta esperada:
                  [
                    {{"intencion": "agradecer", "detalle": "Gracias"}},
                  ]
                Ejemplo 6:
                - Mensaje: "Quiero saber la disponibilidad para reservar mañana" -> Respuesta esperada:
                  [
                    {{"intencion": "info_reservas", "detalle": "para mañana"}},
                  ]
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
        {"role": "system", "content": "Responde a este mensaje como respondería una persona que trabaja en un restaurante. IMPORTANTE: Solo quiero que saludes cuando el input sea un saludo."},
        {"role": "user", "content": message}
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=prompt,
        temperature=0.7,
    )
    texto = response.choices[0].message.content
    return texto
