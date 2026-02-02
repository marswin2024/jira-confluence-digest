import logging
from datetime import datetime, timedelta
from atlassian import Jira
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class JiraCollector:
    """Collects updates from Jira over the last 24 hours."""

    def __init__(self, url: str, username: str, api_token: str, projects: Optional[List[str]] = None):
        """
        Initialize Jira collector.

        Args:
            url: Jira instance URL
            username: Jira username
            api_token: Jira API token
            projects: Optional list of project keys to filter
        """
        self.jira = Jira(url=url, username=username, password=api_token, cloud=True)
        self.projects = projects
        logger.info(f"JiraCollector initialized for {url}")

    def _build_project_filter(self) -> str:
        """Build JQL project filter."""
        if self.projects:
            project_list = ','.join(self.projects)
            return f"project in ({project_list})"
        return ""

    def get_new_tickets(self) -> List[Dict]:
        """Get tickets created in the last 24 hours."""
        try:
            project_filter = self._build_project_filter()
            jql = f"{project_filter + ' AND ' if project_filter else ''}created >= -1d ORDER BY created DESC"

            logger.info(f"Fetching new tickets with JQL: {jql}")
            issues = self.jira.jql(jql, limit=1000)

            tickets = []
            for issue in issues.get('issues', []):
                fields = issue.get('fields', {})
                tickets.append({
                    'key': issue.get('key'),
                    'summary': fields.get('summary'),
                    'status': fields.get('status', {}).get('name'),
                    'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                    'created': fields.get('created'),
                    'project': fields.get('project', {}).get('name'),
                    'project_key': fields.get('project', {}).get('key'),
                    'url': f"{self.jira.url}/browse/{issue.get('key')}",
                    'type': fields.get('issuetype', {}).get('name')
                })

            logger.info(f"Found {len(tickets)} new tickets")
            return tickets

        except Exception as e:
            logger.error(f"Error fetching new tickets: {e}")
            return []

    def get_status_changes(self) -> List[Dict]:
        """Get tickets with status changes in the last 24 hours."""
        try:
            project_filter = self._build_project_filter()
            jql = f"{project_filter + ' AND ' if project_filter else ''}status changed AFTER -1d ORDER BY updated DESC"

            logger.info(f"Fetching status changes with JQL: {jql}")
            issues = self.jira.jql(jql, limit=1000)

            tickets = []
            for issue in issues.get('issues', []):
                fields = issue.get('fields', {})

                changelog = self.jira.get_issue_changelog(issue.get('key'))
                status_changes = []

                for history in changelog.get('values', []):
                    created = history.get('created')
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))

                    if created_dt > datetime.now(created_dt.tzinfo) - timedelta(days=1):
                        for item in history.get('items', []):
                            if item.get('field') == 'status':
                                status_changes.append({
                                    'from': item.get('fromString'),
                                    'to': item.get('toString'),
                                    'when': created
                                })

                if status_changes:
                    tickets.append({
                        'key': issue.get('key'),
                        'summary': fields.get('summary'),
                        'current_status': fields.get('status', {}).get('name'),
                        'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                        'project': fields.get('project', {}).get('name'),
                        'project_key': fields.get('project', {}).get('key'),
                        'url': f"{self.jira.url}/browse/{issue.get('key')}",
                        'status_changes': status_changes
                    })

            logger.info(f"Found {len(tickets)} tickets with status changes")
            return tickets

        except Exception as e:
            logger.error(f"Error fetching status changes: {e}")
            return []

    def get_assignment_changes(self) -> List[Dict]:
        """Get tickets with assignee changes in the last 24 hours."""
        try:
            project_filter = self._build_project_filter()
            jql = f"{project_filter + ' AND ' if project_filter else ''}assignee changed AFTER -1d ORDER BY updated DESC"

            logger.info(f"Fetching assignment changes with JQL: {jql}")
            issues = self.jira.jql(jql, limit=1000)

            tickets = []
            for issue in issues.get('issues', []):
                fields = issue.get('fields', {})

                changelog = self.jira.get_issue_changelog(issue.get('key'))
                assignment_changes = []

                for history in changelog.get('values', []):
                    created = history.get('created')
                    created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))

                    if created_dt > datetime.now(created_dt.tzinfo) - timedelta(days=1):
                        for item in history.get('items', []):
                            if item.get('field') == 'assignee':
                                assignment_changes.append({
                                    'from': item.get('fromString') or 'Unassigned',
                                    'to': item.get('toString') or 'Unassigned',
                                    'when': created
                                })

                if assignment_changes:
                    tickets.append({
                        'key': issue.get('key'),
                        'summary': fields.get('summary'),
                        'status': fields.get('status', {}).get('name'),
                        'current_assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                        'project': fields.get('project', {}).get('name'),
                        'project_key': fields.get('project', {}).get('key'),
                        'url': f"{self.jira.url}/browse/{issue.get('key')}",
                        'assignment_changes': assignment_changes
                    })

            logger.info(f"Found {len(tickets)} tickets with assignment changes")
            return tickets

        except Exception as e:
            logger.error(f"Error fetching assignment changes: {e}")
            return []

    def get_new_comments(self) -> List[Dict]:
        """Get tickets with new comments in the last 24 hours."""
        try:
            project_filter = self._build_project_filter()
            jql = f"{project_filter + ' AND ' if project_filter else ''}updated >= -1d ORDER BY updated DESC"

            logger.info(f"Fetching tickets with potential new comments with JQL: {jql}")
            issues = self.jira.jql(jql, limit=1000)

            tickets = []
            for issue in issues.get('issues', []):
                fields = issue.get('fields', {})

                try:
                    comments_data = self.jira.issue_get_comments(issue.get('key'))
                    comments = comments_data.get('comments', [])

                    recent_comments = []
                    for comment in comments:
                        created = comment.get('created')
                        created_dt = datetime.fromisoformat(created.replace('Z', '+00:00'))

                        if created_dt > datetime.now(created_dt.tzinfo) - timedelta(days=1):
                            recent_comments.append({
                                'author': comment.get('author', {}).get('displayName', 'Unknown'),
                                'body': comment.get('body', '')[:200],
                                'created': created
                            })

                    if recent_comments:
                        tickets.append({
                            'key': issue.get('key'),
                            'summary': fields.get('summary'),
                            'status': fields.get('status', {}).get('name'),
                            'assignee': fields.get('assignee', {}).get('displayName', 'Unassigned') if fields.get('assignee') else 'Unassigned',
                            'project': fields.get('project', {}).get('name'),
                            'project_key': fields.get('project', {}).get('key'),
                            'url': f"{self.jira.url}/browse/{issue.get('key')}",
                            'comments': recent_comments
                        })
                except Exception as comment_error:
                    logger.warning(f"Could not fetch comments for {issue.get('key')}: {comment_error}")
                    continue

            logger.info(f"Found {len(tickets)} tickets with new comments")
            return tickets

        except Exception as e:
            logger.error(f"Error fetching new comments: {e}")
            return []

    def collect_all_updates(self) -> Dict:
        """Collect all Jira updates from the last 24 hours."""
        logger.info("Collecting all Jira updates")

        updates = {
            'new_tickets': self.get_new_tickets(),
            'status_changes': self.get_status_changes(),
            'assignment_changes': self.get_assignment_changes(),
            'new_comments': self.get_new_comments()
        }

        total_updates = sum(len(v) for v in updates.values())
        logger.info(f"Total Jira updates collected: {total_updates}")

        return updates
