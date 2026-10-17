"""Check generated pages for missing local assets and links before publishing."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import json
import re

root = Path(__file__).resolve().parent
data = json.loads((root / 'data/group.json').read_text())
showcase_slugs = set()

for section in data.get('sections', []):
    for person in section.get('people', []):
        showcase = person.get('showcase')
        if not showcase:
            continue
        required = ('slug', 'title', 'description', 'alt', 'pdf', 'preview')
        missing = [key for key in required if not isinstance(showcase.get(key), str) or not showcase[key].strip()]
        if missing:
            raise ValueError(f'{person.get("name", "Unknown member")}: missing showcase fields: {", ".join(missing)}')
        slug = showcase['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise ValueError(f'{person["name"]}: invalid showcase slug: {slug}')
        if slug in showcase_slugs:
            raise ValueError(f'Duplicate showcase slug: {slug}')
        showcase_slugs.add(slug)
        if showcase['pdf'] != f'assets/uploads/posters/{slug}.pdf':
            raise ValueError(f'{person["name"]}: showcase PDF path must match its slug')
        if showcase['preview'] != f'assets/uploads/posters/{slug}-preview.jpg':
            raise ValueError(f'{person["name"]}: showcase preview path must match its slug')
        for key in ('pdf', 'preview'):
            if not (root / showcase[key]).is_file():
                raise ValueError(f'{person["name"]}: missing showcase {key}: {showcase[key]}')
        if not (root / f'{slug}-poster.html').is_file():
            raise ValueError(f'{person["name"]}: missing generated showcase page: {slug}-poster.html')

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
