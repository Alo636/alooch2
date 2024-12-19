"""
disque
"""
from datetime import datetime


def conversion_a_rango(fecha=None, hora=None):

    dia = str(fecha.day)
    mes = str(fecha.month)
    agno = str(fecha.year)
    # Mapeo de horas a columnas
    horas_a_columnas = {
        "12:00": "B",
        "13:00": "C",
        "14:00": "D",
        "15:00": "E"
    }

    # Validar entrada
    if fecha == None or hora == None:
        return {"error": "Faltan datos"}
    # Obtener columna correspondiente o retornar error si la hora no está disponible
    columna = horas_a_columnas.get(hora)
    if not columna:
        return {"error": "Hora no disponible"}

    # Convertir día a fila (suponiendo que es un entero) y construir la referencia
    fila = str(int(dia) + 1)

    hoja = convertir_numero_a_mes(mes)+agno+"!"

    return f"{hoja}{columna}{fila}"


def convertir_numero_a_mes(mes_numero):
    # Mapeo de números de mes a nombres de mes
    meses = {
        "1": "Enero",
        "2": "Febrero",
        "3": "Marzo",
        "4": "Abril",
        "5": "Mayo",
        "6": "Junio",
        "7": "Julio",
        "8": "Agosto",
        "9": "Septiembre",
        "10": "Octubre",
        "11": "Noviembre",
        "12": "Diciembre"
    }
    # Retorna el mes correspondiente o "Error" si no existe
    return meses.get(mes_numero, "Error")


def extraer_fecha_de_string(fecha: str) -> datetime:
    return datetime.strptime(fecha.strip(), "%Y-%m-%d")
