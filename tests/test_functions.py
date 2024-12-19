from datetime import datetime


def extraer_fecha_de_string(fecha: str) -> datetime:
    return datetime.strptime(fecha.strip(), "%Y-%m-%d")


frase = "2024-10-19"
frase = extraer_fecha_de_string(frase)
print(type(frase))
