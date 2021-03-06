import numpy as np
from copy import deepcopy
from . import Pieces
# import Pieces


class ChessError(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class ChessBoard:
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    turn = 'W'

    def __init__(self):
        Piece = Pieces.Piece
        Pawn = Pieces.Pawn
        self.chess_fields = {}

        # wrzuć do funkcji tworzenie szachownicy

        for i in range(8):
            for j in range(8):
                self.chess_fields[f'{self.letters[i]}{j + 1}'] = (i, j)

        self.chessboard = np.array(
            [None for _ in range(64)], dtype=Piece).reshape(8, 8)
        for i in range(8):
            self.chessboard[i, 1] = Pawn(i, 1, 'W')

        for i in range(8):
            self.chessboard[i, 6] = Pawn(i, 6, 'B')

        piece_kinds = ['Rook', 'Knight', 'Bishop', 'Queen', 'King']

        for i, piece_kind in enumerate(piece_kinds):
            piece = eval(f'Pieces.{piece_kind}')
            self.chessboard[i, 0] = piece(i, 0, 'W')
            self.chessboard[i, 7] = piece(i, 7, 'B')

            if i < 3:
                self.chessboard[7 - i, 0] = piece(7-i, 0, 'W')
                self.chessboard[7 - i, 7] = piece(7-i, 7, 'B')

            if i == 4:
                self.kings = {
                    'W': self.chessboard[i, 0],
                    'B': self.chessboard[i, 7]
                }
        # ------

    def print_board(self):
        chessboard = np.flip(np.copy(self.chessboard), axis=1).transpose()
        border = f'  {"+---"*8}+'
        for x in range(8):
            print(border)
            print(f'{8 - x} ', end='')
            for y in range(8):
                if chessboard[x, y]:
                    print(f'| {str(chessboard[x, y])} ', end='')
                else:
                    print('|   ', end='')
            print('|')

        print(border)
        print(f'    {"".join([f"{self.letters[i]}   " for i in range(8)])}')

    def get_available_moves(self, piece, enemy_turn=False):
        moves = piece.get_moves(self.chessboard)

        king = deepcopy(self.kings['W' if self.turn == 'B' else 'B']
                        ) if enemy_turn else deepcopy(self.kings[self.turn])

        def filter_check_moves(move):
            chessboard_copy = np.copy(self.chessboard)
            chessboard_copy[move['move']] = piece
            chessboard_copy[piece.get_position()] = None
            if str(piece) in ['k', 'K']:
                king.move(move['move'])

            return not king.is_check(chessboard_copy)

        return list(filter(filter_check_moves, moves))

    def get_player_move_input(self):
        invalid_move = True

        while invalid_move:
            try:
                player_input = input(
                    'Select the piece and place you want to move it (eg. G1 F3).\nType "board" to display board on console: ')

                if player_input == 'board':
                    self.print_board()
                    continue

                player_move = player_input.split(' ')[:2]

                if len(player_move) < 2:
                    raise ChessError(
                        '>Please give two arguments separated by space.')

                if not set(player_move).issubset(self.chess_fields.keys()):
                    raise ChessError(
                        '>First value should be between A and H and second between 1 and 8.')

                piece_coordinates, move = player_move
                piece = self.chessboard[self.chess_fields[piece_coordinates]]
                if not piece or (isinstance(piece, Pieces.Piece) and piece.color != self.turn):
                    raise ChessError('>Please select the piece of Your color.')

                available_moves = self.get_available_moves(piece)
                move = [
                    m for m in available_moves if self.chess_fields[move] == m['move']]
                if not move:
                    raise ChessError('>Illegal move')

                invalid_move = False

            except ChessError as chess_error:
                print(chess_error)

        return piece, move.pop()

    def move_piece(self, piece, move):
        if move['type'] == 'castling-long':
            self.chessboard[piece.x, 2] = piece
            self.chessboard[piece.get_position()] = None
            rook = self.chessboard[piece.x, 0]
            self.chessboard[piece.x, 3] = rook
            self.chessboard[rook.get_position()] = None
            # self.kings[self.turn] = piece

        elif move['type'] == 'castling-short':
            self.chessboard[6, piece.y] = piece
            self.chessboard[piece.get_position()] = None
            piece.move((6, piece.y))
            rook = self.chessboard[7, piece.y]
            self.chessboard[5, piece.y] = rook
            self.chessboard[rook.get_position()] = None
            rook.move((5, piece.y))
            # self.kings[self.turn] = piece

        else:
            self.chessboard[tuple(move['move'])] = piece
            self.chessboard[piece.get_position()] = None
            piece.move(tuple(move['move']))

        if str(piece) == 'K':
            self.kings[self.turn] = piece
        
        self.turn = 'B' if self.turn == 'W' else 'W'

    def get_game_status(self):
        status = {}

        check = False
        enemy_king = self.kings['B' if self.turn == 'W' else 'W']
        if enemy_king.is_check(self.chessboard):
            check = True
        
        status['isCheck'] = check

        end_game = False
        try:
            for row in self.chessboard:
                for field in row:
                    if isinstance(field, Pieces.Piece) and field.color != self.turn:
                        moves = self.get_available_moves(
                            field, enemy_turn=True)
                        if moves:
                            raise ChessError()
            end_game = True
        except ChessError:
            pass
        status['endGame'] = end_game
        if end_game:
            status['winner'] = self.turn if check else 'stalemate'

        return status

    def local_terminal_game(self):
        print('--------------Chess Terminal game--------------')
        while True:
            if self.turn == 'W':
                print('White turn')
            else:
                print('Black turn')

            self.print_board()

            piece, move = self.get_player_move_input()

            if move['type'] == 'castling-long':
                self.chessboard[piece.x, 2] = piece
                self.chessboard[piece.get_position()] = None
                rook = self.chessboard[piece.x, 0]
                self.chessboard[piece.x, 3] = rook
                self.chessboard[rook.get_position()] = None
                self.kings[self.turn] = piece

            elif move['type'] == 'castling-short':
                self.chessboard[6, piece.y] = piece
                self.chessboard[piece.get_position()] = None
                piece.move((6, piece.y))
                rook = self.chessboard[7, piece.y]
                self.chessboard[5, piece.y] = rook
                self.chessboard[rook.get_position()] = None
                rook.move((5, piece.y))
                self.kings[self.turn] = piece

            else:
                # print(move)
                self.chessboard[move['move']] = piece
                self.chessboard[piece.get_position()] = None
                piece.move(move['move'])

            if str(piece) == 'K':
                self.kings[self.turn] = piece

            check = False
            enemy_king = self.kings['B' if self.turn == 'W' else 'W']
            if enemy_king.is_check(self.chessboard):
                print('CHECK!!!')
                check = True

            end_game = False
            try:
                for row in self.chessboard:
                    for field in row:
                        if isinstance(field, Pieces.Piece) and field.color != self.turn:
                            moves = self.get_available_moves(
                                field, enemy_turn=True)
                            if moves:
                                raise ChessError()
                end_game = True
            except ChessError:
                pass

            if end_game:
                if check:
                    print(f'{"White" if self.turn == "W" else "Black"} won!')
                else:
                    print('Stalemate.')
                break

            self.turn = 'B' if self.turn == 'W' else 'W'


if __name__ == '__main__':
    board = ChessBoard()
    board.local_terminal_game()
