
from dotenv import load_dotenv
from chatbot.utils import get_connection, obtener_fechas_cerradas, validar_fechas, format_menu_response
from datetime import datetime, timedelta
import logging

load_dotenv()
# chatbot/functions.py

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_contact_info():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT telefono, email, pagina_web FROM contacto LIMIT 1")
    resultado = cursor.fetchone()
    conn.close()

    if resultado:
        return {
            "telefono": resultado[0],
            "email": resultado[1],
            "pagina_web": resultado[2]
        }
    else:
        return {"error": "Información de contacto no disponible."}


def get_menu(fecha=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT nombre_platillo, descripcion, precio, imagen_url
        FROM menu_fecha
        WHERE fecha = %s
    """
    cursor.execute(query, (fecha,))
    
    rows = cursor.fetchall()
    conn.close()

    menu = []
    for row in rows:
        nombre_platillo, descripcion, precio, imagen_url = row
        menu.append({
            "nombre_platillo": nombre_platillo,
            "descripcion": descripcion,
            "precio": float(precio),
            "imagen_url": imagen_url
        })

    return format_menu_response({"menu": menu})



def get_horario(fechas):
    if not fechas:
        return {"error": "Debe proporcionar al menos una fecha o un rango de fechas en formato YYYY-MM-DD."}
    
    conn = get_connection()
    cursor = conn.cursor()

    try:
        # Convertir la entrada a una lista de fechas
        if isinstance(fechas, str):
            fechas_list = [f.strip() for f in fechas.split(",")]
        else:
            return {"error": "El formato de fechas debe ser una cadena separada por comas."}

        # Obtener las fechas cerradas
        fechas_cerradas = obtener_fechas_cerradas()
        # Diccionario para almacenar horarios de cada fecha
        horarios = {}

        # Mapeo de días en inglés a español para la base de datos
        for fecha in fechas_list:
            try:
                fecha = str(fecha)  # Asegurar que la fecha sea string
                datetime.strptime(fecha, "%Y-%m-%d")  # Validar formato

                # 1. Verificar si la fecha está en la lista de fechas cerradas
                if fecha in fechas_cerradas:
                    horarios[fecha] = {"estado": "cerrado"}
                    continue  # Pasar a la siguiente fecha

                # 2. Buscar horario especial
                query = "SELECT hora_apertura, hora_cierre FROM horario_especial WHERE fecha = %s"
                cursor.execute(query, (fecha,))
                resultado = cursor.fetchone()
                if resultado:
                    horarios[fecha] = {
                        "hora_apertura": str(resultado[0]),
                        "hora_cierre": str(resultado[1])
                    }
                    continue  # Pasar a la siguiente fecha
                # 3. Si no hay horario especial, obtener horario normal según el día de la semana
                dia_semana = datetime.strptime(
                    fecha, "%Y-%m-%d").strftime("%A")
                query = "SELECT hora_apertura, hora_cierre FROM horario WHERE dia_semana = %s"
                cursor.execute(query, (dia_semana,))
                resultado = cursor.fetchone()
                if resultado:
                    horarios[fecha] = {
                        "hora_apertura": str(resultado[0]),
                        "hora_cierre": str(resultado[1])
                    }
                else:
                    horarios[fecha] = {"estado": "HORARIO NO DISPONIBLE"}

            except ValueError:
                horarios[fecha] = {
                    "error": "Formato de fecha inválido. Debe ser YYYY-MM-DD."}
        print(horarios)
        return horarios

    except (ValueError, KeyError, FileNotFoundError, ConnectionError) as e:
        logging.error("Error ocurrido en functions.py: %s", str(e))
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


def hacer_reserva(fecha=None, hora=None, nombre=None):
    """
    Inserta una reserva en la base de datos solo si:
      - La fecha no está en la base de datos de fechas no disponibles.
      - La fecha no es demasiado lejana.
      - La hora es válida (12:00, 13:00, 14:00 o 15:00).
    """
    if not nombre:
        return {"error": "Falta el nombre para la reserva."}
    if not fecha:
        return {"error": "Falta la fecha para la reserva."}
    if not hora:
        return {"error": "Falta la hora para la reserva."}

    # Convertir la fecha de string a objeto datetime
    fecha_reserva = datetime.strptime(fecha, "%Y-%m-%d")
    hoy = datetime.now()

    # **1. Verificar que la fecha no está demasiado lejos (Ejemplo: máximo 30 días)**

    limite_futuro = hoy + timedelta(days=30)
    if fecha_reserva > limite_futuro:
        return {"error": "Solo se pueden hacer reservas con un máximo de 30 días de antelación."}

    # **2. Obtener las fechas cerradas desde la base de datos y verificar**
    fechas_cerradas = obtener_fechas_cerradas()
    if fecha in fechas_cerradas:
        return {"error": f"El restaurante estará cerrado el {fecha}. No es posible reservar en esa fecha."}

    # **3. Validar que la hora sea permitida**
    horas_permitidas = ["12:00", "13:00", "14:00", "15:00"]
    if hora not in horas_permitidas:
        return {"error": "Solo se permiten reservas a las 12:00, 13:00, 14:00 o 15:00."}

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO reservas (fecha, hora, nombre)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (fecha, hora, nombre))
        conn.commit()

        reserva_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return {"status": "Completada", "reserva_id": reserva_id}


    except (ValueError, KeyError, FileNotFoundError, ConnectionError) as e:
        logging.error("Error ocurrido en functions.py: %s", str(e))
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


def info_reservas(fechas=None, horas=None):
    if not fechas:
        return {"error": "Fechas no recibidas"}

    if isinstance(fechas, str):
        fechas_list = [f.strip() for f in fechas.split(",")]
    elif isinstance(fechas, list):
        fechas_list = fechas
    else:
        return {"error": "Formato de fechas inválido"}
    
    fechas_cerradas = obtener_fechas_cerradas()
    fechas_validadas = validar_fechas(fechas_list, fechas_cerradas)

    if fechas_validadas != "OK":
        return fechas_validadas

    horas_permitidas = ["12:00", "13:00", "14:00", "15:00"]

    if horas:
        horas_solicitadas = [h.strip() for h in horas.split(",")]
        horas_permitidas = [
            h for h in horas_solicitadas if h in horas_permitidas]

    fechas_list = list(filter(None, fechas_list))
    if not fechas_list:
        return {"error": "No se encontraron fechas válidas."}

    conn = get_connection()
    cursor = conn.cursor()

    placeholders = ",".join(["%s"] * len(fechas_list))
    query = f"SELECT fecha, hora FROM reservas WHERE fecha IN ({placeholders})"

    cursor.execute(query, tuple(fechas_list))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    horas_ocupadas = {}
    for fecha_ocupada, hora_ocupada in rows:
        fecha_str = str(fecha_ocupada)
        hora_str = str(hora_ocupada)[:5]  # Convertir "HH:MM:SS" a "HH:MM"

        if fecha_str not in horas_ocupadas:
            horas_ocupadas[fecha_str] = set()
        horas_ocupadas[fecha_str].add(hora_str)

    respuesta = {}
    for fecha in fechas_list:
        ocupadas = horas_ocupadas.get(fecha, set())
        disponibilidad = {}
        for h in horas_permitidas:
            disponibilidad[f"{fecha} {h}"] = "Ocupada" if h in ocupadas else "Libre"
        respuesta.update(disponibilidad)
    return respuesta

def eliminar_reserva(fecha=None, hora=None, nombre=None):
    """
    Elimina una reserva existente que coincida con fecha, hora y nombre.
    Retorna un mensaje de éxito o de error si no se encontró.
    """
    if not fecha or not nombre:
        return {"error": "Faltan la fecha o el nombre para eliminar la reserva."}

    # Se puede requerir la hora o no, depende de tu lógica.
    if not hora:
        return {"error": "Falta la hora de la reserva."}

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            DELETE FROM reservas
            WHERE fecha = %s AND hora = %s AND nombre = %s
        """
        cursor.execute(query, (fecha, hora, nombre))
        conn.commit()

        if cursor.rowcount > 0:
            result = "Reserva eliminada."
        else:
            result = "No se encontró una reserva con esos datos."

        cursor.close()
        conn.close()

        return {"status": result}

    except (ValueError, KeyError, FileNotFoundError, ConnectionError) as e:
        logging.error("Error ocurrido en functions.py: %s", str(e))
        return {"error": str(e)}


funciones_disponibles = {
    "get_menu": get_menu,
    "info_reservas": info_reservas,
    "hacer_reserva": hacer_reserva,
    "eliminar_reserva": eliminar_reserva,
    "get_horario": get_horario,
    "get_contact_info": get_contact_info,
}
