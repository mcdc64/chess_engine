from enum import Enum
import pygame
import copy

class Color(Enum):
    BLACK = 0
    WHITE = 1
    NONE = 2

class PieceType(Enum):
    PAWN = 1
    KNIGHT = 2
    BISHOP = 3
    ROOK = 4
    QUEEN = 5
    KING = 6
    EMPTY = 0

class Piece():
    def __init__(self,color,piece_type):

        self.color = color # black or white
        self.piece_type = piece_type # type of piece

    def promote(self,new_type):
        if(self.piece_type == PieceType.PAWN):
            self.piece_type = new_type
        else:
            raise("Cannot promote a non-pawn piece")


class Board():
    def __init__(self,pieces,color_at_bottom=Color.WHITE,color_to_move=Color.WHITE,en_passant=[-1,-1],castling_rights="KQkq",halfmoves = 0,fullmoves = 0):
        self.pieces = pieces
        self.color_to_move = color_to_move # the color whose turn it is
        self.en_passant = en_passant
        self.castling_rights = castling_rights
        self.halfmoves = halfmoves
        self.fullmoves = fullmoves
        self.color_at_bottom = color_at_bottom # color at the bottom of the board
    def move(self,old_position,new_position,en_passant):
        old_x = old_position[0]
        old_y = old_position[1]
        new_x = new_position[0]
        new_y = new_position[1]
        moving_piece = copy.deepcopy(self.pieces[old_x][old_y])
        self.pieces[old_x][old_y] = Piece(Color.NONE,PieceType.EMPTY)
        self.pieces[new_x][new_y] = moving_piece
        if (en_passant and new_y>0):
            self.pieces[new_x][new_y-1] = Piece(Color.NONE,PieceType.EMPTY)



def initialise_pieces(): #initialise the starting position of a chessboard. Return the corresponding piece array
    pieces = [[Piece(Color.NONE, PieceType.EMPTY)] * 8 for i in range(8)]
    for i in range(0,8):
        pieces[i][1] = Piece(Color.WHITE,PieceType.PAWN)
        pieces[i][6] = Piece(Color.BLACK,PieceType.PAWN)
    pieces[0][0] = Piece(Color.WHITE,PieceType.ROOK)
    pieces[7][0] = Piece(Color.WHITE, PieceType.ROOK)
    pieces[0][7] = Piece(Color.BLACK, PieceType.ROOK)
    pieces[7][7] = Piece(Color.BLACK, PieceType.ROOK)

    pieces[1][0] = Piece(Color.WHITE, PieceType.KNIGHT)
    pieces[6][0] = Piece(Color.WHITE, PieceType.KNIGHT)
    pieces[1][7] = Piece(Color.BLACK, PieceType.KNIGHT)
    pieces[6][7] = Piece(Color.BLACK, PieceType.KNIGHT)

    pieces[2][0] = Piece(Color.WHITE, PieceType.BISHOP)
    pieces[5][0] = Piece(Color.WHITE, PieceType.BISHOP)
    pieces[2][7] = Piece(Color.BLACK, PieceType.BISHOP)
    pieces[5][7] = Piece(Color.BLACK, PieceType.BISHOP)

    pieces[3][0] = Piece(Color.WHITE,PieceType.QUEEN)
    pieces[3][7] = Piece(Color.BLACK,PieceType.QUEEN)

    pieces[4][0] = Piece(Color.WHITE,PieceType.KING)
    pieces[4][7] = Piece(Color.BLACK,PieceType.KING)
    return pieces

def import_fen(fen_str): #standardised representation of a chess board using a single string
    #output a board matching the given fen

    fen_parts = fen_str.split(" ")
    color_to_move = Color.NONE
    board_rows = fen_parts[0].split("/")
    pieces = [[Piece(Color.NONE, PieceType.EMPTY)] * 8 for i in range(8)]
    for k in range(0,8):

        j = 7-k # y coord of current row
        curr_row = board_rows[k]
        white_piece_string = " PNBRQK"
        black_piece_string = " pnbrqk"
        print(curr_row)
        index = -1
        board_coord = 0 # x coord to place pieces
        for i in range(0,len(curr_row)): #iterate through chars in the current row (NOT through board positions)
            color = Color.NONE
            character = curr_row[i]

            if (not character.isdigit()):
                if(character.isupper()):
                    index = white_piece_string.index(character)
                    color = color.WHITE
                elif(character.islower()):
                    index = black_piece_string.index(character)
                    color = color.BLACK
                pieces[board_coord][j] = Piece(color,PieceType(index))
                board_coord+=1 #if the last char was a letter, increment the board coordinate by 1
            else:
                num_to_move = int(character)
                board_coord += num_to_move # skip however many squares the number in the fen string tells you to

    if (fen_parts[1]=="b"):
        color_to_move = Color.BLACK
    if(fen_parts[1]=="w"):
        color_to_move = Color.WHITE
    castling_rights = fen_parts[2]
    en_passant_str = fen_parts[3]
    alpha_string = "abcdefgh"
    en_passant_out = [-1,-1] #will output the square where en passant is possible, if it exists
    if not(en_passant_str == "-"):
        x_coord = alpha_string.index(en_passant_str[0]) #first char in the string is the letter of the enpassant square
        y_coord = en_passant_str[1]
        en_passant_out = [x_coord,y_coord]
    halfmoves = fen_parts[4] # no. of halfmoves since last capture or pawn advance. If it gets to 100, there is a draw
    fullmoves = fen_parts[5] # no. of fullmoves since start of game (incremented with every Black move)
    output_board = Board(pieces,Color.WHITE,color_to_move,castling_rights,en_passant_out,halfmoves,fullmoves)
    return output_board