import socket
from game_logic.Chessboard import ChessBoard

# pyenv -> zarządzanie wersjami pythona
# asyncio

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = '!DISCONNECT'
SERVER = '127.0.1.1'
ADDR = (SERVER, PORT)
AWAITING = '!AWAITING'
TURN = '!TURN'
'''
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)

playing = True

while playing:
    message = client.recv(2048).decode(FORMAT)
    if message == TURN:
        move = input('Podaj swój ruch na szachownicy: ')
        move = move.encode(FORMAT)
        client.send(move)
    elif message == AWAITING:
        print('Oczekiwanie na ruch przeciwnika...')
        pass
'''
board = ChessBoard()
board.print_board()