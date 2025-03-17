from chatbot.openai_client import summarize_history
from chatbot.utils import cargar_instrucciones_start

conversacion = cargar_instrucciones_start()
conversacion.append({'role': 'user', 'content': 'dime el hroario de mañana'})
conversacion.append({'role': 'assistant', 'content': 'El horario para la fecha 17-03-2025 es de 8:00 a 22:00.'})
conversacion.append({'role': 'user', 'content': 'y el del dia 23'})
conversacion.append({'role': 'assistant', 'content': 'El horario para la fecha 23-03-2025 es de 10:00 a 20:00.'})
conversacion.append({'role': 'user', 'content': 'y el 32'})
conversacion.append({'role': 'assistant', 'content': 'La fecha 32-03-2025 no es válida. Por favor, verifica la fecha y vuelve a intentarlo.'})

del conversacion[0]

print(conversacion)

print(summarize_history(conversacion))
