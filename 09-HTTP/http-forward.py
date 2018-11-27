import sys

port = int(sys.argv[1])
upstream = sys.argv[2]
upstream = 'http://' + upstream + '/'

import http.server
import urllib.request as req
import json

timeout = 1

class ForwarderHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        request = req.Request(upstream, headers={'Accept-Encoding': 'identity', 'Accept-Charset': 'utf-8'})
        resp = req.urlopen(request, timeout=timeout)
        self.send_response(200, 'OK')
        for keyword, value in resp.getheaders():
            self.send_header(keyword, value)
        self.end_headers()
        output = {'code': resp.getcode(), 'headers': dict(resp.getheaders())}
        content = resp.read().decode('UTF-8')
        try:
            json.loads(content)
            output['json'] = content
        except ValueError:
            output['content'] = content
        self.wfile.write(bytes(json.dumps(output), encoding='UTF-8'))

    def do_POST(self):
        content = self.rfile.read().decode('utf-8')
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
        headers = params.get('headers')
        if headers is None:
            headers = {'Content-Type': 'text/html; charset=UTF-8'}
        content = params.get('content')
        if (typ == 'POST') and (content is None):
            code = 'invalid json'
        timeout = params.get('timeout')
        if timeout is None:
            timeout = 1
        if code is not None:
            self.send_response(201, code)
            self.send_header('Content-Type', 'text/html; charset=UTF-8')
            self.end_headers()
            self.wfile.write(bytes(json.dumps({'code':code}), encoding='UTF-8'))
            return
        data = bytes(content, encoding='UTF-8')
        request = req.Request(url, headers=headers, method=typ, data=data)
        resp = req.urlopen(request, timeout=timeout)
        self.send_response(200, 'OK')
        for keyword, value in resp.getheaders():
            self.send_header(keyword, value)
        self.end_headers()
        output = {'code': resp.getcode(), 'headers': dict(resp.getheaders())}
        content = resp.read().decode('UTF-8')
        try:
            json.loads(content)
            output['json'] = content
        except ValueError:
            output['content'] = content
        self.wfile.write(bytes(json.dumps(output), encoding='UTF-8'))

class ForwarderServer(http.server.HTTPServer):
    pass

def run(server_class=http.server.HTTPServer, handler_class=http.server.BaseHTTPRequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def main():
    run(handler_class=ForwarderHandler)

if __name__ == '__main__':
    main()


