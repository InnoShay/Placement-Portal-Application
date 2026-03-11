"""Email and notification utilities."""
from flask_mail import Mail, Message
from flask import current_app
import requests
import json

mail = Mail()


def init_mail(app):
    """Initialize Flask-Mail with the app."""
    mail.init_app(app)


def send_email(to, subject, html_body, text_body=None):
    """Send an email notification."""
    try:
        msg = Message(
            subject=subject,
            recipients=[to] if isinstance(to, str) else to,
            html=html_body,
            body=text_body or ''
        )
        mail.send(msg)
        return True
    except Exception as e:
        current_app.logger.error(f'Failed to send email: {str(e)}')
        return False


def send_gchat_notification(message):
    """Send a notification via Google Chat Webhook."""
    webhook_url = current_app.config.get('GCHAT_WEBHOOK_URL')
    if not webhook_url:
        current_app.logger.warning('Google Chat webhook URL not configured')
        return False

    try:
        payload = {'text': message}
        response = requests.post(
            webhook_url,
            data=json.dumps(payload),
            headers={'Content-Type': 'application/json'}
        )
        return response.status_code == 200
    except Exception as e:
        current_app.logger.error(f'Failed to send GChat notification: {str(e)}')
        return False


def send_reminder(user_email, subject, message):
    """Send a reminder via configured channels."""
    # Try email first
    html_body = f'''
    <div style="font-family: 'Segoe UI', Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background: linear-gradient(135deg, #1a1a2e, #16213e); padding: 30px; text-align: center;">
            <h1 style="color: #e94560; margin: 0;">Placement Portal</h1>
        </div>
        <div style="padding: 30px; background: #f8f9fa;">
            <h2 style="color: #1a1a2e;">{subject}</h2>
            <p style="color: #333; line-height: 1.6;">{message}</p>
        </div>
        <div style="background: #1a1a2e; padding: 15px; text-align: center;">
            <p style="color: #888; font-size: 12px; margin: 0;">Placement Portal Application &copy; 2026</p>
        </div>
    </div>
    '''
    email_sent = send_email(user_email, subject, html_body)

    # Also try GChat
    gchat_sent = send_gchat_notification(f'*{subject}*\n{message}')

    return email_sent or gchat_sent
