"""
app/utils/email.py
──────────────────
Helper module to dispatch emails using smtplib via SMTP.
Asynchronous execution is wrapped using anyio's worker thread pool.
"""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import logging
import smtplib

import anyio

from app.core.config import settings

logger = logging.getLogger("assetflow.email")


def _send_email_sync(to_email: str, subject: str, html_content: str) -> None:
    """Synchronous implementation of SMTP email dispatch."""
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.warning("SMTP credentials are not configured. Skipping email dispatch.")
        return

    # Construct email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
    msg["To"] = to_email

    # Attach HTML content
    msg.attach(MIMEText(html_content, "html"))

    try:
        # Connect to Gmail SMTP
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # Upgrade connection to secure TLS
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAILS_FROM_EMAIL, to_email, msg.as_string())
        logger.info(f"Successfully sent email to {to_email}")
    except Exception as exc:
        logger.error(f"Failed to send email to {to_email}: {exc}")
        raise exc


async def send_email_async(to_email: str, subject: str, html_content: str) -> None:
    """Asynchronous SMTP email dispatch wrapper running in a thread pool."""
    # Execute the synchronous blocking send in an anyio worker thread
    await anyio.to_thread.run_sync(_send_email_sync, to_email, subject, html_content)
