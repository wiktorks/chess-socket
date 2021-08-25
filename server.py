import asyncio
import random
import json

from game_logic.Chessboard import ChessBoard, ChessError
from player import Player

# Wrzuć to do env-ów
# Tego typu argumenty lepiej przesyłać do funkcji
# HEADER = 64
# PORT = 5050
# HOST = socket.gethostbyname(socket.gethostname())
# ADDR = (HOST, PORT)
# FORMAT = 'utf-8'
# AWAITING = '!AWAITING'
# TURN = '!TURN'
# DISCONNECT_MESSAGE = '!DISCONNECT'

# server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server.bind(ADDR)


# player_move = {
#     'type': 'move',
#     'piece': [3, 1],
#     'move': [3, 3],
#     'color': 'W/B',
#     'isCheck': False # True
# }

# Stwórz singletona z klasy Server!!!

class Server:
    header = 64
    game_queue = []

    def __init__(self, address, port, str_format='utf-8'):
        self.address = address
        self.port = port
        self.format = str_format

    async def handle_game(self, player1, player2):
        game = ChessBoard()
        moving, awaiting = (player1, player2) if player1.color == 'W' else (
            player2, player1)
        await moving.send({
            'type': 'game_start',
            'assigned_color': moving.color,
            'enemy_player': awaiting.name
        })
        await awaiting.send({
            'type': 'game_start',
            'assigned_color': awaiting.color,
            'enemy_player': moving.name
        })
        playing = True
        while playing:
            move = await moving.receive()
            await awaiting.send({
                'type': 'move',
                'move': move
            })
            moving, awaiting = (awaiting, moving)
# cors -> do bezpiecznego dzielenia się zasobami
# endpoint -> permission robisz socket server i wrzucasz w payload
# Self signed certificate

    async def handle_player(self, reader, writer):
        message = await reader.read(200)
        message = message.decode(self.format)
        player_data = json.loads(message)

        if 'name' not in player_data.keys():
            raise KeyError('Wrong connect message from player')

        writer.write(json.dumps({
            'type': 'search_game',
            'status': 'success',
            'message': 'searching for player'
        }).encode(self.format))
        await writer.drain()

        player = Player(
            player_data['name'],
            reader,
            writer
        )
# Global interpreter lock (GIL) w Pythonie
        queue_lock = asyncio.Lock()
        async with queue_lock:
            self.game_queue.append(player)

            if len(self.game_queue) >= 2:
                player_color = random.choice(['W', 'B'])
                player1 = self.game_queue.pop()
                player1.assign_color(player_color)
                player2 = self.game_queue.pop()
                player2.assign_color('W' if player_color == 'B' else 'B')
                asyncio.create_task(self.handle_game(player1, player2))

    async def start(self):
        server = await asyncio.start_server(self.handle_player, self.address, self.port)
        assigned_address = server.sockets[0].getsockname()
        print(
            f'[ RUNNING ] Server is running on {assigned_address}:{self.port}')

        async with server:
            await server.serve_forever()


def main():
    server = Server('127.0.0.1', 5050)
    asyncio.run(server.start())


main()
# dobrze dać header z długością wiadomości jako pierwsza wiadomość

# tab nine -> dodatek do pythona, kite


#
# Front -> Django
#
#
# Front (gry) -> server socket
