from enum import Enum
import numpy as np
import copy

from simple_board import SimpleBoard



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

class Move():
    def __init__(self,old_position,new_position,promote_piece = PieceType.EMPTY):
        # only the first three fields are required to make the move on the board
        # the others are needed to undo a move properly (important for legal move generation)
        self.old_position = old_position
        self.new_position = new_position
        self.promote_piece = promote_piece
        self.is_capture = False
        self.captured_piece = Piece(Color.NONE,PieceType.EMPTY)
        self.is_promotion = False
        if(promote_piece != PieceType.EMPTY):
            self.is_promotion = True
        self.is_castle = False
        self.removed_castling_rights = ""
        self.is_en_passant = False
        self.prev_en_passant = [-1,-1] #en passant state of the board BEFORE the move is executed
    def print_stats(self):
        print("Old Position: "+str(self.old_position))
        print("New Position: " + str(self.new_position))
        print("Is Promotion: "+str(self.is_promotion))
        print("Promote Piece: "+str(self.promote_piece))
        print("Is Capture: "+str(self.is_capture))
        print("Captured Piece: " + str(self.captured_piece))
        print("Is Castle: "+str(self.is_castle))
        print("Is En Passant: "+str(self.is_en_passant))

    def __eq__(self,other):
        same = (self.old_position == other.old_position) and (self.new_position == other.new_position) and (self.promote_piece == self.promote_piece)
        return same


class Board():
    def __init__(self,pieces,color_at_bottom=Color.WHITE,color_to_move=Color.WHITE,castling_rights=[True,True,True,True],en_passant=[-1,-1],halfmoves = 0,fullmoves = 1):
        self.pieces = pieces
        self.white_piece_positions = []
        self.black_piece_positions = []
        for i in range(0,8):
            for j in range(0,8):
                if(pieces[i][j].color == Color.WHITE):
                    self.white_piece_positions.append([i,j])
                if(pieces[i][j].color == Color.BLACK):
                    self.black_piece_positions.append([i,j])
        self.color_to_move = color_to_move # the color whose turn it is
        self.en_passant = en_passant
        self.castling_rights = castling_rights
        self.halfmoves = halfmoves
        self.fullmoves = fullmoves
        self.color_at_bottom = color_at_bottom # color at the bottom of the board

    def make_move(self,move): # move a piece from one position to another
        move.prev_en_passant = self.en_passant
        old_position = move.old_position
        new_position = move.new_position
        promote_piece = move.promote_piece
        old_x = old_position[0]
        old_y = old_position[1]
        new_x = new_position[0]
        new_y = new_position[1]
        moving_piece = self.pieces[old_x][old_y]
        new_piece = self.pieces[new_x][new_y]
        # handle the four different castling possibilities
        castling = self.move_castle(old_position,new_position)
        if(castling): #if a move results from calling move_castle, end the function there (more or less)
            self.en_passant = [-1, -1]

            move.is_castle = True
            if (moving_piece.color == Color.BLACK):
                self.fullmoves += 1
                self.color_to_move = Color.WHITE
            elif(moving_piece.color==Color.WHITE):
                self.color_to_move = Color.BLACK
            move.removed_castling_rights = self.check_castling_rights()
            return True

        #update board elements based on move characteristics
        if(new_piece.piece_type != PieceType.EMPTY or moving_piece.piece_type == PieceType.PAWN):
            #either of the above conditions revert the number of halfmoves to 0
            self.halfmoves = 0
        else:
            self.halfmoves += 1



        if (moving_piece.piece_type == PieceType.PAWN and np.abs(new_x-old_x)==1 and np.abs(new_y-old_y)==1 and new_position == self.en_passant):
            # if en passant is possible, allow a pawn to execute it (just need to remove the pawn that moved 2 spaces)

            if(moving_piece.color == Color.WHITE):
                self.pieces[self.en_passant[0]][self.en_passant[1]-1] = Piece(Color.NONE,PieceType.EMPTY)
                self.black_piece_positions.remove([self.en_passant[0],self.en_passant[1]-1])
            if(moving_piece.color == Color.BLACK):
                if([self.en_passant[0],self.en_passant[1]+1] not in self.white_piece_positions):
                    print("THE PROBLEM IS HERE: "+str(generate_fen(self)))
                self.pieces[self.en_passant[0]][self.en_passant[1]+1] = Piece(Color.NONE,PieceType.EMPTY)

                self.white_piece_positions.remove([self.en_passant[0], self.en_passant[1] + 1])
            move.is_en_passant = True
        self.en_passant = [-1,-1]
        if (moving_piece.piece_type==PieceType.PAWN and np.abs(new_y-old_y)==2): # if the move is a pawn moving 2 spaces, set en passant square
            if(moving_piece.color == Color.WHITE):
                self.en_passant = [old_x,old_y+1]
            elif(moving_piece.color == Color.BLACK):
                self.en_passant = [old_x,old_y-1]


        if(self.pieces[new_x][new_y].piece_type != PieceType.EMPTY): #if we are capturing a piece...
            if(moving_piece.color == Color.WHITE):
                self.black_piece_positions.remove([new_x,new_y])
            if (moving_piece.color == Color.BLACK):
                self.white_piece_positions.remove([new_x, new_y])
            move.is_capture = True
            move.captured_piece = Piece(new_piece.color,new_piece.piece_type)
        self.pieces[old_x][old_y] = Piece(Color.NONE,PieceType.EMPTY)
        self.pieces[new_x][new_y] = moving_piece
        if(moving_piece.color == Color.WHITE):
            self.white_piece_positions.remove([old_x,old_y])
            self.white_piece_positions.append([new_x,new_y])
        if(moving_piece.color == Color.BLACK):

            self.black_piece_positions.remove([old_x,old_y])
            self.black_piece_positions.append([new_x, new_y])

        if(promote_piece != PieceType.EMPTY):
            move.is_promotion = True
            self.pieces[new_x][new_y] = Piece(self.color_to_move,promote_piece)

        if(moving_piece.color == Color.BLACK):
            self.fullmoves += 1
            self.color_to_move = Color.WHITE
        elif(moving_piece.color == Color.WHITE):
            self.color_to_move = Color.BLACK
        move.removed_castling_rights = self.check_castling_rights()

    def unmake_move(self,move): #undoes a move that was just done to the board
        # messes up the halfmove counter but we don't care for the purposes of move generation...
        original_position = move.old_position
        new_position = move.new_position
        captured_piece = move.captured_piece
        moving_piece = Piece(self.pieces[new_position[0]][new_position[1]].color,self.pieces[new_position[0]][new_position[1]].piece_type)
        if(self.color_to_move==Color.WHITE):
            self.color_to_move = Color.BLACK
        else:
            self.color_to_move = Color.WHITE
        if(moving_piece.color == Color.BLACK):
            self.fullmoves -= 1
        if(not move.is_castle):
            self.pieces[original_position[0]][original_position[1]] = moving_piece
            if(move.is_promotion):
                self.pieces[original_position[0]][original_position[1]].piece_type = PieceType.PAWN
            if(moving_piece.color == Color.WHITE):
                self.white_piece_positions.remove([new_position[0], new_position[1]])
                self.white_piece_positions.append([original_position[0],original_position[1]])
            if(moving_piece.color == Color.BLACK):
                self.black_piece_positions.remove([new_position[0], new_position[1]])
                self.black_piece_positions.append([original_position[0],original_position[1]])

            if(captured_piece.color == Color.WHITE):
                self.white_piece_positions.append([new_position[0], new_position[1]])
            if(captured_piece.color == Color.BLACK):
                self.black_piece_positions.append([new_position[0], new_position[1]])
            self.pieces[new_position[0]][new_position[1]] = captured_piece
            if(move.is_en_passant):
                pawn_color = Color.WHITE # color of pawn to insert
                if(moving_piece.color == Color.WHITE):
                    pawn_color = Color.BLACK
                if(pawn_color == Color.BLACK):
                    self.pieces[new_position[0]][new_position[1]-1] = Piece(pawn_color,PieceType.PAWN)
                    self.black_piece_positions.append([new_position[0], new_position[1]-1])
                elif(pawn_color == Color.WHITE):
                    self.pieces[new_position[0]][new_position[1] + 1] = Piece(pawn_color, PieceType.PAWN)
                    self.white_piece_positions.append([new_position[0], new_position[1]+1])
            self.en_passant = move.prev_en_passant


            if move.removed_castling_rights != "":
                if "K" in move.removed_castling_rights: self.castling_rights[0] = True
                if "Q" in move.removed_castling_rights: self.castling_rights[1] = True
                if "k" in move.removed_castling_rights: self.castling_rights[2] = True
                if "q" in move.removed_castling_rights: self.castling_rights[3] = True

        else:
            if(new_position == [6,0]):
                self.castling_rights[0] = True
                self.pieces[4][0] = Piece(Color.WHITE, PieceType.KING)
                self.pieces[5][0] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[6][0] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[7][0] = Piece(Color.WHITE, PieceType.ROOK)
                self.white_piece_positions.remove([5, 0])
                self.white_piece_positions.remove([6, 0])
                self.white_piece_positions.append([7, 0])
                self.white_piece_positions.append([4, 0])
            if(new_position == [2,0]):
                self.castling_rights[1] = True
                self.pieces[4][0] = Piece(Color.WHITE, PieceType.KING)
                self.pieces[3][0] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[2][0] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[1][0] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[0][0] = Piece(Color.WHITE, PieceType.ROOK)
                self.white_piece_positions.remove([2, 0])
                self.white_piece_positions.remove([3, 0])
                self.white_piece_positions.append([4, 0])
                self.white_piece_positions.append([0, 0])
            if(new_position == [6,7]):
                self.castling_rights[2] = True
                self.pieces[4][7] = Piece(Color.BLACK, PieceType.KING)
                self.pieces[5][7] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[6][7] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[7][7] = Piece(Color.BLACK, PieceType.ROOK)
                self.black_piece_positions.remove([5, 7])
                self.black_piece_positions.remove([6, 7])
                self.black_piece_positions.append([7, 7])
                self.black_piece_positions.append([4, 7])
            if(new_position == [2,7]):
                self.castling_rights[3] = True
                self.pieces[4][7] = Piece(Color.BLACK, PieceType.KING)
                self.pieces[3][7] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[2][7] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[1][7] = Piece(Color.NONE,PieceType.EMPTY)
                self.pieces[0][7] = Piece(Color.BLACK, PieceType.ROOK)
                self.black_piece_positions.remove([2, 7])
                self.black_piece_positions.remove([3, 7])
                self.black_piece_positions.append([4, 7])
                self.black_piece_positions.append([0, 7])




    def hypo_move(self,move): # hypothetical move... return the RESULT of moving a piece (without actually changing the board)
        new_board = copy.deepcopy(self)

        new_board.make_move(move)
        return new_board

    def check_castling_rights(self):
        # check if the white king has moved from its starting spot
        if ((self.pieces[4][0].piece_type != PieceType.KING) or (self.pieces[4][0].color != Color.WHITE)):
            if(self.castling_rights[0] or self.castling_rights[1]):
                self.castling_rights[0] = False
                self.castling_rights[1] = False
                return "KQ"

        # Repeat for the two white rooks, and their black counterparts
        if (self.pieces[7][0].piece_type != PieceType.ROOK or (self.pieces[7][0].color != Color.WHITE)):
            if(self.castling_rights[1]):
                self.castling_rights[0] = False
                return "Q"
        if (self.pieces[0][0].piece_type != PieceType.ROOK or (self.pieces[0][0].color != Color.WHITE)):
            if(self.castling_rights[0]):
                self.castling_rights[0] = False
                return "K"
        # Black king and rooks
        if ((self.pieces[4][7].piece_type != PieceType.KING) or (self.pieces[4][7].color != Color.BLACK)):
            if (self.castling_rights[2] or self.castling_rights[3]):
                self.castling_rights[2] = False
                self.castling_rights[3] = False
                return "kq"
        if (self.pieces[7][7].piece_type != PieceType.ROOK or (self.pieces[7][7].color != Color.BLACK)):
            if (self.castling_rights[2]):
                self.castling_rights[2] = False
                return "k"
        if (self.pieces[0][7].piece_type != PieceType.ROOK or (self.pieces[0][7].color != Color.BLACK)):
            if (self.castling_rights[3]):
                self.castling_rights[3] = False
                return "q"
        return ""

    def move_castle(self,old_position,new_position):
        # Handles castling possibilities when the "move" method is called.
        # Castles if the move represents one
        # Does NOT prevent an attempted castle if it is not allowed
        old_x,old_y = old_position
        new_x,new_y = new_position
        moving_piece = (self.pieces[old_x][old_y])
        new_piece = (self.pieces[new_x][new_y])

        output = False
        if (moving_piece.piece_type == PieceType.KING and old_position == [4, 0] and (new_position == [6, 0] or new_position == [7, 0])):
            self.pieces[4][0] = Piece(Color.NONE, PieceType.EMPTY)
            self.pieces[5][0] = Piece(Color.WHITE,PieceType.ROOK)
            self.pieces[6][0] = Piece(Color.WHITE,PieceType.KING)
            self.pieces[7][0] = Piece(Color.NONE,PieceType.EMPTY)
            if [4, 0] in self.white_piece_positions: self.white_piece_positions.remove([4, 0])
            if [7, 0] in self.white_piece_positions: self.white_piece_positions.remove([7, 0])
            self.white_piece_positions.append([5,0])
            self.white_piece_positions.append([6,0])
            output = True
        elif (moving_piece.piece_type == PieceType.KING and old_position == [4, 0] and (new_position == [0, 0] or new_position == [1, 0] or new_position == [2,0])):
            self.pieces[0][0] = Piece(Color.NONE, PieceType.EMPTY)
            self.pieces[1][0] = Piece(Color.NONE,PieceType.EMPTY)
            self.pieces[2][0] = Piece(Color.WHITE,PieceType.KING)
            self.pieces[3][0] = Piece(Color.WHITE,PieceType.ROOK)
            self.pieces[4][0] = Piece(Color.NONE, PieceType.EMPTY)
            if [4, 0] in self.white_piece_positions: self.white_piece_positions.remove([4, 0])
            if [0, 0] in self.white_piece_positions: self.white_piece_positions.remove([0, 0])
            self.white_piece_positions.append([2,0])
            self.white_piece_positions.append([3,0])
            output = True
        elif (moving_piece.piece_type == PieceType.KING and old_position == [4, 7] and (new_position == [6, 7] or new_position == [7, 7])):
            self.pieces[4][7] = Piece(Color.NONE, PieceType.EMPTY)
            self.pieces[5][7] = Piece(Color.BLACK,PieceType.ROOK)
            self.pieces[6][7] = Piece(Color.BLACK,PieceType.KING)
            self.pieces[7][7] = Piece(Color.NONE,PieceType.EMPTY)
            if [4, 7] in self.black_piece_positions: self.black_piece_positions.remove([4, 7])
            if [7, 7] in self.black_piece_positions: self.black_piece_positions.remove([7, 7])
            self.black_piece_positions.append([5,7])
            self.black_piece_positions.append([6,7])
            output = True
        elif (moving_piece.piece_type == PieceType.KING and old_position == [4, 7] and (new_position == [0, 7] or new_position == [1, 7] or new_position == [2,7])):
            self.pieces[0][7] = Piece(Color.NONE, PieceType.EMPTY)
            self.pieces[1][7] = Piece(Color.NONE,PieceType.EMPTY)
            self.pieces[2][7] = Piece(Color.BLACK,PieceType.KING)
            self.pieces[3][7] = Piece(Color.BLACK,PieceType.ROOK)
            self.pieces[4][7] = Piece(Color.NONE, PieceType.EMPTY)
            if [4, 7] in self.black_piece_positions: self.black_piece_positions.remove([4, 7])
            if [0, 7] in self.black_piece_positions: self.black_piece_positions.remove([0, 7])
            self.black_piece_positions.append([2,7])
            self.black_piece_positions.append([3,7])
            output = True
        '''
        # check if the white king has moved from its starting spot
        if ((self.pieces[4][0].piece_type != PieceType.KING) or (self.pieces[4][0].color != Color.WHITE)):
            self.castling_rights[0] = False
            self.castling_rights[1] = False
        # Repeat for the two white rooks, and their black counterparts
        if (self.pieces[7][0].piece_type != PieceType.ROOK or (self.pieces[7][0].color != Color.WHITE)):
            self.castling_rights[0] = False
        if (self.pieces[0][0].piece_type != PieceType.ROOK or (self.pieces[0][0].color != Color.WHITE)):
            self.castling_rights[1] = False
        # Black king and rooks
        if ((self.pieces[4][7].piece_type != PieceType.KING) or (self.pieces[4][7].color != Color.BLACK)):
            self.castling_rights[2] = False
            self.castling_rights[3] = False

        if (self.pieces[7][7].piece_type != PieceType.ROOK or (self.pieces[7][7].color != Color.BLACK)):
            self.castling_rights[2] = False
        if (self.pieces[0][7].piece_type != PieceType.ROOK or (self.pieces[0][7].color != Color.BLACK)):
            self.castling_rights[3] = False
        '''
        return output

    def toggle_color(self):
        if(self.color_to_move==Color.WHITE):
            self.color_to_move = Color.BLACK
        elif(self.color_to_move==Color.BLACK):
            self.color_to_move = Color.WHITE

def simple_to_normal(simple_board):
    pieces = [[Piece(Color.NONE,PieceType.EMPTY)]*8 for i in range(8)]
    colors = [[Color.NONE]*8 for i in range(8)]
    simple_pieces = simple_board.pieces
    white_positions = []
    black_positions = []
    for i in range(0,8):
        for j in range(0,8):
            if (simple_pieces[i][j] % 2 == 1 and simple_pieces[i][j] > 0):
                colors[i][j] = Color.WHITE
            if(simple_pieces[i][j]%2 == 0 and simple_pieces[i][j]>0):
                colors[i][j] = Color.BLACK
    for i in range(0, 8):
        for j in range(0, 8):
            enum_value = (simple_pieces[i][j] + simple_pieces[i][j]%2)//2
            if(colors[i][j]==Color.WHITE):
                pieces[i][j] = Piece(colors[i][j],PieceType(enum_value))
            if (colors[i][j] == Color.BLACK):
                pieces[i][j] = Piece(colors[i][j],PieceType(enum_value))
    color_to_move = Color.BLACK
    if(simple_board.white_to_move):
        color_to_move = Color.WHITE
    color_at_bottom = Color.WHITE
    castling_rights = simple_board.castling_rights
    en_passant = list(simple_board.en_passant)
    halfmoves = simple_board.halfmoves
    fullmoves = simple_board.fullmoves
    output = Board(pieces,color_at_bottom,color_to_move,castling_rights,en_passant,halfmoves,fullmoves)

    return output

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
    castling_rights_str = fen_parts[2]
    print(castling_rights_str)
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
    castling_rights = [False, False, False, False]
    if("K" in castling_rights_str): castling_rights[0] = True
    if("Q" in castling_rights_str): castling_rights[1] = True
    if("k" in castling_rights_str): castling_rights[2] = True
    if("q" in castling_rights_str): castling_rights[3] = True
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
    castling_str = "KQkq"

    if(not(board.castling_rights[0])):
        castling_str = castling_str.replace("K","")
    if (not(board.castling_rights[1])):
        castling_str = castling_str.replace("Q","")
    if (not(board.castling_rights[2])):
        castling_str = castling_str.replace("k","")
    if (not(board.castling_rights[3])):
        castling_str = castling_str.replace("q","")
    if (castling_str == ""):
        castling_str = "-"
    alpha_string = "abcdefgh"
    en_passant_arr = board.en_passant
    en_passant_str = "-"
    if(board.en_passant != [-1,-1]):
        en_passant_str = alpha_string[board.en_passant[0]]+str(board.en_passant[1]+1)
    halfmoves_str = str(board.halfmoves)
    fullmoves_str = str(board.fullmoves)
    output_str = " ".join([position_str,who_str,castling_str,en_passant_str,halfmoves_str,fullmoves_str])
    return output_str
