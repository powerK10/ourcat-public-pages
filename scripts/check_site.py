"""Dependency-free checks for the static OurCat site. Run with Python 3."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.ids = []
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])

errors = []
pages = {p.name: Page(p.read_text(encoding='utf-8')) for p in ROOT.glob('*.html')}
for name, page in pages.items():
    def require(condition, message):
        if not condition:
            errors.append(f'{name}: {message}')
    source = (ROOT / name).read_text(encoding='utf-8')
    require(any(t == 'html' and a.get('lang') == 'en-GB' for t,a in page.tags), 'British English language declaration')
    require(sum(t == 'h1' for t,a in page.tags) == 1, 'exactly one primary heading')
    require(any(t == 'main' and a.get('id') == 'main' for t,a in page.tags), 'main landmark and skip destination')
    require(any(t == 'a' and a.get('href') == '#main' for t,a in page.tags), 'skip link')
    require(len(page.ids) == len(set(page.ids)), 'unique fragment IDs')
    require(any(t == 'meta' and a.get('name') == 'viewport' for t,a in page.tags), 'responsive viewport')
    require(any(t == 'meta' and a.get('name') == 'description' and a.get('content') for t,a in page.tags), 'page description')
    require(bool(re.search(r'<title>[^<]+</title>', source)), 'page title')
    require(not any(t in ('script','iframe','form') for t,a in page.tags), 'no website scripts, embeds or custom data collection')
    if name in ('join.html','guide.html','feedback.html'):
        require(any(t == 'meta' and a.get('name') == 'robots' and 'noindex' in a.get('content','') for t,a in page.tags), 'private-journey noindex')
    else:
        require(any(t == 'link' and a.get('rel') == 'canonical' for t,a in page.tags), 'public canonical URL')
    for tag, attrs in page.tags:
        if tag == 'img':
            require('alt' in attrs, 'image alternative')
            require('width' in attrs and 'height' in attrs, 'image dimensions prevent layout shifts')
        url = attrs.get('href') if tag in ('a','link') else attrs.get('src')
        if not url:
            continue
        parsed = urlsplit(url)
        if parsed.scheme:
            require(parsed.scheme in ('https','mailto'), f'allowed URL scheme: {url}')
            if parsed.scheme == 'mailto':
                require(parsed.path == 'mycatapps@gmail.com', 'correct public mailbox')
            continue
        require(not parsed.path.startswith('/'), f'project-site relative path: {url}')
        target = ROOT / unquote(parsed.path or name)
        require(target.is_file(), f'local target exists: {url}')
        if parsed.fragment and target.suffix == '.html' and target.name in pages:
            require(unquote(parsed.fragment) in pages[target.name].ids, f'fragment exists: {url}')

css = (ROOT/'site.css').read_text()
for path in re.findall(r'url\([\'\"]?([^\)\'\"]+)',css):
    if not (ROOT/path).is_file():
        errors.append(f'site.css: missing {path}')
for path in ('privacy.html','support.html','delete-account.html','test.html','join.html','guide.html','feedback.html','contribute.html'):
    if path not in pages:
        errors.append(f'missing public/legacy route: {path}')
if 'support-development' not in pages.get('support.html',Page('')).ids:
    errors.append('missing legacy development-support fragment')
if 'test-forms' not in pages.get('privacy.html',Page('')).ids:
    errors.append('missing form privacy fragment')
print(f'{len(pages)} pages checked; {len(errors)} errors')
for error in errors:
    print('ERROR:',error)
sys.exit(bool(errors))
