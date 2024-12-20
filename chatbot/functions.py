
import json
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from collections import defaultdict
from chatbot.utils import conversion_a_rango, extraer_fecha_de_string

load_dotenv()


CREDENTIALS_FILE = os.getenv("CREDENTIALS_FILE")

SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


SCOPES = [os.getenv("SCOPES")]
credentials = Credentials.from_service_account_file(
    CREDENTIALS_FILE, scopes=SCOPES)

service = build('sheets', 'v4', credentials=credentials)


def info_reservas(fechas=None, horas=None):
    """
    Consulta la disponibilidad para un conjunto específico de fechas y horas.
    Las fechas deben ser proporcionadas como una cadena separada por comas.
    """
    if fechas is None:
        return "Fechas no recibidas"

    # pylint: disable=no-member
    sheet = service.spreadsheets()

    fechas = [extraer_fecha_de_string(fecha.strip())
              for fecha in fechas.split(",")]

    if horas is None:
        horas = ["12:00", "13:00", "14:00", "15:00"]
    else:
        horas = horas.split(",")

    fechas_horas = [(fecha, hora) for fecha in fechas for hora in horas]

    rangos = []
    for fecha, hora in fechas_horas:
        conversion = conversion_a_rango(fecha, hora)

        if conversion == {"error": "Hora no disponible"}:
            return "Hora no disponible"
        rangos.append(conversion)

    result = sheet.values().batchGet(
        spreadsheetId=SPREADSHEET_ID,
        ranges=rangos
    ).execute()

    valores = result.get('valueRanges', [])
    disponibilidad_por_dia = defaultdict(list)

    for idx, (fecha, hora) in enumerate(fechas_horas):
        valores_rango = valores[idx].get('values', [])
        if not valores_rango:  # Si no hay valores, se considera "Libre"
            clave = fecha.strftime('%Y-%m-%d')
            disponibilidad_por_dia[clave].append(hora)

    # Convertir el defaultdict a un dict normal para el resultado final
    disponibilidad_por_dia = dict(disponibilidad_por_dia)
    if not disponibilidad_por_dia:
        return "Ocupado"

    return disponibilidad_por_dia


def hacer_reserva(fecha=None, hora=None, nombre=None):
    """
    Realiza una reserva en la hoja de cálculo de Google Sheets para un día y hora específicos.
    Devuelve un diccionario con la información de la reserva y su estado ("Completada" o "No completada").
    """
    if fecha is None:
        return "Fecha no recibida"
    if hora is None:
        return info_reservas(fecha, hora)

    disponibilidad = info_reservas(
        fecha, hora)

    if disponibilidad == "Hora no disponible" or disponibilidad == "Ocupado":
        return disponibilidad

    if nombre is None:
        return "Nombre no recibido"

    fecha_dt = extraer_fecha_de_string(fecha)
    key = f"{fecha_dt.strftime('%Y-%m-%d')}"
    if disponibilidad.get(key) == [f'{hora}']:
        rangos = []
        conversion = conversion_a_rango(fecha_dt, hora)
        if conversion == {"error": "Hora no disponible"}:
            return "Hora no disponible"
        rangos.append(conversion)
        rango = rangos[0]
        body = {'values': [[nombre]]}

        # pylint: disable=no-member
        sheet = service.spreadsheets()
        sheet.values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=rango,
            valueInputOption="RAW",
            body=body
        ).execute()

        reserva_estado = "Completada"
    else:
        reserva_estado = "No completada"

    info = {
        "fecha": fecha,
        "hora": hora,
        "nombre": nombre,
        "Reserva": reserva_estado
    }
    print(info)

    return {key: info}


def obtener_nombre(rango):
    # pylint: disable=no-member
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=rango).execute()
    valores = result.get('values', [])

    if valores:
        return valores[0][0]
    else:
        return "Celda vacía o no encontrada."


def eliminar_reserva(fecha=None, nombre=None, hora=None):
    if fecha is None:
        return "Fecha no recibida"
    if nombre is None:
        return "Nombre no recibido"

    # pylint: disable=no-member
    fecha_dt = extraer_fecha_de_string(fecha)

    if hora != None and hora != "12:00" and hora != "13:00" and hora != "14:00" and hora != "15:00":
        return "Hora erronea"

    if hora is None:
        horas = ["12:00", "13:00", "14:00", "15:00"]
    else:
        horas = [hora]
    name = "."

    for hour in horas:
        rang = conversion_a_rango(fecha_dt, hour)
        name = obtener_nombre(rang)
        if name == nombre:
            break
    if name == nombre:
        rango = rang
        body = {"ranges": [rango]}
        # pylint: disable=no-member
        request = service.spreadsheets().values().batchClear(
            spreadsheetId=SPREADSHEET_ID, body=body)
        request.execute()
        return "Reserva eliminada"
    else:
        return "Nombre incorrecto"


def info_menu(fecha):
    if fecha is None:
        return "Fecha no recibida"

    fecha_dt = extraer_fecha_de_string(fecha)
    dia = str(fecha_dt.day)

    if dia == "1":
        menu = "1-Patatas, 2-Carne"
    else:
        menu = "1-Bistec, 2-Verduritas"

    info = {
        "fecha": fecha,
        "menu": menu,
    }
    return json.dumps(info)


funciones_disponibles = {
    "info_menu": info_menu,
    "info_reservas": info_reservas,
    "hacer_reserva": hacer_reserva,
    "eliminar_reserva": eliminar_reserva,
}
