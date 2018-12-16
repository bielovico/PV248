import sys
import http.server
from urllib.parse import urlparse, parse_qs
import json
import asyncio

class TTTGame():
    player_characters = {0: '_', 1: 'x', 2: 'o'}

    def __init__(self, id, name, board_size=3):
        self.id = id
        self.board_size = board_size
        self.board = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.board_T = [[0 for _ in range(board_size)] for _ in range(board_size)]
        self.name = name
        self.next = 1
        self.winner = None
        self.moves = 0
        self.completed = False

    def get_id(self):
        return self.id

    def status(self):
        return {'completed': self.completed, 'winner': self.winner, 'board': self.board, 'next': self.next}

    def play(self, player, x, y):
        if self.completed:
            return False
        if player != self.next:
            return False
        if self.board[x][y] != 0:
            return False
        self.board[x][y] = player
        self.board_T[y][x] = player
        self.moves +=1
        self.next = (player % 2) + 1
        self.check_board()
        return True
    
    def check_row(self, row):
        if sum(row) >= len(row) and row.count(row[0]) == len(row):
            self.completed = True
            self.winner = row[0]
            return True

    def check_board(self):
        for row in self.board:
            if self.check_row(row):
                return True
        for column in self.board_T:
            if self.check_row(column):
                return True
        diag = [d[i] for i, d in enumerate(self.board)]
        if self.check_row(diag):
            return True
        diag = [d[len(self.board)-i-1] for i, d in enumerate(self.board)]
        if self.check_row(diag):
            return True
        if self.moves == len(self.board)**2 and not self.completed:
            self.completed = True
            self.winner = 0
        return self.completed

    def draw_board(self):
        for row in self.board:
            print('|', end='')
            for c in row:
                print(self.player_characters[c] + '|', sep='', end='')
            print()

class TTTServer(http.server.HTTPServer):
    games = {}
    free_id = 0
    board_size = 3

    def start_game(self, name):
        g = TTTGame(self.free_id, name, self.board_size,)
        self.games[self.free_id] = g
        self.free_id += 1
        return g.get_id()

    def play_game(self, id, player, x, y):
        g = self.games.get(id)
        if g is None:
            return None
        return g.play(player, x, y)

    def game_status(self, id):
        g = self.games.get(id)
        if g is None:
            return None
        return g.status()
    
    def list_games(self):
        return [{'id':g.id, 'name':g.name, 'moves':g.moves} for g in self.games.values()]

class TTTHandler(http.server.BaseHTTPRequestHandler):
    headers = {'Content-Type': 'application/json'}

    def set_headers(self, content_len):
        for keyword, value in self.headers.items():
            self.send_header(keyword, value)
        self.send_header('Content-Length', content_len)
        self.end_headers()
    
    def do_HEAD(self):
        pass
    
    def do_POST(self):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        p = parsed.path
        output = {}
        if p == '/start':
            self.send_response(200)
            name = parse_qs(parsed.query).get('name')
            if name is None:
                output['id'] = self.server.start_game('')
            else:
                output['id'] = self.server.start_game(name[0])
        elif p == '/play':
            params = parse_qs(parsed.query)
            game = params.get('game')
            player = params.get('player')
            x = params.get('x')
            y = params.get('y')
            if game is None or player is None or x is None or y is None:
                self.send_error(401, 'Missing input')
                return
            try:
                game = int(game[0])
                player = int(player[0])
                x = int(x[0])
                y = int(y[0])
            except ValueError:
                self.send_error(402, 'Non-integral input')
                return
            played = self.server.play_game(game, player, x, y)
            if played is None:
                self.send_error(403, 'Wrong game ID')
                return
            self.send_response(200)
            if not played:
                output['status'] = 'bad'
                output['message'] = 'Could not play this move. Check the /status?game={}.'.format(game)
            else:
                output['status'] = 'ok'
        elif p == '/status':
            game = parse_qs(parsed.query).get('game')
            if game is None:
                self.send_error(401, 'Missing input')
                return
            try:
                game = int(game[0])
            except ValueError:
                self.send_error(402, 'Non-integral input')
                return
            self.send_response(200)
            status = self.server.game_status(game)
            if status is None:
                self.send_error(403, 'Wrong game ID')
                return
            if status['completed']:
                output['winner'] = status['winner']
            else:
                output['board'] = status['board']
                output['next'] = status['next']
        elif p == '/list':
            self.send_response(200)
            output = self.server.list_games()
        else:
            self.send_error(404, 'Command not found')
            return
        output = bytes(json.dumps(output), encoding='UTF-8')
        self.set_headers(len(output))
        self.wfile.write(output)

def run(server_class=http.server.HTTPServer, handler_class=http.server.BaseHTTPRequestHandler):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

def main():
    port = int(sys.argv[1])
    run(server_class=TTTServer, handler_class=TTTHandler)

if __name__ == '__main__':
    main()