#!/usr/bin/env python3
"""3D Office Dashboard Server"""
import http.server
import socketserver
import os
from pathlib import Path
from urllib.parse import urlparse

PORT = 9502
DIRECTORY = Path(__file__).parent

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ('', '/'):
            self.path = '/office.html' + ('?' + parsed.query if parsed.query else '')
        return super().do_GET()
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"3D Office Dashboard running at http://0.0.0.0:{PORT}")
        print(f"Mesh-VPN URL: http://100.66.142.21:{PORT}")
        httpd.serve_forever()