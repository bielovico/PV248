import sys
import http.server
import urllib.request as req
from urllib.error import URLError
import json

class ForwarderHandler(http.server.BaseHTTPRequestHandler):
    def write_forwarded(self, request, timeout=1):
        try:
            resp = req.urlopen(request, timeout=timeout)
            code = resp.getcode()
            headers = dict(resp.getheaders())
            content = resp.read().decode('UTF-8')
        except (http.server.socket.timeout, URLError):
            code = 'timeout'
            headers = {'Content-Type': 'application/json'}
            content = ''
        self.send_response(200, 'OK')
        for keyword, value in headers.items():
            self.send_header(keyword, value)
        self.end_headers()
        output = {'code': code, 'headers': headers}
        try:
            j = json.loads(content)
            output['json'] = j
        except ValueError:
            output['content'] = content
        written = self.wfile.write(bytes(json.dumps(output), encoding='UTF-8'))

    def do_GET(self):
        print('GET request')
        request = req.Request(url = self.server.upstream)
        self.write_forwarded(request)

    def do_POST(self):
        print('POST request')
        content_length = int(self.headers['Content-Length'])
        content = self.rfile.read(content_length).decode('utf-8')
        code = None
        try:
            params = json.loads(content)
        except ValueError:
            code = 'invalid json'
            params = {}
        typ = params.get('type')
        if typ is None:
            typ = 'GET'
        url = params.get('url')
        if url is None:
            code = 'invalid json'
        content = params.get('content')
        if content is None:
            if typ == 'POST':
                code = 'invalid json'
            else:
                content = ''
        headers = params.get('headers')
        if headers is None:
            headers = {'Content-Type': 'application/json', 'Content-Length': len(content)}
        timeout = params.get('timeout')
        if timeout is None:
            timeout = 1
        if code is not None:
            data = bytes(json.dumps({'code':code}), encoding='UTF-8')
            self.send_response(200, 'OK')
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', len(data))
            self.end_headers()
            self.wfile.write(data)
            return
        data = bytes(content, encoding='UTF-8')
        request = req.Request(url, headers=headers, method=typ, data=data)
        self.write_forwarded(request, timeout)

class ForwarderServer(http.server.HTTPServer):
    def set_upstream(self, upstream):
        self.upstream = upstream

def run(port, upstream, server_class=http.server.HTTPServer, handler_class=http.server.BaseHTTPRequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.set_upstream(upstream)
    print('HTTP server starting.')
    httpd.serve_forever()

def main():
    port = int(sys.argv[1])
    upstream = sys.argv[2]
    upstream = 'http://' + upstream + '/'

    run(port, upstream, server_class=ForwarderServer, handler_class=ForwarderHandler)

if __name__ == '__main__':
    main()


