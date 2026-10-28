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
        """Despacha un correo electrónico utilizando Amazon SES (o SMTP como fallback)"""
        # 1. Intentar despacho mediante Amazon SES si está habilitado
        if getattr(settings, "USE_SES", True):
            try:
                import boto3
                ses_client = boto3.client("ses", region_name=getattr(settings, "AWS_REGION", "us-east-1"))
                response = ses_client.send_email(
                    Source=f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>",
                    Destination={
                        "ToAddresses": [to_email]
                    },
                    Message={
                        "Subject": {
                            "Data": subject,
                            "Charset": "UTF-8"
                        },
                        "Body": {
                            "Html": {
                                "Data": html_body,
                                "Charset": "UTF-8"
                            }
                        }
                    }
                )
                message_id = response.get("MessageId", "N/A")
                logger.info(f"[SES] Correo despachado exitosamente a: {to_email} (MessageId: {message_id}, Asunto: {subject})")
                return True
            except Exception as ses_err:
                logger.warning(f"[SES] No fue posible despachar vía Amazon SES: {ses_err}. Procediendo con fallback SMTP...")

        # 2. Fallback a servidor SMTP (Mailpit o relé local)
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg["To"] = to_email

            part = MIMEText(html_body, "html", "utf-8")
            msg.attach(part)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                if settings.SMTP_USER and settings.SMTP_PASSWORD:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAILS_FROM_EMAIL, [to_email], msg.as_string())
            
            logger.info(f"[SMTP] Correo enviado exitosamente a: {to_email} (Asunto: {subject})")
            return True
        except Exception as e:
            logger.error(f"Error al enviar correo a {to_email}: {e}")
            return False

    @classmethod
    def send_activation_email(cls, to_email: str, nombre: str, token: str) -> bool:
        """Envía el enlace oficial de activación de cuenta (24 horas)"""
        base_url = getattr(settings, "FRONTEND_BASE_URL", "http://becas-alb-production-1257891277.us-east-1.elb.amazonaws.com").rstrip("/")
        activation_url = f"{base_url}/api/v1/auth/activate?token={token}"
        subject = "Activa tu cuenta - Plataforma Nacional de Becas (MINEDUC)"
        html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 620px; margin: auto; padding: 25px; border: 1px solid #dce4ec; border-radius: 10px; background-color: #ffffff;">
            <div style="text-align: center; border-bottom: 2px solid #005596; padding-bottom: 15px; margin-bottom: 20px;">
                <h1 style="color: #005596; font-size: 22px; margin: 0; font-weight: 700;">MINISTERIO DE EDUCACIÓN</h1>
                <p style="color: #555555; font-size: 13px; margin: 5px 0 0 0;">Plataforma Nacional de Gestión y Asignación de Becas</p>
            </div>
            
            <h2 style="color: #1e293b; font-size: 18px; margin-top: 0;">¡Bienvenido(a), {nombre}!</h2>
            <p style="color: #475569; font-size: 15px; line-height: 1.6;">
                Gracias por registrarte como postulante en la Plataforma Nacional de Becas del Ministerio de Educación de Guatemala.
            </p>
            <p style="color: #475569; font-size: 15px; line-height: 1.6;">
                Para verificar tu dirección de correo electrónico, proteger tu identidad y habilitar el acceso a las convocatorias de becas activas, por favor haz clic en el siguiente botón:
            </p>
            
            <div style="text-align: center; margin: 35px 0;">
                <a href="{activation_url}" style="background-color: #005596; color: #ffffff; padding: 14px 32px; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 16px; display: inline-block; box-shadow: 0 4px 6px -1px rgba(0, 85, 150, 0.2);">
                    Activar mi Cuenta de Postulante
                </a>
            </div>
            
            <div style="background-color: #f8fafc; border-left: 4px solid #005596; padding: 12px 16px; margin: 20px 0; border-radius: 0 6px 6px 0;">
                <p style="color: #64748b; font-size: 13px; margin: 0; line-height: 1.5;">
                    <strong>¿No funciona el botón?</strong> Copia y pega este enlace directo en tu navegador web:<br>
                    <a href="{activation_url}" style="color: #005596; word-break: break-all;">{activation_url}</a>
                </p>
            </div>

            <p style="color: #b91c1c; font-size: 13px; font-weight: 500;">
                &#9888; Este enlace tiene una vigencia de 24 horas y solo puede utilizarse una vez.
            </p>
            
            <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 25px 0;">
            <p style="font-size: 12px; color: #94a3b8; text-align: center; margin: 0;">
                Gobierno de Guatemala &bull; Ministerio de Educación (MINEDUC) &copy; 2026<br>
                Este mensaje fue enviado de forma automática por el sistema nacional de notificaciones.
            </p>
        </div>
        """
        return cls.send_email(to_email, subject, html)

    @classmethod
    def send_password_reset_email(cls, to_email: str, nombre: str, token: str) -> bool:
        """Envía el enlace de restablecimiento de contraseña (15 minutos)"""
        base_url = getattr(settings, "FRONTEND_BASE_URL", "http://becas-alb-production-1257891277.us-east-1.elb.amazonaws.com").rstrip("/")
        reset_url = f"{base_url}/?reset_token={token}"
        subject = "Recuperación de Contraseña - Plataforma Nacional de Becas"
        html = f"""
        <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 620px; margin: auto; padding: 25px; border: 1px solid #dce4ec; border-radius: 10px; background-color: #ffffff;">
            <div style="text-align: center; border-bottom: 2px solid #005596; padding-bottom: 15px; margin-bottom: 20px;">
                <h1 style="color: #005596; font-size: 22px; margin: 0; font-weight: 700;">MINISTERIO DE EDUCACIÓN</h1>
                <p style="color: #555555; font-size: 13px; margin: 5px 0 0 0;">Plataforma Nacional de Gestión y Asignación de Becas</p>
            </div>
            
            <h2 style="color: #1e293b; font-size: 18px; margin-top: 0;">Recuperación de Contraseña</h2>
            <p style="color: #475569; font-size: 15px; line-height: 1.6;">Estimado(a) <strong>{nombre}</strong>,</p>
            <p style="color: #475569; font-size: 15px; line-height: 1.6;">
                Hemos recibido una solicitud para restablecer la contraseña de acceso a tu cuenta.
            </p>
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
