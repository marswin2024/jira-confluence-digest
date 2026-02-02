import logging
import signal
import sys
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from config import config
from collectors.jira_collector import JiraCollector
from collectors.confluence_collector import ConfluenceCollector
from reporters.email_builder import EmailBuilder
from reporters.email_sender import EmailSender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('/app/logs/digest.log')
    ]
)
logger = logging.getLogger(__name__)


class DigestApp:
    """Main application for Jira & Confluence Daily Digest."""

    def __init__(self):
        """Initialize the application with all components."""
        logger.info("Initializing Jira & Confluence Daily Digest Application")

        config.validate()

        self.jira_collector = JiraCollector(
            url=config.JIRA_URL,
            username=config.JIRA_USERNAME,
            api_token=config.JIRA_API_TOKEN,
            projects=config.JIRA_PROJECTS if config.JIRA_PROJECTS else None
        )

        self.confluence_collector = ConfluenceCollector(
            url=config.CONFLUENCE_URL,
            username=config.CONFLUENCE_USERNAME,
            api_token=config.CONFLUENCE_API_TOKEN,
            spaces=config.CONFLUENCE_SPACES if config.CONFLUENCE_SPACES else None
        )

        self.email_builder = EmailBuilder()

        self.email_sender = EmailSender(
            smtp_host=config.SMTP_HOST,
            smtp_port=config.SMTP_PORT,
            username=config.SMTP_USERNAME,
            password=config.SMTP_PASSWORD,
            recipient=config.RECIPIENT_EMAIL
        )

        self.scheduler = BlockingScheduler(timezone=config.TIMEZONE)

        logger.info("Application initialized successfully")

    def daily_digest_job(self):
        """Main job that runs daily to collect and send the digest email."""
        logger.info("=" * 80)
        logger.info("Starting daily digest job")
        logger.info("=" * 80)

        try:
            logger.info("Step 1: Collecting Jira updates")
            jira_updates = self.jira_collector.collect_all_updates()

            logger.info("Step 2: Collecting Confluence updates")
            confluence_pages = self.confluence_collector.collect_all_updates()

            logger.info("Step 3: Building email content")
            html_content = self.email_builder.build_digest(jira_updates, confluence_pages)
            plain_text_content = self.email_builder.build_plain_text_fallback(jira_updates, confluence_pages)

            logger.info("Step 4: Sending email")
            subject = f"Daily Digest - Jira & Confluence Updates"

            success = self.email_sender.send_email(
                html_content=html_content,
                subject=subject,
                plain_text_content=plain_text_content
            )

            if success:
                logger.info("✅ Daily digest job completed successfully")
            else:
                logger.error("❌ Daily digest job failed: Email could not be sent")

        except Exception as e:
            logger.error(f"❌ Daily digest job failed with error: {e}", exc_info=True)

        logger.info("=" * 80)

    def run_once(self):
        """Run the digest job immediately (for testing)."""
        logger.info("Running digest job immediately (test mode)")
        self.daily_digest_job()

    def start_scheduler(self):
        """Start the scheduler to run the digest job daily."""
        hour, minute = config.SCHEDULE_TIME.split(':')

        self.scheduler.add_job(
            self.daily_digest_job,
            CronTrigger(hour=int(hour), minute=int(minute)),
            id='daily_digest',
            name='Daily Jira & Confluence Digest',
            replace_existing=True
        )

        logger.info(f"Scheduler configured to run daily at {config.SCHEDULE_TIME} ({config.TIMEZONE})")

        def signal_handler(signum, frame):
            logger.info("Received shutdown signal, stopping scheduler...")
            self.scheduler.shutdown()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        logger.info("Starting scheduler (press Ctrl+C to exit)")
        logger.info(f"Next run scheduled for: {self.scheduler.get_jobs()[0].next_run_time}")

        try:
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped")


def main():
    """Main entry point."""
    logger.info("Starting Jira & Confluence Daily Digest")

    import os
    run_once = os.getenv('RUN_ONCE', 'false').lower() == 'true'

    app = DigestApp()

    if run_once:
        app.run_once()
    else:
        app.start_scheduler()


if __name__ == '__main__':
    main()
