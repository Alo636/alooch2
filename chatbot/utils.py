"""
disque
"""
from datetime import datetime


def elegir_instruccion(function):
    if function == "info_menu":
        return """
        Quiero que informes sobre el menú del día solicitado.
        Si recibes "Fecha no recibida", pide al usuario que te facilite la fecha.

"""
    elif function == "info_reservas":
        return """
        Sigue estos pasos:
        1. Las horas que te llegan son las horas que hay libres.
        2. Si obtienes una string "Fechas no recibidas" pide al usuario que te facilite la fecha por la que quiere preguntar.
        3. Si obtienes una string "Hora no disponible" informa al usuario sobre que esa hora no está disponible.
        4. Informa sobre las horas libres que hay.
        5. Si no hay ninguna hora libre, infórmalo sin dar detalles de las reservas.
"""
    elif function == "hacer_reserva":
        return """
        Sigue estos pasos:
        1. Si la data es una string "Fecha no recibida", quiero que le preguntes al usuario para cuándo sería la reserva.
        2. Si la data es una string "Hora no dispobible", quiero que le informes al usuario que esa hora no está disponible para reservar.
        3. Si la data es una string "Hora no recibida", quiero que pidas al usuario qué hora querría hacer la reserva.
        4. Si la data es un dict con la fecha y un valor que dice 'Todo ocupado', quiero que informes al usuario que esa hora está ocupada.
        5. Si la data es una string "Nombre no recibido", quiero que preguntes al usuario a qué nombre querría hacer la reserva.

        En caso de que la data no sea ninguna de las anteriores sigue estos pasos:
        1. Confirma al usuario si la reserva se ha realizado o no viendo el argumento Reserva.
        2. Si la reserva se ha completado, incluye en tu respuesta los detalles de la misma.
        """
    elif function == "eliminar_reserva":
        return """
        IMPORTANTE: No le digas al usuario la información que recibes.
        Sigue estos pasos:
        1. Si la data es una string "Fecha no recibida", quiero que le preguntes al usuario la fecha de su reserva.
        2. Si la data es una string "Nombre no recibido", quiero que preguntes al usuario a qué nombre está hecha su reserva.
        3. Si la data es una string "Hora erronea", quiero que informes al usuario de que ha proporcionado una hora erronea.
        En caso de que la data no sea ninguna de las anteriores:
        Informa al usuario de que su reserva se ha eliminado.
        """
    return ""


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


def extraer_fecha_de_string(fecha):
    fecha_tansformed = fecha.strip("")
    fecha_tansformed = fecha_tansformed.split('-')
    agno = int(fecha_tansformed[0])
    mes = int(fecha_tansformed[1])
    dia = int(fecha_tansformed[2])
    date = datetime(agno, mes, dia)

    return date


def instrucciones_segun_intencion(prompt):

    hoy = datetime.now()
    # Diccionario de intenciones y sus instrucciones asociadas
    intenciones = {
        "info_reservas": f"""
        Primero, ten en cuenta que hoy es {str(hoy.strftime('%d-%m-%Y'))} ({str(hoy.strftime('%A'))}).

        Por favor, procesa los argumentos siguiendo estas reglas:

        1. Si no se especifican las fechas o las horas, establece estos argumentos como None.
        2. Los meses deben interpretarse como números (enero = 1, febrero = 2, ..., diciembre = 12).
        3. Las fechas deben estar en formato datetime: YYYY-MM-DD.
        4. Si se menciona un día, asume que se refiere al próximo día futuro, no a uno pasado. 
        Ajusta automáticamente el mes y el año si es necesario.
        5. Si se menciona un día anterior al actual con una fecha específica, ajusta automáticamente el mes o el año para que corresponda al futuro.


        Sigue estas reglas de forma estricta para procesar correctamente los datos.
        Ejemplos si hoy fuese 10 de diciembre:
            Ejemplo1: "'intencion': 'info_reservas', 'detalle': 'disponibilidad para reservar'" -> fechas:null, horas:null
            Ejemplo2: "'intencion': 'info_reservas', 'detalle': 'disponibilidad para reservar mañana'" -> fechas:2024-12-11, horas:null
            Ejemplo3: "'intencion': 'info_reservas', 'detalle': 'información para reservar pasado mañana a las 12 '" -> fechas:2024-12-12, horas:12:00
        """,

        "info_menu":
        f"""Quiero que tomes los argumentos valorando los detalles.
        En caso de que no se especifique la fecha, tómala como argumento None.
        Ten en cuenta que hoy es {str(hoy.strftime('%d-%m-%Y'))} ({str(hoy.strftime('%A'))}).
        """,

        "hacer_reserva": f"""
        Primero, ten en cuenta que hoy es {str(hoy.strftime('%d-%m-%Y'))} ({str(hoy.strftime('%A'))}).

        Por favor, procesa los argumentos siguiendo estas reglas:

        1. Si no se especifican las horas, la fecha o el nombre, establece estos argumentos como None.
        2. Los meses deben interpretarse como números (enero = 1, febrero = 2, ..., diciembre = 12).
        3. Las fechas deben estar en formato datetime: YYYY-MM-DD.
        4. Si se menciona un día, asume que se refiere al próximo día futuro, no a uno pasado. 
        Ajusta automáticamente el mes y el año si es necesario.
        5. Si se menciona un día anterior al actual con una fecha específica, ajusta automáticamente el mes o el año para que corresponda al futuro.

        Sigue estas reglas de forma estricta para procesar correctamente los datos.
        """,

        "eliminar_reserva": f"""
        Primero, ten en cuenta que hoy es {str(hoy.strftime('%d-%m-%Y'))} ({str(hoy.strftime('%A'))}).

        Por favor, procesa los argumentos siguiendo estas reglas:

        1. Si no se especifican las horas, la fecha o el nombre, establece estos argumentos como None.
        2. Los meses deben interpretarse como números (enero = 1, febrero = 2, ..., diciembre = 12).
        3. Las fechas deben estar en formato datetime: YYYY-MM-DD.
        4. Si se menciona un día, asume que se refiere al próximo día futuro, no a uno pasado. 
        Ajusta automáticamente el mes y el año si es necesario.
        5. Si se menciona un día anterior al actual con una fecha específica, ajusta automáticamente el mes o el año para que corresponda al futuro.
        

        Sigue estas reglas de forma estricta para procesar correctamente los datos.
        """,

    }

    # Obtener la intención desde el prompt
    intencion = prompt.get("intencion")

    # Buscar las instrucciones asociadas o devolver un error
    instrucciones = intenciones.get(
        intencion, "error en la identificación de instrucciones")

    # Resultado
    return instrucciones
