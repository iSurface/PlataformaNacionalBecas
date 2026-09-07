# -*- coding: utf-8 -*-
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    def send_email(to_email: str, subject: str, html_body: str) -> bool:
        """Despacha un correo electrónico utilizando SMTP / Amazon SES"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg["To"] = to_email

            part = MIMEText(html_body, "html")
            msg.attach(part)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAILS_FROM_EMAIL, [to_email], msg.as_string())
            
            logger.info(f"Correo enviado exitosamente a: {to_email} (Asunto: {subject})")
            return True
        except Exception as e:
            logger.error(f"Error al enviar correo a {to_email}: {e}")
            return False

    @classmethod
    def send_activation_email(cls, to_email: str, nombre: str, token: str) -> bool:
        """Envía el enlace de activación de cuenta (24 horas)"""
        activation_url = f"https://becas.mineduc.gob.gt/activar-cuenta?token={token}"
        subject = "Activa tu cuenta - Plataforma Nacional de Becas (MINEDUC)"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #005596;">Bienvenido a la Plataforma Nacional de Becas</h2>
            <p>Estimado(a) <strong>{nombre}</strong>,</p>
            <p>Gracias por registrarte en el Sistema de Becas del Ministerio de Educación de Guatemala.</p>
            <p>Para activar tu cuenta y acceder a las convocatorias de becas, por favor haz clic en el siguiente botón:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{activation_url}" style="background-color: #005596; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Activar mi Cuenta</a>
            </div>
            <p style="color: #666; font-size: 13px;">O copia y pega el siguiente enlace en tu navegador:<br><a href="{activation_url}">{activation_url}</a></p>
            <p style="color: #d9534f; font-size: 13px;">Este enlace tiene una vigencia estricta de 24 horas.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 11px; color: #888; text-align: center;">Ministerio de Educación de Guatemala (MINEDUC) &copy; 2026</p>
        </div>
        """
        return cls.send_email(to_email, subject, html)

    @classmethod
    def send_password_reset_email(cls, to_email: str, nombre: str, token: str) -> bool:
        """Envía el enlace de restablecimiento de contraseña (15 minutos)"""
        reset_url = f"https://becas.mineduc.gob.gt/restablecer-clave?token={token}"
        subject = "Recuperación de Contraseña - Plataforma Nacional de Becas"
        html = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #005596;">Recuperación de Contraseña</h2>
            <p>Estimado(a) <strong>{nombre}</strong>,</p>
            <p>Hemos recibido una solicitud para restablecer la contraseña de tu cuenta.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" style="background-color: #d9534f; color: white; padding: 12px 25px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">Restablecer mi Contraseña</a>
            </div>
            <p style="color: #666; font-size: 13px;">O copia y pega este enlace en tu navegador:<br><a href="{reset_url}">{reset_url}</a></p>
            <p style="color: #d9534f; font-size: 13px;">Por seguridad, este enlace expirará en 15 minutos y solo puede usarse una vez.</p>
            <p style="font-size: 12px; color: #666;">Si no realizaste esta solicitud, puedes ignorar este mensaje.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 11px; color: #888; text-align: center;">Ministerio de Educación de Guatemala (MINEDUC) &copy; 2026</p>
        </div>
        """
        return cls.send_email(to_email, subject, html)
