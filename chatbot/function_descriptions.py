
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
        "name": "get_horario_bar",
        "description": "Devuelve el horario del bar para una o varias fechas especificadas.",
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
                "personas": {
                    "type": ["integer", "null"],
                    "description": "Número de personas para la reserva."
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
                "personas": {
                    "type": ["integer", "null"],
                    "description": "Número de personas para la reserva."
                },
                "confirmacion": {
                    "type": "boolean",
                    "description": "Es true cuando el usuario confirma la reserva.",
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
    {
        "name": "obtener_datos_usuario",
        "description": "Devuelve el nombre de usuario, email y teléfono del usuario.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID del usuario"
                }
            },
            "required": ["user_id"]
        }
    },
    {
        "name": "obtener_historial_usuario",
        "description": "Devuelve las conversaciones previas del usuario.",
        "parameters": {
            "type": "object",
            "properties": {
                "user_id": {
                    "type": "integer",
                    "description": "ID del usuario"
                }
            },
            "required": ["user_id"]
        }
    },
]
