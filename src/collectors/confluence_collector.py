import logging
from datetime import datetime, timedelta
from atlassian import Confluence
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ConfluenceCollector:
    """Collects updates from Confluence over the last 24 hours."""

    def __init__(self, url: str, username: str, api_token: str, spaces: Optional[List[str]] = None):
        """
        Initialize Confluence collector.

        Args:
            url: Confluence instance URL
            username: Confluence username
            api_token: Confluence API token
            spaces: Optional list of space keys to filter
        """
        self.confluence = Confluence(url=url, username=username, password=api_token, cloud=True)
        self.spaces = spaces
        logger.info(f"ConfluenceCollector initialized for {url}")

    def get_updated_pages(self) -> List[Dict]:
        """Get pages updated in the last 24 hours."""
        try:
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_str = yesterday.strftime('%Y-%m-%d')

            cql = f'lastModified >= "{yesterday_str}"'

            if self.spaces:
                space_filter = ' OR '.join([f'space = "{space}"' for space in self.spaces])
                cql = f'({space_filter}) AND {cql}'

            cql += ' ORDER BY lastModified DESC'

            logger.info(f"Fetching updated pages with CQL: {cql}")

            pages = []
            start = 0
            limit = 50

            while True:
                try:
                    results = self.confluence.cql(cql, start=start, limit=limit)

                    if not results or 'results' not in results:
                        break

                    for result in results['results']:
                        content = result.get('content', {})
                        page_id = content.get('id')

                        if not page_id:
                            continue

                        try:
                            page_details = self.confluence.get_page_by_id(
                                page_id,
                                expand='version,space,history.lastUpdated'
                            )

                            version = page_details.get('version', {})
                            space = page_details.get('space', {})
                            history = page_details.get('history', {})

                            last_updated_by = version.get('by', {}).get('displayName', 'Unknown')
                            last_updated = history.get('lastUpdated', {}).get('when', version.get('when', ''))

                            pages.append({
                                'id': page_id,
                                'title': page_details.get('title'),
                                'space_name': space.get('name'),
                                'space_key': space.get('key'),
                                'url': f"{self.confluence.url}/pages/viewpage.action?pageId={page_id}",
                                'last_updated': last_updated,
                                'last_updated_by': last_updated_by,
                                'version_number': version.get('number')
                            })

                        except Exception as page_error:
                            logger.warning(f"Could not fetch details for page {page_id}: {page_error}")
                            continue

                    if len(results['results']) < limit:
                        break

                    start += limit

                except Exception as search_error:
                    logger.error(f"Error during CQL search: {search_error}")
                    break

            logger.info(f"Found {len(pages)} updated pages")
            return pages

        except Exception as e:
            logger.error(f"Error fetching updated pages: {e}")
            return []

    def get_page_details(self, page_id: str) -> Optional[Dict]:
        """Get detailed information about a specific page."""
        try:
            page = self.confluence.get_page_by_id(
                page_id,
                expand='version,space,history,body.view'
            )

            version = page.get('version', {})
            space = page.get('space', {})

            return {
                'id': page_id,
                'title': page.get('title'),
                'space_name': space.get('name'),
                'space_key': space.get('key'),
                'url': f"{self.confluence.url}/pages/viewpage.action?pageId={page_id}",
                'last_updated': version.get('when'),
                'last_updated_by': version.get('by', {}).get('displayName', 'Unknown'),
                'version_number': version.get('number'),
                'body': page.get('body', {}).get('view', {}).get('value', '')[:500]
            }

        except Exception as e:
            logger.error(f"Error fetching page details for {page_id}: {e}")
            return None

    def collect_all_updates(self) -> List[Dict]:
        """Collect all Confluence updates from the last 24 hours."""
        logger.info("Collecting all Confluence updates")

        pages = self.get_updated_pages()

        logger.info(f"Total Confluence updates collected: {len(pages)}")
        return pages
