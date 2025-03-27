
function_descriptions_multiple = [
    {
    "name": "get_image",
    "description": "Devuelve la imagen de un platillo específico si está disponible.",
    "parameters": {
        "type": "object",
        "properties": {
            "plato": {
                "type": "string",
                "description": "Nombre del platillo del que se quiere obtener la imagen."
            }
        },
        "required": ["plato"]
    }
    },

    {
    "name": "get_contact_info",
    "description": "Devuelve la información de contacto del restaurante, incluyendo teléfono, email y página web.",
    "parameters": {}
    },
    {
        "name": "get_menu",
        "description": "Devuelve la lista de platillos disponibles para una fecha específica (YYYY-MM-DD), incluyendo imágenes.",
        "parameters": {
            "type": "object",
            "properties": {
                "fecha": {
                    "type": "string",
                    "description": "Fecha en formato YYYY-MM-DD para la que se quiere el menú"
                }
            }
        }
    },
    {
        "name": "get_horario",
        "description": "Devuelve el horario del restaurante para una o varias fechas especificadas. Si una fecha está en la lista de fechas cerradas, se indicará como 'CERRADO'. Si tiene un horario especial, se mostrará dicho horario. Si no es una fecha cerrada ni tiene horario especial, se devolverá el horario regular correspondiente al día de la semana.",
        "parameters": {
            "type": "object",
            "properties": {
                "fechas": {
                    "type": "string",
                    "description": "Lista de fechas en formato YYYY-MM-DD separadas por comas. Ejemplo: '2025-03-15,2025-03-16,2025-03-17'."
                }
            },
            "required": ["fechas"]
        }
    },
    {
        "name": "info_reservas",
        "description": "Obtener información sobre la disponibilidad de reservas.",
        "parameters": {
            "type": "object",
            "properties": {
                "fechas": {
                    "type": ["string", "null"],
                    "description": "Lista de fechas de la reserva en formato YYYY-MM-DD. Tiene que ser una cadena separada por comas.",
                    "items": {"type": "string"},
                },
                "horas": {
                    "type": ["string", "null"],
                    "description": "Lista de horas de la reserva en formato HH:MM. Tiene que ser una cadena separada por comas.",
                    "items": {"type": "string"},
                },
            },
            "required": [],
        },
    },
    {
        "name": "hacer_reserva",
        "description": "La intención es hacer una reserva.",
        "parameters": {
            "type": "object",
            "properties": {
                "fecha": {
                    "type": ["string", "null"],
                    "description": "La fecha de la reserva en formato YYYY-MM-DD.",
                },
                "hora": {
                    "type": ["string", "null"],
                    "description": "La hora de la reserva en formato HH:MM.",
                },
                "nombre": {
                    "type": ["string", "null"],
                },
                "confirmacion": {
                    "type": "boolean",
                    "description": "La confirmacion de la reserva",
                },
            },
            "required": [],
        },
    },
    {
        "name": "eliminar_reserva",
        "description": "La intención es eliminar una reserva.",
        "parameters": {
            "type": "object",
            "properties": {
                "fecha": {
                    "type": ["string", "null"],
                    "description": "La fecha de la reserva en formato YYYY-MM-DD.",
                },
                "hora": {
                    "type": ["string", "null"],
                    "description": "La hora de la reserva en formato HH:MM.",
                },
                "nombre": {
                    "type": ["string", "null"],
                },
            },
            "required": [],
        },
    },
]