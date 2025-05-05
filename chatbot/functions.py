
import json
from dotenv import load_dotenv
from chatbot.utils import get_connection, obtener_fechas_cerradas, validar_fechas, format_menu_response, mesas_necesarias
from datetime import datetime, timedelta
import logging

load_dotenv()
# chatbot/functions.py

logging.basicConfig(level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def get_image(plato=None):
    """
    Devuelve la URL de la imagen de un plato específico si existe en menu_especial o menu_base.
    """
    if not plato:
        return {"error": "Debes especificar un nombre de platillo."}

    conn = get_connection()
    cursor = conn.cursor()

    # Primero busca en menu_especial
    query_base = "SELECT imagen_url FROM menu_base WHERE nombre_platillo = %s LIMIT 1"
    cursor.execute(query_base, (plato,))
    resultado = cursor.fetchone()

    if not resultado:
        query_especial = "SELECT imagen_url FROM menu_especial WHERE nombre_platillo = %s LIMIT 1"
        cursor.execute(query_especial, (plato,))
        resultado = cursor.fetchone()
        # Si no está en menu_especial, busca en menu_base
        query_base = "SELECT imagen_url FROM menu_base WHERE nombre_platillo = %s LIMIT 1"
        cursor.execute(query_base, (plato,))
        resultado = cursor.fetchone()

    conn.close()

    if resultado and resultado[0]:
        return {"imagen_url": resultado[0]}
    else:
        return {"error": "No se encontró imagen para este platillo."}


def get_contact_info():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT telefono, email, pagina_web FROM contacto LIMIT 1")
            resultado = cursor.fetchone()

    if resultado:
        return {"telefono": resultado[0], "email": resultado[1], "pagina_web": resultado[2]}
    else:
        return {"error": "Información de contacto no disponible."}


def get_menu(fecha=None):
    if not fecha:
        return {"error": "Debe proporcionar una fecha para obtener el menú."}

    conn = get_connection()
    cursor = conn.cursor()

    # Paso 1: comprobar si hay menú especial para la fecha
    cursor.execute("""
        SELECT nombre_platillo, descripcion, precio, imagen_url
        FROM menu_especial
        WHERE fecha = %s
    """, (fecha,))
    rows_especial = cursor.fetchall()

    menu = []

    if rows_especial:
        # Usar el menú especial
        for row in rows_especial:
            nombre, desc, precio, img = row
            menu.append({
                "nombre_platillo": nombre,
                "descripcion": desc,
                "precio": float(precio),
                "imagen_url": img
            })
    else:
        # Usar menú base
        cursor.execute("""
            SELECT nombre_platillo, descripcion, precio, imagen_url
            FROM menu_base
        """)
        rows_base = cursor.fetchall()
        for row in rows_base:
            nombre, desc, precio, img = row
            menu.append({
                "nombre_platillo": nombre,
                "descripcion": desc,
                "precio": float(precio),
                "imagen_url": img
            })

    conn.close()
    return format_menu_response({"menu": menu})


def get_horario_bar(fechas):
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
                    "error": "Fecha no válida."}
        return horarios

    except (ValueError, KeyError, FileNotFoundError, ConnectionError) as e:
        logging.error("Error ocurrido en functions.py: %s", str(e))
        return {"error": str(e)}

    finally:
        cursor.close()
        conn.close()


def hacer_reserva(fecha=None, hora=None, nombre=None, personas=None, confirmacion=False,):
    """
    Inserta una reserva en la base de datos solo si:
      - La fecha no está en la base de datos de fechas no disponibles.
      - La fecha no es demasiado lejana.
      - La hora es válida (12:00, 13:00, 14:00 o 15:00).
    """
    if not fecha:
        return {"error": "Falta la fecha para la reserva."}
    if not hora:
        return {"error": "Falta la hora para la reserva."}
    if not personas:
        return {"error": "¿Para cuántas personas?"}

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

    disponibilidad = info_reservas(fechas=fecha, horas=hora, personas=personas)
    if disponibilidad.get(f"{fecha} {hora}") == "Ocupada":
        return {"error": "La hora seleccionada ya está ocupada."}

    if not nombre:
        return {"error": "Falta el nombre para la reserva."}

    if not confirmacion:
        return {"error": f"Confirma la reserva para el día {fecha} a las {hora} a nombre de {nombre}?"}

    numero_mesas = mesas_necesarias(personas)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO reservas (fecha, hora, nombre)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (fecha, hora, nombre))

        cursor.execute("""
            UPDATE disponibilidad_mesas
            SET total_mesas = total_mesas - %s
            WHERE fecha = %s AND hora = %s AND total_mesas >= %s
        """, (numero_mesas, fecha, hora, numero_mesas))

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


def info_reservas(fechas=None, horas=None, personas=None):
    if not fechas:
        return {"error": "Fechas no recibidas"}
    if not personas:
        return {"error": "¿Para cuántas personas?"}

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
        horas_no_disponibles = [
            h for h in horas_solicitadas if h not in horas_permitidas]
        if horas_no_disponibles:
            return f"Las {', '.join(horas_no_disponibles)} no están disponibles para reservar."
        horas_permitidas = [
            h for h in horas_solicitadas if h in horas_permitidas]

    fechas_list = list(filter(None, fechas_list))
    if not fechas_list:
        return {"error": "No se encontraron fechas válidas."}

    numero_mesas = mesas_necesarias(personas)

    conn = get_connection()
    cursor = conn.cursor()

    respuesta = {}

    for fecha in fechas_list:
        for hora in horas_permitidas:
            # Obtener cuántas reservas hay para esa fecha y hora
            cursor.execute("""
                SELECT COUNT(*) FROM reservas WHERE fecha = %s AND hora = %s
            """, (fecha, hora))
            reservas_actuales = cursor.fetchone()[0]

            # Obtener el total de mesas disponibles desde la nueva tabla
            cursor.execute("""
                SELECT total_mesas FROM disponibilidad_mesas WHERE fecha = %s AND hora = %s
            """, (fecha, hora))
            resultado = cursor.fetchone()
            if resultado:
                mesas_disponibles = resultado[0]
            else:
                mesas_disponibles = 10  # Valor por defecto si no se encuentra registro

            clave = f"{fecha} {hora}"
            if mesas_disponibles - reservas_actuales >= numero_mesas:
                respuesta[clave] = "Libre"
            else:
                respuesta[clave] = "Ocupada"

    cursor.close()
    conn.close()
    return respuesta


def eliminar_reserva(fecha=None, hora=None, nombre=None):
    """
    Elimina una reserva existente que coincida con fecha, hora y nombre.
    Retorna un mensaje de éxito o de error si no se encontró.
    """
    if not fecha:
        return {"error": "Falta la fecha para eliminar la reserva."}

    # Se puede requerir la hora o no, depende de tu lógica.
    if not hora:
        return {"error": "Falta la hora de la reserva."}

    if not nombre:
        return {"error": "Falta el nombre para eliminar la reserva."}

    if not nombre:
        return {"error": "Falta el nombre para eliminar la reserva."}

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


def obtener_datos_usuario(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, email, telefono FROM usuarios WHERE id = %s", (user_id,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return {
            "user_id": user_id,
            "username": result[0],
            "email": result[1],
            "telefono": result[2]
        }
    else:
        return {"error": "Usuario no encontrado"}


def obtener_historial_usuario(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT contenido, created_at FROM conversaciones WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "contenido": json.loads(row[0]),
            "created_at": row[1].strftime("%Y-%m-%d %H:%M:%S")
        }
        for row in rows
    ]


funciones_disponibles = {
    "get_menu": get_menu,
    "info_reservas": info_reservas,
    "hacer_reserva": hacer_reserva,
    "eliminar_reserva": eliminar_reserva,
    "get_horario": get_horario_bar,
    "get_contact_info": get_contact_info,
    "get_image": get_image,
    "obtener_datos_usuario": obtener_datos_usuario,
    "obtener_historial_usuario": obtener_historial_usuario,
}
