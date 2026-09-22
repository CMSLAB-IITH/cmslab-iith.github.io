"""Check generated pages for missing local assets and links before publishing."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

root = Path(__file__).resolve().parent

class LinkChecker(HTMLParser):
    def handle_starttag(self, tag, attributes):
        for key, value in attributes:
            if key not in ('src', 'href') or not value:
                continue
            parsed = urlsplit(value)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = root / parsed.path.lstrip('/')
            if not target.exists():
                raise ValueError(f'Missing local file: {value}')

for page in root.glob('*.html'):
    LinkChecker().feed(page.read_text())
print('All local links and media files exist.')
