import sys

port = int(sys.argv[1])

import http.server
from urllib.parse import urlparse, parse_qs
import json
import asyncio


class TTTGame():
    

class TTTHandler(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        pass
    
    def do_POST(self):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        p = parsed.path
        if p == '/start':
            name = parse_qs(parsed.query).get('name')[0]
            print(name)
        self.send_response(200, 'OK')
        headers = {'Content-Type': 'application/json'}
        for keyword, value in headers.items():
            self.send_header(keyword, value)
        self.end_headers()
        self.wfile.write(bytes(json.dumps({}), encoding='UTF-8'))

def run(server_class=http.server.HTTPServer, handler_class=http.server.BaseHTTPRequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def main():
    run(handler_class=TTTHandler)

if __name__ == '__main__':
    main()