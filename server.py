import socket
import threading
import queue
import json
import dotenv

# Wrzuć to do env-ów
HEADER = 64
PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
ADDR = (HOST, PORT)
FORMAT = 'utf-8'
AWAITING = '!AWAITING'
TURN = '!TURN'
DISCONNECT_MESSAGE = '!DISCONNECT'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

game_queue = queue.Queue(100)


def handle_game(player1, player2):
    connected = True

    turn, awaiting = player1, player2
    while connected:
        awaiting[0].send(AWAITING.encode(FORMAT))

        turn[0].send(TURN.encode(FORMAT))
        move = turn[0].recv(2048).decode(FORMAT)
        print(f'{turn[1]}: {move}')

        turn, awaiting = awaiting, turn


def start():
    server.listen()
    print(f'[ LISTENING ] Server is listening on {HOST}:{PORT}')
    while True:
        conn, addr = server.accept()
        game_queue.put((conn, addr))

        if game_queue.qsize() >= 2:
            player1 = game_queue.get()
            player2 = game_queue.get()

            thread = threading.Thread(target=handle_game, args=(player1, player2))
            thread.start()


print("[ STARTING ] Server is starting...")
start()


#
# Front -> Django 
#
#
# Front (gry) -> server socket