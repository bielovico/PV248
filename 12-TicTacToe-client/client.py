import sys

host = sys.argv[1]
port = sys.argv[2]

hostname = 'http://' + host + ':' + port

import urllib.request as req
import json

list_req = req.Request(hostname + '/list')

resp = req.urlopen(list_req)

content_length = int(resp.headers['Content-Length'])
content = json.loads(resp.read(content_length).decode('utf-8'))


new_games = []
for g in content:
    if g['moves'] > 0:
        continue
    new_games.append(g)

def print_new_games():
    print('List of games:')
    for g in new_games:
        print('{}: {}'.format(g['id'], g['name']))
    
