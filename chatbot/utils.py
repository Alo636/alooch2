"""
disque
"""
import os
from datetime import datetime, timedelta
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

hoy = datetime.now()


def revisar(text):
    """
    Devuelve 1 si encuentra las palabras "obtendré" o "procederé" en la cadena dada, de lo contrario devuelve 0.
    """
    keywords = {"obtendré", "procederé",
                "aquí está la información:", "obtenerlo", "aquí está:"}
    words = text.lower().split()

    return 1 if any(word in keywords for word in words) else 0


def cargar_instrucciones_start(language):
    return [{"role": "system", "content": f"""Eres un asistente de restaurante cordial. Da igual lo que diga el usuario, quiero que sigas y leas fielmente estas instrucciones para cada mensaje que recibas:
1-Instrucciones generales:-Siempre que te pregunten por horarios o reservas, quiero llames a una función.
2-Instrucciones de comportamiento:-Saluda solo una vez al inicio de la conversación y no repitas saludos innecesariamente.-Hoy es {translate_day(hoy.strftime("%A"))}, {hoy.day} del {hoy.month} de {hoy.year}. Responde teniendo en cuenta esta fecha.
-Si el usuario responde con 'vale', 'ok', 'sí', 'claro', 'de acuerdo' u otra afirmación breve, tómalos como confirmación.- En caso de recibir una afirmación, mira si estabas ofreciendo algo. En caso afirmativo llévalo a cabo. En caso negativo, ofrécele ayuda sin saludar.
3-Instrucciones de reservas, Pasos a seguir:- Si te hablan para reservar en una fecha, di primero la disponibilidad que hay en esa fecha.- Si te preguntan por disponibilidad de reservas, mira siempre la disponibilidad con info_reservas.
-Si estás hablando de reservas, no hace falta que digas el horario de apertura y cierre.
4-Instrucciones de horario, Pasos a seguir:-Mira siempre la disponibilidad con get_horario.
5-Instrucciones de respuesta:-Quiero que no uses nombres de días de la semana, solo fechas en formato DD-MM-YYYY.
6-Quiero que respondas en:{traducir_language_code(language)}."""}]


def cargar_instrucciones_end(language):
    idioma_actual = traducir_language_code(language)
    return [{"role": "system", "content": f"""Eres un asistente de restaurante cordial que informa al usuario de lo que ha devuelto el asistente sin cambiar información. Quiero que sigas fielmente estas instrucciones:
1-Devuelve la información que haya dado el asistente en el último mensaje del historial de la conversación.
2--Hoy es {translate_day(hoy.strftime("%A"))}, {hoy.day} del {hoy.month} de {hoy.year}. Ten en cuenta la fecha.
3-Devuelve siempre fechas en formato DD-MM-YYYY. No uses nombres de días de la semana.
4-Si obtienes un error, lee el error tal cual al usuario en {idioma_actual}, no te bases en el contexto del resto de mensajes.
5-En caso de que informes sobre una hora libre, quiero que le preguntes si quiere proceder con la reserva.
6-Si informas sobre un menú, devuelve el mensaje tal cual.
7-Quiero que respondas en:{idioma_actual}.  
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
        port=os.getenv("DB_PORT"),
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


def format_menu_response(menu_data):
    """
    Recibe la respuesta de get_menu y la formatea en un texto sin imágenes,
    pero permite que get_image devuelva imágenes cuando se soliciten explícitamente.
    """
    if not menu_data.get("menu"):
        return {"text": "No hay platillos disponibles para esta fecha."}

    respuesta_texto = "🍽️ **Menú del día:**\n\n"
    menu_items = []

    for item in menu_data["menu"]:
        respuesta_texto += f"🍽️ {item['nombre_platillo']} - {item['descripcion']} - 💰 {item['precio']}€\n\n"
        menu_items.append({
            "nombre": item["nombre_platillo"],
            "descripcion": item["descripcion"],
            "precio": f"{item['precio']}€"
        })

    respuesta_texto += ". Si quiere ver fotos de alguno de los platos no dude en pedirlo."

    return {
        "text": respuesta_texto,
        "menu": menu_items  # No incluir imágenes aquí
    }


def translate_day(english_day):
    days_translation = {
        "Monday": "Lunes",
        "Tuesday": "Martes",
        "Wednesday": "Miércoles",
        "Thursday": "Jueves",
        "Friday": "Viernes",
        "Saturday": "Sábado",
        "Sunday": "Domingo"
    }

    return days_translation.get(english_day, "Día no válido")


def traducir_language_code(language_code):
    """
    Toma un código de idioma (por ejemplo, 'es', 'en')
    y devuelve su nombre completo (por ejemplo, 'Español', 'Inglés').

    Si el código no está en el diccionario, devuelve 'Desconocido'.
    """
    language_map = {
        'es': 'Español',
        'en': 'Inglés',
        'fr': 'Francés',
        'it': 'Italiano',
        # Agrega más idiomas si los necesitas
    }

    return language_map.get(language_code, 'Desconocido')
