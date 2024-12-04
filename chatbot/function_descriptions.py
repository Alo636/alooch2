
function_descriptions_multiple = [
    {
        "name": "info_menudeldia",
        "description": "La intención es obtener información sobre el menú.",
        "parameters": {
            "type": "object",
            "properties": {
                "dia": {
                    "type": "string",
                },
                "mes": {
                    "type": "string",
                },
                "agno": {
                    "type": "string",
                },
            },
            "required": ["dia"],
        },

    },
    {
        "name": "info_reservas_fechas_especificas",
        "description": "La intención es obtener información sobre la disponibilidad de reservas.",
        "parameters": {
            "type": "object",
            "properties": {
                "fechas": {
                    "type": "string",
                },
                "horas": {
                    "type": "string",
                },
            },
            "required": ["dia", "horas"],
        },

    },
    {
        "name": "hacer_reserva",
        "description": "La intención es hacer una reserva.",
        "parameters": {
            "type": "object",
            "properties": {
                "fecha": {
                    "type": "string",
                },
                "hora": {
                    "type": "string",
                },
                "nombre": {
                    "type": "string",
                },
            },
            "required": ["fecha", "hora", "nombre"],
        },

    },
    {
        "name": "eliminar_reserva",
        "description": "La intención es eliminar una reserva.",
        "parameters": {
            "type": "object",
            "properties": {
                "fecha": {
                    "type": "string",
                },
                "hora": {
                    "type": "string",
                },
                "nombre": {
                    "type": "string",
                },
            },
            "required": ["dia", "nombre"],
        },
    },
    {
        "name": "agradecimientos",
        "description": "La intención es agradecer o halagar.",
        "parameters": {
            "type": "object",
            "properties": {
                "mensaje": {
                    "type": "string",
                },
            },
        },
    },
    {
        "name": "saludar",
        "description": "La intención es saludar.",
        "parameters": {
            "type": "object",
            "properties": {
                "mensaje": {
                    "type": "string",
                },
            },
        },
    },
    {
        "name": "despedir",
        "description": "La intención es despedirse o marcharse.",
        "parameters": {
            "type": "object",
            "properties": {
                "mensaje": {
                    "type": "string",
                },
            },
        },
    },
]
