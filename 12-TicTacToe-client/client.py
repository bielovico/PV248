import sys
import urllib.request as req
import json
from ttt import TTTGame
from time import sleep

class TTTClient():
    def __init__(self, hostname):
        self.hostname = hostname
        self.list_req = req.Request(hostname + '/list')
        self.start_req = req.Request(hostname + '/start')
        self.games = {}
        self.current = None
        self.player = None
        self.opponent = None
        self.charmap = TTTGame.player_characters

    def parse_request(self, request):
        resp = req.urlopen(request)
        content_length = int(resp.headers['Content-Length'])
        content = json.loads(resp.read(content_length).decode('utf-8'))
        return content

    def get_games_list(self):
        content = self.parse_request(self.list_req)
        for g in content:
            if g['moves'] == 0:
                self.games[g['id']] = TTTGame(g['id'], g['name'])

    def print_games(self):
        print('List of games:')
        for i, g in self.games.items():
            print('{} {}'.format(i, g.name))

    def check_remote_status(self):
        status_req = req.Request(hostname + '/status?game=' + str(self.current.id))
        content = self.parse_request(status_req)
        if self.current.board != content.get('board'):
            print('status changed unexpectedly. Closing the game.')
            return False

    def start(self):
        self.print_games()
        print('Choose a game (or type "new" for a new game): ', end='')
        chosen = input()
        while not self.valid_game(chosen):
            print('Please input valid game ID or "new": ', end='')
            chosen = input()
        if chosen == 'new':
            # print('You want to start a new game.')
            content = self.parse_request(self.start_req)
            i = content['id']
            g = TTTGame(i, '')
            self.games[i] = g
            self.current = g
            self.player = 1
            self.opponent = 2
            print('Received a new game id: {}. You are a player 1.'\
                    .format(self.current.id))
        else:
            self.current = self.games[int(chosen)]
            self.player = 2
            self.opponent = 1
            print('You`ve chosen to play a game: {} ({}). You are a player 2.'\
                    .format(self.current.name, self.current.id))
        self.current.draw_board()

    def valid_game(self, chosen):
        if chosen == 'new':
            return True
        else:
            try:
                chosen = int(chosen)
            except ValueError:
                print('Invalid input')
                return False
            if chosen not in self.games.keys():
                print('Id is not a valid game.')
                return False
            else:
                return True

    def valid_coords(self, coords):
        coords = coords.split(' ')
        if len(coords) != 2:
            return False
        try:
            x = int(coords[0])
            y = int(coords[1])
        except ValueError:
            return False
        if y<0 or x<0 or y>=self.current.board_size or x>=self.current.board_size:
            return False
        if self.current.board[y][x] != 0:
            return False
        return True     

    def resolve_move(self, board):
        changes = []
        for y in range(self.current.board_size):
            for x in range(self.current.board_size):
                if board[y][x] != self.current.board[y][x]:
                    changes.append((x,y))
        return changes

    def serve_game(self):
        self.check_remote_status()
        while not self.current.completed:
            if self.current.next == self.player:
                print('your turn ({}):'.format(self.charmap[self.player]))
                coords = input()
                while not self.valid_coords(coords):
                    print('invalid input')
                    coords = input()
                coords = coords.split(' ')
                x = int(coords[0])
                y = int(coords[1])
                move_req = req.Request('{}/play?game={}&player={}&x={}&y={}'.format(self.hostname, self.current.id, self.player, x, y))
                content = self.parse_request(move_req)
                if content['status'] == 'bad':
                    print(content['message'])
                    # print('invalid input')
                    return
                else:
                    self.current.play(self.player, x, y)
                    self.check_remote_status()
                    self.current.draw_board()
                    if self.current.completed:
                        if self.current.winner == self.player:
                            print('you win')
                        elif self.current.winner == 0:
                            print('draw')
                        else:
                            print('you lose')
                        return True
                    continue
            else:
                print('waiting for the other player')
                status_req = req.Request('{}/status?game={}'.format(self.hostname, self.current.id))
                content = self.parse_request(status_req)
                while content.get('next') != self.player:
                    if content.get('winner') is not None:
                        self.current.board = content['board']
                        self.current.draw_board()
                        if content.get('winner') == self.player:
                            print('you win')
                        elif content.get('winner') == 0:
                            print('draw')
                        else:
                            print('you lose')
                        return True
                    sleep(1)
                    content = self.parse_request(status_req)
                changes = self.resolve_move(content['board'])
                if len(changes) > 1:
                    return False
                self.current.play(self.opponent, changes[0][0], changes[0][1])
                self.check_remote_status()
                self.current.draw_board()


if __name__ == "__main__":
    host = sys.argv[1]
    port = sys.argv[2]
    hostname = 'http://' + host + ':' + port

    client = TTTClient(hostname)
    client.get_games_list()
    client.start()
    client.serve_game()
