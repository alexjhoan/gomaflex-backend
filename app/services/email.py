from typing import List
from email.message import EmailMessage
import aiosmtplib
from app.config import get_settings


class EmailService:
    def __init__(self):
        self.settings = get_settings()

    async def send_email(
        self,
        to: List[str],
        subject: str,
        body_html: str,
        body_text: str = None,
    ) -> bool:
        """
        Envía un email usando SMTP.
        Retorna True si se envió correctamente, False en caso contrario.
        """
        if not self.settings.SMTP_USER or not self.settings.SMTP_PASSWORD:
            print("WARNING: SMTP credentials not configured, skipping email send")
            return False

        message = EmailMessage()
        message["From"] = self.settings.EMAIL_FROM
        message["To"] = ", ".join(to)
        message["Subject"] = subject

        if body_text:
            message.set_content(body_text)
        message.add_alternative(body_html, subtype="html")

        try:
            await aiosmtplib.send(
                message,
                hostname=self.settings.SMTP_HOST,
                port=self.settings.SMTP_PORT,
                start_tls=True,
                username=self.settings.SMTP_USER,
                password=self.settings.SMTP_PASSWORD,
            )
            print(f"Email sent successfully to {to}")
            return True
        except Exception as e:
            print(f"ERROR sending email: {e}")
            return False

    async def notify_new_sugerencia(self, sugerencia_data: dict) -> bool:
        """Notifica al admin sobre una nueva sugerencia."""
        subject = f"[GOMAFLEX] Nueva sugerencia: {sugerencia_data.get('tipo', 'N/A')}"
        
        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #b90014;">🔔 Nueva sugerencia recibida</h2>
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>Tipo:</strong> {sugerencia_data.get('tipo', 'N/A')}</p>
                        <p><strong>Mensaje:</strong></p>
                        <p style="background: white; padding: 15px; border-radius: 4px; border-left: 4px solid #b90014;">
                            {sugerencia_data.get('mensaje', 'Sin mensaje')}
                        </p>
                        <p><strong>Contacto:</strong> {sugerencia_data.get('contacto', 'No proporcionado')}</p>
                        <p><strong>Fecha:</strong> {sugerencia_data.get('created_at', 'N/A')}</p>
                    </div>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Este es un mensaje automático del sistema GOMAFLEX.
                    </p>
                </div>
            </body>
        </html>
        """
        
        body_text = f"""
Nueva sugerencia recibida:
Tipo: {sugerencia_data.get('tipo', 'N/A')}
Mensaje: {sugerencia_data.get('mensaje', 'Sin mensaje')}
Contacto: {sugerencia_data.get('contacto', 'No proporcionado')}
Fecha: {sugerencia_data.get('created_at', 'N/A')}

---
Este es un mensaje automático del sistema GOMAFLEX.
        """
        
        return await self.send_email(
            to=[self.settings.EMAIL_TO],
            subject=subject,
            body_html=body_html,
            body_text=body_text,
        )

    async def notify_new_contacto(self, contacto_data: dict) -> bool:
        """Notifica al admin sobre un nuevo mensaje de contacto."""
        subject = f"[GOMAFLEX] Nuevo contacto: {contacto_data.get('asunto', 'N/A')}"
        
        body_html = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #b90014;">📬 Nuevo mensaje de contacto</h2>
                    <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                        <p><strong>Nombre:</strong> {contacto_data.get('nombre', 'N/A')}</p>
                        <p><strong>Email:</strong> {contacto_data.get('email', 'N/A')}</p>
                        <p><strong>Teléfono:</strong> {contacto_data.get('telefono', 'No proporcionado')}</p>
                        <p><strong>Asunto:</strong> {contacto_data.get('asunto', 'N/A')}</p>
                        <p><strong>Mensaje:</strong></p>
                        <p style="background: white; padding: 15px; border-radius: 4px; border-left: 4px solid #b90014;">
                            {contacto_data.get('mensaje', 'Sin mensaje')}
                        </p>
                        <p><strong>Fecha:</strong> {contacto_data.get('created_at', 'N/A')}</p>
                    </div>
                    <hr style="border: none; border-top: 1px solid #eee; margin: 20px 0;">
                    <p style="color: #666; font-size: 12px;">
                        Este es un mensaje automático del sistema GOMAFLEX.
                    </p>
                </div>
            </body>
        </html>
        """
        
        body_text = f"""
Nuevo mensaje de contacto:
Nombre: {contacto_data.get('nombre', 'N/A')}
Email: {contacto_data.get('email', 'N/A')}
Teléfono: {contacto_data.get('telefono', 'No proporcionado')}
Asunto: {contacto_data.get('asunto', 'N/A')}
Mensaje: {contacto_data.get('mensaje', 'Sin mensaje')}
Fecha: {contacto_data.get('created_at', 'N/A')}

---
Este es un mensaje automático del sistema GOMAFLEX.
        """
        
        return await self.send_email(
            to=[self.settings.EMAIL_TO],
            subject=subject,
            body_html=body_html,
            body_text=body_text,
        )


# Instancia singleton
email_service = EmailService()