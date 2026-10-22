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
    nav = re.search(r'<nav aria-label="Main navigation">(.*?)</nav>', source)
    nav_links = re.findall(r'href="([^"]+)"[^>]*>([^<]+)</a>', nav.group(1)) if nav else []
    require([(h.rsplit('/', 1)[-1], t) for h, t in nav_links] == [('test.html','Try OurCat'),('feedback.html','Feedback'),('support.html','Help')], 'header menu is Try OurCat, Feedback, Help')
    for heading in re.findall(r'<h[1-3][^>]*>([^<]*)</h[1-3]>', source):
        require(not heading.rstrip().endswith('.'), f'heading without a full stop: {heading}')
    for tag, attrs in page.tags:
        if tag == 'meta' and attrs.get('property') == 'og:image':
            local = attrs.get('content', '').split('/ourcat-public-pages/', 1)[-1]
            require((ROOT / local).is_file(), f'link-preview image exists: {local}')
    if name in ('join.html','guide.html','feedback.html','404.html'):
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
if 'temporary-carers' not in pages.get('privacy.html',Page('')).ids:
    errors.append('missing temporary-carer privacy fragment')
try:
    from PIL import Image
except ImportError:
    print('Pillow not installed: photo metadata check skipped')
else:
    for photo in sorted((ROOT/'assets').glob('*.jpg')):
        with Image.open(photo) as image:
            if image.getexif() or image.info.get('exif'):
                errors.append(f'{photo.name}: remove embedded metadata (EXIF/location)')
    with Image.open(ROOT/'assets'/'share.png') as image:
        if image.size != (1200, 630):
            errors.append(f'share.png: expected 1200x630, found {image.size}')
print(f'{len(pages)} pages checked; {len(errors)} errors')
for error in errors:
    print('ERROR:',error)
sys.exit(bool(errors))
