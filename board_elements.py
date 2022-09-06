from enum import Enum
import numpy as np
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
    def __init__(self,pieces,color_at_bottom=Color.WHITE,color_to_move=Color.WHITE,castling_rights="KQkq",en_passant=[-1,-1],halfmoves = 0,fullmoves = 1):
        self.pieces = pieces
        self.color_to_move = color_to_move # the color whose turn it is
        self.en_passant = en_passant
        self.castling_rights = castling_rights
        self.halfmoves = halfmoves
        self.fullmoves = fullmoves
        self.color_at_bottom = color_at_bottom # color at the bottom of the board
    def move(self,old_position,new_position): # move a piece from one position to another
        old_x = old_position[0]
        old_y = old_position[1]
        new_x = new_position[0]
        new_y = new_position[1]
        moving_piece = copy.deepcopy(self.pieces[old_x][old_y])
        new_piece = copy.deepcopy(self.pieces[new_x][new_y])
        # handle the four different castling possibilities
        castling = self.move_castle(old_position,new_position)
        if(castling): #if a move results from calling move_castle, end the function there
            if (moving_piece.color == Color.BLACK):
                self.fullmoves += 1
                self.color_to_move = Color.WHITE
            else:
                self.color_to_move = Color.BLACK
            return True



        if (moving_piece.piece_type == PieceType.PAWN and np.abs(new_x-old_x)==1 and np.abs(new_y-old_y)==1 and new_position == self.en_passant):
            # if en passant is possible, allow a pawn to execute it (just need to remove the pawn that moved 2 spaces)

            if(moving_piece.color == Color.WHITE):
                self.pieces[self.en_passant[0]][self.en_passant[1]-1] = Piece(Color.NONE,PieceType.EMPTY)
            if(moving_piece.color == Color.BLACK):
                self.pieces[self.en_passant[0]][self.en_passant[1]+1] = Piece(Color.NONE,PieceType.EMPTY)

        if (moving_piece.piece_type==PieceType.PAWN and np.abs(new_y-old_y)==2): # if the move is a pawn moving 2 spaces, set en passant square
            if(moving_piece.color == Color.WHITE):
                self.en_passant = [old_x,old_y+1]
            elif(moving_piece.color == Color.BLACK):
                self.en_passant = [old_x,old_y-1]
        else:
            self.en_passant = [-1,-1]

        self.pieces[old_x][old_y] = Piece(Color.NONE,PieceType.EMPTY)
        self.pieces[new_x][new_y] = moving_piece

        #update board elements based on move characteristics
        if(new_piece.piece_type != PieceType.EMPTY or moving_piece.piece_type == PieceType.PAWN):
            #either of the above conditions revert the number of halfmoves to 0
            self.halfmoves = 0
        else:
            self.halfmoves += 1
        if(moving_piece.color == Color.BLACK):
            self.fullmoves += 1
            self.color_to_move = Color.WHITE
        elif(moving_piece.color == Color.WHITE):
            self.color_to_move = Color.BLACK

    def move_castle(self,old_position,new_position):
        # Handles castling possibilities when the "move" method is called.
        # Castles if the move represents one
        # Does NOT prevent an attempted castle if it is not allowed (the future "is_pseudo_legal" method should do that)
        old_x,old_y = old_position
        new_x,new_y = new_position
        moving_piece = copy.deepcopy(self.pieces[old_x][old_y])
        new_piece = copy.deepcopy(self.pieces[new_x][new_y])

        output = False
        if (moving_piece.piece_type == PieceType.KING and old_position == [4, 0] and (new_position == [6, 0] or new_position == [7, 0])):
            self.pieces[4][0] = Piece(Color.NONE, PieceType.EMPTY)
            self.pieces[5][0] = Piece(Color.WHITE,PieceType.ROOK)
            self.pieces[6][0] = Piece(Color.WHITE,PieceType.KING)
            self.pieces[7][0] = Piece(Color.NONE,PieceType.EMPTY)
            output = True
        elif (moving_piece.piece_type == PieceType.KING and old_position == [4, 0] and (new_position == [0, 0] or new_position == [1, 0] or new_position == [2,0])):
            self.pieces[0][0] = Piece(Color.NONE, PieceType.EMPTY)
            self.pieces[1][0] = Piece(Color.WHITE,PieceType.EMPTY)
            self.pieces[2][0] = Piece(Color.WHITE,PieceType.KING)
            self.pieces[3][0] = Piece(Color.WHITE,PieceType.ROOK)
            self.pieces[4][0] = Piece(Color.NONE, PieceType.EMPTY)
            output = True
        elif (moving_piece.piece_type == PieceType.KING and old_position == [4, 7] and (new_position == [6, 7] or new_position == [7, 7])):
            self.pieces[4][7] = Piece(Color.NONE, PieceType.EMPTY)
            self.pieces[5][7] = Piece(Color.BLACK,PieceType.ROOK)
            self.pieces[6][7] = Piece(Color.BLACK,PieceType.KING)
            self.pieces[7][7] = Piece(Color.NONE,PieceType.EMPTY)
            output = True
        elif (moving_piece.piece_type == PieceType.KING and old_position == [4, 7] and (new_position == [0, 7] or new_position == [1, 7] or new_position == [2,7])):
            self.pieces[0][7] = Piece(Color.NONE, PieceType.EMPTY)
            self.pieces[1][7] = Piece(Color.NONE,PieceType.EMPTY)
            self.pieces[2][7] = Piece(Color.BLACK,PieceType.KING)
            self.pieces[3][7] = Piece(Color.BLACK,PieceType.ROOK)
            self.pieces[4][7] = Piece(Color.NONE, PieceType.EMPTY)
            output = True

        # check if the white king has moved from its starting spot
        if((self.pieces[4][0].piece_type != PieceType.KING)or(self.pieces[4][0].color != Color.WHITE)):
            self.castling_rights = self.castling_rights.replace("K","")
            self.castling_rights = self.castling_rights.replace("Q", "")
        # Repeat for the two white rooks, and their black counterparts
        if(self.pieces[7][0].piece_type != PieceType.ROOK or(self.pieces[7][0].color != Color.WHITE)):
            self.castling_rights = self.castling_rights.replace("K","")
        if (self.pieces[0][0].piece_type != PieceType.ROOK or (self.pieces[0][0].color != Color.WHITE)):
            self.castling_rights = self.castling_rights.replace("Q", "")
        # Black king and rooks
        if((self.pieces[4][7].piece_type != PieceType.KING)or(self.pieces[4][7].color != Color.BLACK)):
            self.castling_rights = self.castling_rights.replace("k","")
            self.castling_rights = self.castling_rights.replace("q", "")

        if(self.pieces[7][7].piece_type != PieceType.ROOK or(self.pieces[7][7].color != Color.BLACK)):
            self.castling_rights = self.castling_rights.replace("k","")
        if (self.pieces[0][7].piece_type != PieceType.ROOK or (self.pieces[0][7].color != Color.BLACK)):
            self.castling_rights = self.castling_rights.replace("q", "")
        if(self.castling_rights == ""): # if all castling rights are removed, make the string a hyphen
            self.castling_rights = "-"
        return output

    def promote(self,promoting_position,new_piece_type):
        piece_to_promote = self.pieces[promoting_position[0]][promoting_position[1]]

        color = piece_to_promote.color
        self.pieces[promoting_position[0]][promoting_position[1]] = Piece(color,new_piece_type)

    def castle_str(self,old_position,new_position):

        old_x,old_y = old_position
        new_x,new_y = new_position
        moving_piece = copy.deepcopy(self.pieces[old_x][old_y])
        new_piece = copy.deepcopy(self.pieces[new_x][new_y])
        if (moving_piece.piece_type == PieceType.KING and old_position == [4, 0] and (new_position == [6, 0] or new_position == [7, 0])):
            return "O-O"
        elif (moving_piece.piece_type == PieceType.KING and old_position == [4, 0] and (new_position == [0, 0] or new_position == [1, 0] or new_position == [2,0])):
            return "O-O-O"
        if (moving_piece.piece_type == PieceType.KING and old_position == [4, 7] and (new_position == [6, 7] or new_position == [7, 7])):
            return "O-O"
        elif (moving_piece.piece_type == PieceType.KING and old_position == [4, 7] and (new_position == [0, 7] or new_position == [1, 7] or new_position == [2,7])):
            return "O-O-O"
        return "No Move"

    def move_string(self,old_position,new_position,en_passant = False,promote_choice = PieceType.EMPTY):
        # return the string corresponding to a given move
        # does not currently deal with ambiguities (e.g. two rooks on the same rank or file)
        castling = self.castle_str(old_position,new_position)
        if(castling !="No Move"):
            return castling
        move_str = ""
        old_piece = self.pieces[old_position[0]][old_position[1]]
        nums = [0,1,2,3,4,5,6]
        strs = ["","","N","B","R","Q","K"]
        move_str+= strs[old_piece.piece_type.value]
        letters = "abcdefgh"

        new_piece = self.pieces[new_position[0]][new_position[1]]
        if(new_piece.piece_type!=PieceType.EMPTY or en_passant):
            if (old_piece.piece_type == PieceType.PAWN):
                move_str += letters[old_position[0]]
            move_str+="x"
        letters = "abcdefgh"
        move_str+=(letters[new_position[0]])

        move_str+=(str(new_position[1]+1))
        if(promote_choice != PieceType.EMPTY):
            if(promote_choice ==PieceType.QUEEN):
                move_str += "=Q"
            if(promote_choice ==PieceType.ROOK):
                move_str += "=R"
            if(promote_choice ==PieceType.BISHOP):
                move_str += "=B"
            if(promote_choice ==PieceType.KNIGHT):
                move_str += "=N"
        return move_str



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

        index = -1
        board_coord = 0 # x coord to place pieces
        for i in range(0,len(curr_row)): #iterate through chars in the current row (NOT through board positions)
            color = Color.NONE
            character = curr_row[i]

            if (not character.isdigit()):
                if(character.isupper()):
                    index = white_piece_string.index(character)
                    color = Color.WHITE
                elif(character.islower()):
                    index = black_piece_string.index(character)
                    color = Color.BLACK
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
    if(en_passant_str == "-"):
        en_passant_out = [-1,-1] # will output the square where en passant is possible, if it exists
    else:
        idx = alpha_string.index(en_passant_str[0]) # get numerical rank of en passant square
        y_val = int(en_passant_str[1])-1 #file of en passant square
        en_passant_out = [idx,y_val]
    if not(en_passant_str == "-"):
        x_coord = alpha_string.index(en_passant_str[0]) #first char in the string is the rank of the enpassant square
        y_coord = int(en_passant_str[1])-1
        en_passant_out = [x_coord,y_coord]
    halfmoves = int(fen_parts[4]) # no. of halfmoves since last capture or pawn advance. If it gets to 100, there is a draw
    fullmoves = int(fen_parts[5]) # no. of fullmoves since start of game (incremented with every Black move)
    output_board = Board(pieces,Color.WHITE,color_to_move,castling_rights,en_passant_out,halfmoves,fullmoves)
    return output_board

def generate_fen(board):
    row_strs = []
    white_piece_string = " PNBRQK"
    black_piece_string = " pnbrqk"
    for i in range(0,8):
        inv_i = 7-i
        curr_row = [col[inv_i] for col in board.pieces]
        piece_char_arr = []
        empty_count = 0
        for j in range(0,8):
            curr_piece = curr_row[j]
            if(curr_piece.piece_type != PieceType.EMPTY):
                if(empty_count > 0):
                    piece_char_arr.append(str(empty_count))
                    empty_count = 0
                if(curr_piece.color == Color.WHITE):
                    piece_char_arr.append(white_piece_string[curr_piece.piece_type.value])
                elif(curr_piece.color == Color.BLACK):
                    piece_char_arr.append(black_piece_string[curr_piece.piece_type.value])
            else:
                empty_count += 1
            if(j == 7 and empty_count>0):
                piece_char_arr.append(str(empty_count))

        row_strs.append("".join(piece_char_arr))
    position_str = "/".join(row_strs)
    who_str = "w"
    if(board.color_to_move == Color.BLACK):
        who_str = "b"
    castling_str = board.castling_rights

    alpha_string = "abcdefgh"
    en_passant_arr = board.en_passant
    en_passant_str = "-"
    if(board.en_passant != [-1,-1]):
        en_passant_str = alpha_string[board.en_passant[0]]+str(board.en_passant[1]+1)
    halfmoves_str = str(board.halfmoves)
    fullmoves_str = str(board.fullmoves)
    output_str = " ".join([position_str,who_str,castling_str,en_passant_str,halfmoves_str,fullmoves_str])
    return output_str
