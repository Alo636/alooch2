import openai
from datetime import datetime, timedelta
import re
from dotenv import load_dotenv
import os

# Carga la clave de API de OpenAI desde el entorno
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("La clave OPENAI_API_KEY no está configurada")

# Configuración de cliente OpenAI
openai.api_key = OPENAI_API_KEY


def detectar_intencion(mensaje):
    """
    Detecta la intención del usuario basada en palabras clave o estructuras comunes en el mensaje.
    """
    intenciones = {
        "reservar": ["reservar", "quiero reservar", "hacer una reserva"],
        "buscar_disponibilidad": ["disponible", "qué días hay libres", "horas libres", "saber disponibilidad"],
        "cancelar": ["cancelar", "anular reserva"]
    }

    mensaje = mensaje.lower()
    for intencion, palabras_clave in intenciones.items():
        for frase in palabras_clave:
            if frase in mensaje:
                return intencion

    return "intención_desconocida"


def calcular_dia_relativo(texto, dias_semana):
    """
    Calcula una fecha o rango basado en texto relativo ('mañana', 'fin de semana', etc.).
    """
    hoy = datetime.now()
    if texto == "mañana":
        return hoy + timedelta(days=1)
    elif texto == "pasado mañana":
        return hoy + timedelta(days=2)
    elif texto.startswith("próximo") and len(texto.split()) > 1:
        dia = texto.split()[1]
        if dia in dias_semana:
            dia_actual = hoy.weekday()
            dias_hasta_dia = (dias_semana[dia] - dia_actual + 7) % 7 + 7
            return hoy + timedelta(days=dias_hasta_dia)
    elif texto in dias_semana:
        dia_actual = hoy.weekday()
        dias_hasta_dia = (dias_semana[texto] - dia_actual + 7) % 7
        return hoy + timedelta(days=dias_hasta_dia)
    return None


def procesar_rango(inicio, fin, inicio_semana):
    """
    Genera fechas a partir de un rango dado. Maneja tanto días como rangos predefinidos.
    """
    fechas = []
    if isinstance(inicio, int) and isinstance(fin, int):
        fechas += [
            inicio_semana + timedelta(days=dia)
            for dia in range(inicio, fin + 1)
        ]
    elif isinstance(inicio, datetime) and isinstance(fin, datetime):
        fechas += [inicio + timedelta(days=i)
                   for i in range((fin - inicio).days + 1)]
    return fechas


def obtener_dias_especificos_v2(mensaje):
    """
    Analiza el mensaje del usuario para extraer días específicos, rangos e intención,
    utilizando tanto reglas como la API de OpenAI para procesamiento avanzado.
    """
    mensaje = mensaje.lower()
    intencion = detectar_intencion(mensaje)

    # Usar la API de OpenAI para enriquecer la interpretación del mensaje
    respuesta_api = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente que analiza mensajes sobre fechas y horarios."},
            {"role": "user", "content": mensaje}
        ]
    )

    interpretacion = respuesta_api.choices[0].message.content

    # Días de la semana y frases adicionales en español
    dias_semana = {
        "lunes": 0, "martes": 1, "miércoles": 2, "jueves": 3,
        "viernes": 4, "sábado": 5, "domingo": 6,
        "fin de semana": (5, 6)
    }

    rangos = []
    dias_mencionados = []
    semana_proxima = False
    mensajes_error = []

    # Detectar frases clave usando expresiones regulares
    tokens = re.findall(r'\b\w+\b', mensaje)

    for idx, token in enumerate(tokens):
        if token in dias_semana:
            if isinstance(dias_semana[token], tuple):
                rangos.append(dias_semana[token])
            else:
                dias_mencionados.append(dias_semana[token])
        if "semana que viene" in mensaje or "próxima semana" in mensaje:
            semana_proxima = True
        if token == "entre" and idx + 3 < len(tokens) and tokens[idx + 2] == "y":
            dia_inicio = calcular_dia_relativo(tokens[idx + 1], dias_semana)
            dia_fin = calcular_dia_relativo(tokens[idx + 3], dias_semana)
            if not dia_inicio or not dia_fin:
                mensajes_error.append(
                    f"Rango no válido entre '{tokens[idx + 1]}' y '{tokens[idx + 3]}'."
                )
            else:
                rangos.append((dia_inicio, dia_fin))

    hoy = datetime.now()
    base = hoy + timedelta(weeks=1) if semana_proxima else hoy
    inicio_semana = base - timedelta(days=base.weekday())

    fechas = []
    if dias_mencionados:
        fechas += [
            inicio_semana + timedelta(days=dia)
            for dia in dias_mencionados
        ]

    for inicio, fin in rangos:
        fechas += procesar_rango(inicio, fin, inicio_semana)

    if not fechas and not rangos and not mensajes_error:
        mensajes_error.append(
            "No se encontraron días o rangos específicos en el mensaje.")

    resultado_enriquecido = {
        "fechas": sorted(fechas),
        "intencion": intencion,
        "errores": mensajes_error,
        "interpretacion_api": interpretacion
    }

    return resultado_enriquecido


# Ejemplo de uso
mensaje_usuario = "Quiero reservar el lunes o el martes de la semana que viene, ¿qué horas libres hay?"
resultado = obtener_dias_especificos_v2(mensaje_usuario)
print(resultado)
