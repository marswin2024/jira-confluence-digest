import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional
import time

logger = logging.getLogger(__name__)


class EmailSender:
    """Sends emails via SMTP."""

    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str, recipient: str):
        """
        Initialize email sender.

        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            username: SMTP username (usually the sender email)
            password: SMTP password or app password
            recipient: Default recipient email address
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.recipient = recipient

        logger.info(f"EmailSender initialized for {smtp_host}:{smtp_port}")

    def send_email(
        self,
        html_content: str,
        subject: str,
        plain_text_content: Optional[str] = None,
        recipient: Optional[str] = None,
        max_retries: int = 3
    ) -> bool:
        """
        Send an email with HTML content and plain text fallback.

        Args:
            html_content: HTML email body
            subject: Email subject
            plain_text_content: Plain text fallback (optional)
            recipient: Override default recipient (optional)
            max_retries: Number of retry attempts on failure

        Returns:
            True if email was sent successfully, False otherwise
        """
        recipient_email = recipient or self.recipient

        for attempt in range(1, max_retries + 1):
            try:
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.username
                msg['To'] = recipient_email

                if plain_text_content:
                    part1 = MIMEText(plain_text_content, 'plain', 'utf-8')
                    msg.attach(part1)

                part2 = MIMEText(html_content, 'html', 'utf-8')
                msg.attach(part2)

                logger.info(f"Connecting to SMTP server {self.smtp_host}:{self.smtp_port} (Attempt {attempt}/{max_retries})")

                with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=30) as server:
                    server.set_debuglevel(0)
                    server.ehlo()

                    if server.has_extn('STARTTLS'):
                        logger.info("Starting TLS encryption")
                        server.starttls()
                        server.ehlo()

                    logger.info(f"Logging in as {self.username}")
                    server.login(self.username, self.password)

                    logger.info(f"Sending email to {recipient_email}")
                    server.send_message(msg)

                logger.info(f"Email sent successfully to {recipient_email}")
                return True

            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP Authentication failed: {e}")
                logger.error("Please check your username and password. For Gmail, use an App Password.")
                return False

            except smtplib.SMTPException as e:
                logger.error(f"SMTP error on attempt {attempt}/{max_retries}: {e}")
                if attempt < max_retries:
                    wait_time = attempt * 2
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Email not sent.")
                    return False

            except Exception as e:
                logger.error(f"Unexpected error sending email on attempt {attempt}/{max_retries}: {e}")
                if attempt < max_retries:
                    wait_time = attempt * 2
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error("Max retries reached. Email not sent.")
                    return False

        return False

    def test_connection(self) -> bool:
        """
        Test SMTP connection and authentication.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Testing SMTP connection to {self.smtp_host}:{self.smtp_port}")

            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.set_debuglevel(0)
                server.ehlo()

                if server.has_extn('STARTTLS'):
                    server.starttls()
                    server.ehlo()

                server.login(self.username, self.password)

            logger.info("SMTP connection test successful")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication test failed: {e}")
            return False

        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False
