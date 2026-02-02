import logging
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import Dict, List

logger = logging.getLogger(__name__)


class EmailBuilder:
    """Builds HTML email content from Jira and Confluence data."""

    def __init__(self):
        """Initialize the email builder with Jinja2 template engine."""
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')

        self.env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

        logger.info(f"EmailBuilder initialized with template directory: {template_dir}")

    def build_digest(self, jira_updates: Dict, confluence_pages: List[Dict]) -> str:
        """
        Build the HTML digest email from collected data.

        Args:
            jira_updates: Dictionary containing Jira updates (new_tickets, status_changes, etc.)
            confluence_pages: List of updated Confluence pages

        Returns:
            HTML string ready to be sent as email
        """
        try:
            template = self.env.get_template('digest_email.html')

            current_date = datetime.now().strftime('%d.%m.%Y %H:%M Uhr')

            html_content = template.render(
                date=current_date,
                jira_updates=jira_updates,
                confluence_pages=confluence_pages
            )

            logger.info("Email HTML content generated successfully")
            return html_content

        except Exception as e:
            logger.error(f"Error building email content: {e}")
            raise

    def build_plain_text_fallback(self, jira_updates: Dict, confluence_pages: List[Dict]) -> str:
        """
        Build a plain text version of the digest as fallback.

        Args:
            jira_updates: Dictionary containing Jira updates
            confluence_pages: List of updated Confluence pages

        Returns:
            Plain text string
        """
        lines = []
        lines.append("=" * 60)
        lines.append("TÄGLICHER JIRA & CONFLUENCE DIGEST")
        lines.append("=" * 60)
        lines.append(f"Datum: {datetime.now().strftime('%d.%m.%Y %H:%M Uhr')}")
        lines.append("")

        lines.append("CONFLUENCE UPDATES")
        lines.append("-" * 60)
        if confluence_pages:
            lines.append(f"{len(confluence_pages)} Seite(n) wurden aktualisiert:")
            lines.append("")
            for page in confluence_pages:
                lines.append(f"  - {page['title']}")
                lines.append(f"    Space: {page['space_name']}")
                lines.append(f"    Von: {page['last_updated_by']}")
                lines.append(f"    URL: {page['url']}")
                lines.append("")
        else:
            lines.append("Keine Confluence-Updates.")
        lines.append("")

        lines.append("JIRA UPDATES")
        lines.append("-" * 60)

        total = sum(len(v) for v in jira_updates.values())
        if total > 0:
            lines.append(f"{total} Jira-Aktivität(en):")
            lines.append("")

            if jira_updates.get('new_tickets'):
                lines.append(f"NEUE TICKETS ({len(jira_updates['new_tickets'])})")
                for ticket in jira_updates['new_tickets']:
                    lines.append(f"  - {ticket['key']}: {ticket['summary']}")
                    lines.append(f"    Projekt: {ticket['project']} | Status: {ticket['status']}")
                    lines.append(f"    URL: {ticket['url']}")
                    lines.append("")

            if jira_updates.get('status_changes'):
                lines.append(f"STATUS-ÄNDERUNGEN ({len(jira_updates['status_changes'])})")
                for ticket in jira_updates['status_changes']:
                    lines.append(f"  - {ticket['key']}: {ticket['summary']}")
                    for change in ticket['status_changes']:
                        lines.append(f"    {change['from']} → {change['to']}")
                    lines.append("")

            if jira_updates.get('assignment_changes'):
                lines.append(f"ZUWEISUNGEN ({len(jira_updates['assignment_changes'])})")
                for ticket in jira_updates['assignment_changes']:
                    lines.append(f"  - {ticket['key']}: {ticket['summary']}")
                    for change in ticket['assignment_changes']:
                        lines.append(f"    {change['from']} → {change['to']}")
                    lines.append("")

            if jira_updates.get('new_comments'):
                lines.append(f"NEUE KOMMENTARE ({len(jira_updates['new_comments'])})")
                for ticket in jira_updates['new_comments']:
                    lines.append(f"  - {ticket['key']}: {ticket['summary']}")
                    for comment in ticket['comments']:
                        lines.append(f"    {comment['author']}: {comment['body'][:100]}...")
                    lines.append("")
        else:
            lines.append("Keine Jira-Updates.")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)
