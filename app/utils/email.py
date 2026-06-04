import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from concurrent.futures import ThreadPoolExecutor
import asyncio

executor = ThreadPoolExecutor(max_workers=3)

def _send_smtp_email_sync(to_email: str, subject: str, html_content: str):
    mail_server = os.getenv("MAIL_SERVER")
    mail_port = int(os.getenv("MAIL_PORT", "587"))
    mail_username = os.getenv("MAIL_USERNAME")
    mail_password = os.getenv("MAIL_PASSWORD")
    mail_from = os.getenv("MAIL_FROM")
    mail_from_name = os.getenv("MAIL_FROM_NAME", "LavaPro")
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{mail_from_name} <{mail_from}>"
    msg["To"] = to_email
    part = MIMEText(html_content, "html")
    msg.attach(part)

    with smtplib.SMTP(mail_server, mail_port) as server:
        server.starttls()
        server.login(mail_username, mail_password)
        server.sendmail(mail_from, to_email, msg.as_string())

async def send_activation_email(to_email: str, nombre_usuario: str, token: str):
    frontend_url = os.getenv("FRONTEND_URL", "https://app.lavapro.online")
    activation_link = f"{frontend_url}/activar-cuenta?token={token}"

    subject = "LavaPro - Invitación de Activación de Cuenta"
    
    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
                <h2 style="color: #2c3e50;">¡Hola, {nombre_usuario}!</h2>
                <p>Has sido dado de alta en el sistema de gestión de lavandería <strong>LavaPro</strong>.</p>
                <p>Para establecer tu contraseña y activar tu perfil en la plataforma, por favor hacé clic en el siguiente botón:</p>
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{activation_link}" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">
                        Activar mi Cuenta
                    </a>
                </div>
                <p style="font-size: 12px; color: #7f8c8d;">Este enlace es único y seguro. Si el botón no funciona, copiá y pegá el siguiente enlace en tu navegador:</p>
                <p style="font-size: 12px; color: #3498db; word-break: break-all;">{activation_link}</p>
                <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
                <p style="font-size: 11px; color: #95a5a6; text-align: center;">LavaPro - Gestión Inteligente de Lavandería</p>
            </div>
        </body>
    </html>
    """

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(executor, _send_smtp_email_sync, to_email, subject, html_content)