
function_descriptions_multiple = [
    {
        "name": "info_menu",
        "description": "La intención es obtener información sobre el menú.",
        "parameters": {
            "type": "object",
            "properties": {
                "fecha": {
                    "type": "string",
                },
            },
            "required": ["dia"],
        },

    },
    {
        "name": "info_reservas",
        "description": "La intención es obtener información sobre la disponibilidad de reservas.",
        "parameters": {
            "type": "object",
            "properties": {
                "fechas": {
                    "type": ["string", "null"],
                    "description": "La fecha de la reserva en formato YYYY-MM-DD.",
                },
                "horas": {
                    "type": ["string", "null"],
                    "description": "La hora de la reserva en formato HH:MM.",
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
