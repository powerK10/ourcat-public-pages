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
if not (ROOT/'CNAME').is_file() or (ROOT/'CNAME').read_bytes() != b'ourcat.app\n':
    errors.append('CNAME: expected ourcat.app followed by a single LF')
old_url = b'powerk10.github.io/' + b'ourcat-public-pages'
for path in sorted(ROOT.rglob('*')):
    if '.git' in path.relative_to(ROOT).parts or path == ROOT/'README.md':
        continue
    if path.is_file() and old_url in path.read_bytes():
        errors.append(f'{path.relative_to(ROOT)}: old project URL remains')
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
    require([(h.rsplit('/', 1)[-1], t) for h, t in nav_links] == [('features','What it does'),('test','Try OurCat'),('feedback','Feedback'),('support','Help')], 'header menu is What it does, Try OurCat, Feedback, Help')
    for heading in re.findall(r'<h[1-3][^>]*>([^<]*)</h[1-3]>', source):
        require(not heading.rstrip().endswith('.'), f'heading without a full stop: {heading}')
    for tag, attrs in page.tags:
        if tag == 'meta' and attrs.get('property') == 'og:image':
            local = attrs.get('content', '').split('https://ourcat.app/', 1)[-1]
            require((ROOT / local).is_file(), f'link-preview image exists: {local}')
    if name in ('join.html','guide.html','feedback.html','404.html'):
        require(any(t == 'meta' and a.get('name') == 'robots' and 'noindex' in a.get('content','') for t,a in page.tags), 'private-journey noindex')
    else:
        require(any(t == 'link' and a.get('rel') == 'canonical' for t,a in page.tags), 'public canonical URL')
        expected = 'https://ourcat.app/' + ('' if name == 'index.html' else name[:-len('.html')])
        require([a.get('href') for t,a in page.tags if t == 'link' and a.get('rel') == 'canonical'] == [expected], f'canonical is {expected}')
        og_urls = [a.get('content') for t,a in page.tags if t == 'meta' and a.get('property') == 'og:url']
        require(og_urls in ([], [expected]), f'og:url is {expected}')
    for tag, attrs in page.tags:
        if tag == 'img':
            require('alt' in attrs, 'image alternative')
            require('width' in attrs and 'height' in attrs, 'image dimensions prevent layout shifts')
        url = attrs.get('href') if tag in ('a','link') else attrs.get('src')
        if not url:
            continue
        parsed = urlsplit(url)
        if tag in ('a','link') and (
            not parsed.scheme and not parsed.netloc
            or parsed.scheme in ('http','https') and parsed.hostname == 'ourcat.app'
        ):
            require(not unquote(parsed.path).endswith('.html'), f'clean internal href: {url}')
        if parsed.scheme:
            require(parsed.scheme in ('https','mailto'), f'allowed URL scheme: {url}')
            if parsed.scheme == 'mailto':
                require(parsed.path == 'mycatapps@gmail.com', 'correct public mailbox')
            continue
        require(not parsed.netloc, f'local URL without external host: {url}')
        local = unquote(parsed.path).lstrip('/')
        if parsed.path in ('./', '/'):
            local = 'index.html'
        target = ROOT / (local or ('index.html' if parsed.path else name))
        if parsed.path and not parsed.path.endswith('/') and not target.suffix and not target.is_file():
            html_target = target.with_suffix('.html')
            if html_target.is_file():
                target = html_target
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
# Cross-platform recruitment must not send iOS applicants down the Play-only route.
for name in ('index.html', 'test.html', 'features.html'):
    source = (ROOT/name).read_text(encoding='utf-8')
    for stale in ('working on an iPhone version', 'working on the iPhone version', 'test is Android only', 'It isn’t ready yet'):
        if stale in source:
            errors.append(f'{name}: stale platform claim: {stale}')
    if 'iPhone' not in source or 'Apple' not in source:
        errors.append(f'{name}: missing iOS request availability/gate')
for name in ('index.html', 'test.html'):
    if 'Device%28s%29' not in (ROOT/name).read_text(encoding='utf-8'):
        errors.append(f'{name}: invitation email fallback must ask for platform')
    fallback = (ROOT/name).read_text(encoding='utf-8')
    if 'Google%20Play%20country' not in fallback or 'App%20Store%20country' not in fallback:
        errors.append(f'{name}: email fallback must ask for each store country')
joining = (ROOT/'join.html').read_text(encoding='utf-8')
for section_id in ('android', 'ios'):
    if section_id not in pages['join.html'].ids:
        errors.append(f'join.html: missing {section_id} joining section')
android_section = re.search(r'<section[^>]*id="android"[^>]*>(.*?)</section>', joining, re.S)
if not android_section or '14 days in a row' not in android_section.group(1):
    errors.append('join.html: Google 14-day request must stay inside Android section')
if 'no Google Play account or 14-day opt-in requirement for iPhone/iPad' not in joining:
    errors.append('join.html: iOS joining must distinguish Google requirements')
privacy = (ROOT/'privacy.html').read_text(encoding='utf-8')
if 'Firebase Analytics is not used and crash reporting is off' in privacy or '<p>Crash reporting and its supporting' in privacy:
    errors.append('privacy.html: broad crash-reporting-off wording hides TestFlight collection')
if 'Apple’s TestFlight' not in privacy or 'working tracker' not in privacy:
    errors.append('privacy.html: missing platform testing/private working-copy handling')
expected_preview = 'Free early access, by invitation.'
for name, page in pages.items():
    for tag, attrs in page.tags:
        if tag == 'meta' and attrs.get('property') == 'og:image:alt' and expected_preview not in attrs.get('content', ''):
            errors.append(f'{name}: stale link-preview platform text')
print(f'{len(pages)} pages checked; {len(errors)} errors')
for error in errors:
    print('ERROR:',error)
sys.exit(bool(errors))
