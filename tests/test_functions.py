import os
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()


def enviar_correo_reserva(fecha, hora, nombre, email_destino):
    asunto = "Reserva hecha - Restaurante La Esquina"
    remitente = os.getenv("EMAIL_REMITENTE")
    password = os.getenv("EMAIL_PASSWORD")
    servidor_smtp = os.getenv("EMAIL_SERVIDOR")
    puerto_smtp = int(os.getenv("EMAIL_PUERTO"))

    # Cuerpo en texto plano
    texto_plano = f"""
Tu reserva ha sido registrada con éxito.

Nombre: {nombre}
Fecha: {fecha}
Hora: {hora}

Gracias por reservar con nosotros.
—
Restaurante La Esquina
Tel: 123 456 789
Web: www.restaurante.com
"""

    # Cuerpo en HTML
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <h2 style="color: #000;">🍽️ ¡Tu reserva ha sido realizada!</h2>
        <p><strong>Nombre:</strong> {nombre}</p>
        <p><strong>Fecha:</strong> {fecha}</p>
        <p><strong>Hora:</strong> {hora}</p>
        <br>
        <p>Gracias por reservar con nosotros. Te esperamos con gusto.</p>
        <hr>
        <p style="font-size: 0.9em;">
          — Restaurante La Esquina<br>
          📞 123 456 789<br>
          🌐 <a href="https://www.restaurante.com">www.restaurante.com</a>
        </p>
      </body>
    </html>
    """

    # Preparar el mensaje
    mensaje = MIMEMultipart("alternative")
    mensaje["Subject"] = asunto
    mensaje["From"] = remitente
    mensaje["To"] = email_destino

    # Adjuntar texto plano + HTML
    mensaje.attach(MIMEText(texto_plano, "plain"))
    mensaje.attach(MIMEText(html, "html"))

    # Enviar el correo
    try:
        with smtplib.SMTP_SSL(servidor_smtp, puerto_smtp) as servidor:
            servidor.login(remitente, password)
            servidor.sendmail(remitente, email_destino, mensaje.as_string())
        print(f"✅ Correo enviado a {email_destino}")
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")


date = "24-07-2025"
hour = "13:00"
name = "Pedro"
email = "alejandro.alonso.arnas@gmail.com"

enviar_correo_reserva(date, hour, name, email)
