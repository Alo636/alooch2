
import json
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials
from chatbot.utils import conversion_a_rango, extraer_fecha_de_string, filtrar_dias_libres

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
    if fechas == None:
        return "Fechas no recibidas"

    disponibilidad = {}

    # pylint: disable=no-member
    sheet = service.spreadsheets()

    fechas = [extraer_fecha_de_string(fecha.strip())
              for fecha in fechas.split(",")]

    if horas == None:
        horas = ["12:00", "13:00", "14:00", "15:00"]

    fechas_horas = [(fecha, hora) for fecha in fechas for hora in horas]

    print(fechas_horas)

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
    for idx, (fecha, hora) in enumerate(fechas_horas):
        valores_rango = valores[idx].get('values', [])
        clave = f"{fecha.strftime('%Y-%m-%d')} {hora}"
        disponibilidad[clave] = "Libre" if not valores_rango else valores_rango[0][0]
    dias_libres = filtrar_dias_libres(disponibilidad)
    return dias_libres


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
        fecha, [hora])
    if disponibilidad == "Hora no disponible":
        return disponibilidad

    if nombre is None:
        return "Nombre no recibido"

    fecha_dt = extraer_fecha_de_string(fecha)
    key = f"{fecha_dt.strftime('%Y-%m-%d')}"
    if disponibilidad.get(key) == [f'{fecha} {hora}']:
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
    dia = str(fecha_dt.day)
    mes = str(fecha_dt.month)
    agno = str(fecha_dt.year)

    if hora is None:
        horas = ["12:00", "13:00", "14:00", "15:00"]
    else:
        horas = [hora]
    name = "."

    for hour in horas:
        rang = conversion_a_rango(dia, mes, agno, hour)
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
