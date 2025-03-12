"""
disque
"""
import os
from datetime import datetime, timedelta
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

hoy = datetime.now()


def cargar_instrucciones_start():
    return [{"role": "system", "content": f"""Eres un asistente de restaurante cordial. Quiero que sigas fielmente estas instrucciones:
    1- Instrucciones de comportamiento: 
            - Saluda solo una vez al inicio de la conversación y no repitas saludos innecesariamente.
            - Hoy es {hoy.strftime("%A")}, {hoy.day} del {hoy.month} de {hoy.year}. Responde teniendo en cuenta esta fecha.
            - Si el usuario responde con 'vale', 'ok', 'sí', 'claro', 'de acuerdo' u otra afirmación breve, tómalos como confirmación.
    2- Instrucciones de reservas, Pasos a seguir:
        - Si te hablan para reservar en una fecha, di primero la disponibilidad que hay en esa fecha.
        - Si te preguntan por disponibilidad de reservas, mira siempre la disponibilidad con info_reservas.
        - Si estás hablando de reservas, no hace falta que digas el horario de apertura y cierre.
    3- Instrucciones de horario, Pasos a seguir:
        - Si estás hablando de horario, mira siempre el horario con get_horario.
    """}]

def cargar_instrucciones_end():
    return [{"role":"system", "content":"""Eres un asistente de restaurante cordial que informa al usuario de lo que ha devuelto el asistente sin cambiar información. Quiero que sigas fielmente estas instrucciones:
    1- Quiero que no uses nombres de días de la semana, solo fechas en formato DD-MM-YYYY.
    2- Si obtienes un error, lee el error tal cual al usuario, no te bases en el contexto del resto de mensajes.  
             
    """}]

def validar_fechas(fechas_list, fechas_cerradas):
    errores = []
    limite_futuro = hoy + timedelta(days=30)

    for fecha in fechas_list:
        try:
            fecha_dt = datetime.strptime(
                fecha, "%Y-%m-%d")  # Convertir a datetime
            if fecha_dt > limite_futuro:
                errores.append(
                    f"La fecha {fecha} supera el límite de 30 días y no es válida para reservar.")
            if fecha in fechas_cerradas:
                errores.append(
                    f"El restaurante estará cerrado el {fecha}. No es posible reservar en esa fecha.")
        except ValueError:
            errores.append(
                f"Formato de fecha inválido: {fecha}. Debe ser YYYY-MM-DD.")

    if errores:
        return {"error": errores}
    return "OK"


def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


def obtener_fechas_cerradas():
    """
    Consulta la base de datos para obtener las fechas en las que el restaurante no acepta reservas.
    Retorna una lista de fechas en formato 'YYYY-MM-DD'.
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT fecha FROM fechas_no_disponibles"
    cursor.execute(query)
    filas = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convertir las fechas a formato de lista
    return [fila[0].strftime("%Y-%m-%d") for fila in filas]