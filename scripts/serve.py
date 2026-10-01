#!/usr/bin/env python3
"""Serve the staged site locally, including the real 404 invite fallback. Ctrl+C stops it."""
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class Handler(SimpleHTTPRequestHandler):
    def guess_type(self,path):
        if path.endswith('apple-app-site-association'):return 'application/json'
        return super().guess_type(path)
    def send_error(self,code,message=None,explain=None):
        if code==404 and (Path(self.directory)/'404.html').is_file():
            content=(Path(self.directory)/'404.html').read_bytes()
            self.send_response(404);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Length',str(len(content)));self.end_headers()
            if self.command!='HEAD':self.wfile.write(content)
        else:super().send_error(code,message,explain)

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--port',type=int,default=8765);args=ap.parse_args()
    if not (ROOT/'dist/index.html').exists():raise SystemExit('Run build-site.py and stage-site.py first.')
    server=ThreadingHTTPServer(('127.0.0.1',args.port),partial(Handler,directory=str(ROOT/'dist')))
    print(f'ReadyKin preview: http://127.0.0.1:{args.port}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close()
if __name__=='__main__':main()
