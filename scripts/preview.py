"""Preview the static site with clean URLs. Run with Python 3."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]


class PreviewHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):
        translated = super().translate_path(path)
        target = Path(translated)
        if not urlsplit(path).path.endswith('/') and not target.suffix and not target.is_file():
            html_target = target.with_suffix('.html')
            if html_target.is_file():
                return str(html_target)
        return translated

    def send_error(self, code, message=None, explain=None):
        if code != 404:
            return super().send_error(code, message, explain)
        try:
            body = (ROOT / '404.html').read_bytes()
        except OSError:
            return super().send_error(code, message, explain)
        self.send_response(404)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        if self.command != 'HEAD':
            self.wfile.write(body)


if __name__ == '__main__':
    handler = partial(PreviewHandler, directory=str(ROOT))
    with ThreadingHTTPServer(('127.0.0.1', 8769), handler) as server:
        print('Preview: http://127.0.0.1:8769/ (Ctrl+C to stop)')
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
