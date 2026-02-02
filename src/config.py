import os
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()


class Config:
    """Configuration management for the application."""

    # Jira Configuration
    JIRA_URL = os.getenv('JIRA_URL')
    JIRA_USERNAME = os.getenv('JIRA_USERNAME')
    JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')

    # Confluence Configuration
    CONFLUENCE_URL = os.getenv('CONFLUENCE_URL')
    CONFLUENCE_USERNAME = os.getenv('CONFLUENCE_USERNAME')
    CONFLUENCE_API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN')

    # Email Configuration
    SMTP_HOST = os.getenv('SMTP_HOST')
    SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')

    # Schedule Configuration
    SCHEDULE_TIME = os.getenv('SCHEDULE_TIME', '07:00')
    TIMEZONE = os.getenv('TIMEZONE', 'Europe/Berlin')

    # Optional Filters
    JIRA_PROJECTS = [p.strip() for p in os.getenv('JIRA_PROJECTS', '').split(',') if p.strip()]
    CONFLUENCE_SPACES = [s.strip() for s in os.getenv('CONFLUENCE_SPACES', '').split(',') if s.strip()]

    @classmethod
    def validate(cls):
        """Validate that all required configuration variables are set."""
        required_vars = {
            'JIRA_URL': cls.JIRA_URL,
            'JIRA_USERNAME': cls.JIRA_USERNAME,
            'JIRA_API_TOKEN': cls.JIRA_API_TOKEN,
            'CONFLUENCE_URL': cls.CONFLUENCE_URL,
            'CONFLUENCE_USERNAME': cls.CONFLUENCE_USERNAME,
            'CONFLUENCE_API_TOKEN': cls.CONFLUENCE_API_TOKEN,
            'SMTP_HOST': cls.SMTP_HOST,
            'SMTP_USERNAME': cls.SMTP_USERNAME,
            'SMTP_PASSWORD': cls.SMTP_PASSWORD,
            'RECIPIENT_EMAIL': cls.RECIPIENT_EMAIL,
        }

        missing = [var for var, value in required_vars.items() if not value]

        if missing:
            error_msg = f"Missing required environment variables: {', '.join(missing)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.info("Configuration validated successfully")
        return True


config = Config()
