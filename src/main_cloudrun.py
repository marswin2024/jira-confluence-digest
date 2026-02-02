import logging
import sys
import os
from flask import Flask, request, jsonify

from config import config
from collectors.jira_collector import JiraCollector
from collectors.confluence_collector import ConfluenceCollector
from reporters.email_builder import EmailBuilder
from reporters.email_sender import EmailSender

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


def run_digest_job():
    """Main job that collects and sends the digest email."""
    logger.info("=" * 80)
    logger.info("Starting daily digest job")
    logger.info("=" * 80)

    try:
        config.validate()

        jira_collector = JiraCollector(
            url=config.JIRA_URL,
            username=config.JIRA_USERNAME,
            api_token=config.JIRA_API_TOKEN,
            projects=config.JIRA_PROJECTS if config.JIRA_PROJECTS else None
        )

        confluence_collector = ConfluenceCollector(
            url=config.CONFLUENCE_URL,
            username=config.CONFLUENCE_USERNAME,
            api_token=config.CONFLUENCE_API_TOKEN,
            spaces=config.CONFLUENCE_SPACES if config.CONFLUENCE_SPACES else None
        )

        email_builder = EmailBuilder()

        email_sender = EmailSender(
            smtp_host=config.SMTP_HOST,
            smtp_port=config.SMTP_PORT,
            username=config.SMTP_USERNAME,
            password=config.SMTP_PASSWORD,
            recipient=config.RECIPIENT_EMAIL
        )

        logger.info("Step 1: Collecting Jira updates")
        jira_updates = jira_collector.collect_all_updates()

        logger.info("Step 2: Collecting Confluence updates")
        confluence_pages = confluence_collector.collect_all_updates()

        logger.info("Step 3: Building email content")
        html_content = email_builder.build_digest(jira_updates, confluence_pages)
        plain_text_content = email_builder.build_plain_text_fallback(jira_updates, confluence_pages)

        logger.info("Step 4: Sending email")
        subject = f"Daily Digest - Jira & Confluence Updates"

        success = email_sender.send_email(
            html_content=html_content,
            subject=subject,
            plain_text_content=plain_text_content
        )

        if success:
            logger.info("✅ Daily digest job completed successfully")
            return {"status": "success", "message": "Email sent successfully"}
        else:
            logger.error("❌ Daily digest job failed: Email could not be sent")
            return {"status": "error", "message": "Email could not be sent"}

    except Exception as e:
        logger.error(f"❌ Daily digest job failed with error: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}

    finally:
        logger.info("=" * 80)


@app.route('/run-digest', methods=['POST', 'GET'])
def trigger_digest():
    """HTTP endpoint to trigger the digest job (called by Cloud Scheduler)."""
    logger.info("Digest job triggered via HTTP endpoint")

    result = run_digest_job()

    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route('/', methods=['GET'])
def root():
    """Root endpoint."""
    return jsonify({
        "service": "Jira & Confluence Daily Digest",
        "status": "running",
        "endpoints": {
            "/run-digest": "POST - Trigger digest job",
            "/health": "GET - Health check"
        }
    }), 200


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
