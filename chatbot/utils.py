"""
disque
"""
from datetime import datetime
from collections import defaultdict


def elegir_instruccion(function):
    if function == "info_menudeldia":
        return """
        IMPORTANTE: No digas "Hola" ni saludes.
        Busca y proporciona el menú del día exacto que se menciona en el texto del usuario. 
        Si el texto incluye una fecha específica, usa esa fecha. 
        Por ejemplo, si dice '7 de diciembre de 2024', responde con 'El menú para el día 7 de diciembre de 2024 es...'. 
        Si la el dia, el mes o el año no son recibidos, pregunta por ellos."

"""
    elif function == "info_reservas":
        return """
        Sigue estos pasos:
        IMPORTANTE: No digas "Hola" ni saludes.
        1. Las horas que te llegan son las horas que hay libres.
        2. Si obtienes una string "Hora no disponible significa que la hora no está disponible".
        3. Informa sobre las horas libres que hay.
        4. Si no hay ninguna hora libre, infórmalo sin dar detalles de las reservas.
        Ejemplo de respuesta: "Hola, gracias por tu consulta. Aquí te informo sobre la disponibilidad para el 2 de diciembre de 2024:
        A las 15:00, tenemos una mesa libre.
"""
    elif function == "hacer_reserva":
        return """
        Sigue estos pasos:
        IMPORTANTE: No digas "Hola" ni saludes.
        IMPORTANTE: No le digas al usuario lo que te ha retornado la función. Solo dile lo que deba saber. Ejemplo: La funcion retorna "Hora no disponible", respuesta:
        "La hora que has solicitado no está disponible para reservar" o "El horario que has elegido no se encuentra disponible para reserva.", por ejemplo. No repitas siempre la misma respuesta.
        1. Si la data es una string "Fecha no recibida", quiero que le preguntes al usuario para cuándo sería la reserva.
        2. Si la data es una string "Hora no dispobible", quiero que le informes al usuario que esa hora no está disponible para reservar.
        3. Si la data es una string "Hora no recibida", quiero que preguntes al usuario sobre qué hora querría hacer la reserva.
        4. Si la data es una string "Nombre no recibido", quiero que preguntes al usuario sobre qué nombre querría hacer la reserva.
        En caso de que la data no sea ninguna de las anteriores sigue estos pasos:
        1. Confirma al usuario si la reserva se ha realizado o no viendo el argumento Reserva.
        2. Si la reserva no ha podido completarse, dile que esa hora ya está ocupada, sin muchas especificaciones.
        3. Si la reserva se ha completado, incluye en tu respuesta los detalles de la misma.
        """
    elif function == "eliminar_reserva":
        return """
        IMPORTANTE: No digas "Hola" ni saludes.
        Informa al usuario si se ha eliminado la reserva. 
        En caso contrario, informa del error que ha habido.
        """
    elif function == "agradecimientos":
        return """
        IMPORTANTE: No digas "Hola" ni saludes.
        Responde al usuario por sus agradecimientos de una forma cordial.
        """
    elif function == "saludar":
        return """
        Responde al usuario por su saludo de una forma cordial de no más de 15 palabras.
        """
    elif function == "despedir":
        return """
        IMPORTANTE: No digas "Hola" ni saludes.
        Responde al mensaje de despedida del usuario de una forma cordial de no más de 20 palabras.
        """
    elif function == "ninguna_funcion":
        return """
        Responde al mensaje del usuario. Si es algo que no está relacionado con el restaurante, di que no puedes responder a eso. En caso de que no entiendas
        el mensaje, informa al usuario de que no le has entendido.
        """
    return ""


def conversion_a_rango(dia="No recibido", mes="No recibido", agno="No recibido", hora="No recibida"):
    # Mapeo de horas a columnas
    horas_a_columnas = {
        "12:00": "B",
        "13:00": "C",
        "14:00": "D",
        "15:00": "E"
    }

    # Validar entrada
    if dia == "No recibido" or hora == "No recibida" or mes == "No recibido" or agno == "No recibido":
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


def filtrar_dias_libres(data):
    resultado = {}

    # Agrupar las claves por día
    horarios_por_dia = defaultdict(dict)
    for fecha_hora, estado in data.items():
        dia, hora = fecha_hora.split()
        horarios_por_dia[dia][hora] = estado

    # Procesar cada día
    for dia, horas in horarios_por_dia.items():
        libres = [f"{dia} {hora}" for hora,
                  estado in horas.items() if estado == "Libre"]
        if libres:
            resultado[dia] = libres
        else:
            resultado[dia] = "Todo ocupado"

    return resultado


def instrucciones_segun_intencion(prompt):

    hoy = datetime.now()
    # Diccionario de intenciones y sus instrucciones asociadas
    intenciones = {
        "info_reservas": f"""Primero que todo, hoy es {str(hoy.strftime('%d-%m-%Y'))} ({str(hoy.strftime('%A'))}).
    Quiero que tomes los argumentos valorando los detalles. Sigue estos apuntes fielmente:
    1. Recuerda que los meses equivalen a números (enero = 1, febrero = 2..., diciembre = 12).
    2. De cara a tomar fechas como argumentos, cógelas con formato datetime (YYYY-MM-DD).
    3. Si en el texto se pregunta por un día que está por detrás del actual, ten en cuenta que hay que cambiar de mes, si no, ten en cuenta que es el mismo mes.
    4. Si en el texto se pregunta por un mes que está por detrás del actual, ten en cuenta que hay que cambiar de año.
    5. En caso de que no se específiquen las horas, tómalas como argumento "".
    6. En caso de que no se específique la fecha, tómala como argumento ""
    """,

        "info_menú": """Quiero que tomes los argumentos valorando los detalles.
    En caso de que no se especifique el día, el mes o el agno, tómalos como argumento "".""",
        "hacer_reserva": "Instrucciones para realizar una reserva",
        "eliminar_reserva": "Instrucciones para eliminar una reserva",
        "saludar": "Instrucciones para saludar",
        "despedir": "Instrucciones para despedir",
        "agradecer": "Instrucciones para agradecer"
    }

    # Obtener la intención desde el prompt
    intencion = prompt.get("intencion")

    # Buscar las instrucciones asociadas o devolver un error
    instrucciones = intenciones.get(
        intencion, "error en la identificación de instrucciones")

    # Resultado
    return instrucciones
