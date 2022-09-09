import numpy as np
class SimpleBoard():
    # An attempt to create a board requiring less memory and time to make moves and search.
    #PIECES:
    #0 = Empty, 1 = White Pawn, 2 = Black Pawn, 3 =  White Knight, 4 = Black Knight, 5 = White Bishop, 6 = Black Bishop
    # 7 = White Rook, 8 = Black Rook, 9 = White Queen, 10 = Black Queen, 11 = White King, 12 = Black King

    def __init__(self,pieces,white_to_move = True,castling_rights = np.asarray([True,True,True,True]),en_passant = np.asarray([-1,-1]),halfmoves = 0,fullmoves = 1):
        self.pieces = pieces #np array
        self.white_to_move = white_to_move
        self.castling_rights = castling_rights
        self.en_passant = en_passant
        self.halfmoves = halfmoves
        self.fullmoves = fullmoves
    def move(self,old_position,new_position,promote_piece = 0):

        old_piece = self.pieces[old_position[0],old_position[1]]
        new_piece = self.pieces[new_position[0],new_position[1]]
        castled = False
        if (old_piece == 11 and old_position == [4, 0] and (new_position == [6, 0] or new_position == [7, 0])):
            self.pieces[4][0] = 0
            self.pieces[5][0] = 7
            self.pieces[6][0] = 11
            self.pieces[7][0] = 0
            self.castling_rights[0] = False
            castled = True

        elif (old_piece == 11 and old_position == [4, 0] and (new_position == [2, 0] or new_position == [1, 0])):
            self.pieces[0][0] = 0
            self.pieces[1][0] = 0
            self.pieces[2][0] = 11
            self.pieces[3][0] = 7
            self.pieces[4][0] = 0
            self.castling_rights[1] = False
            castled = True

        elif (old_piece == 12 and old_position == [4, 7] and (new_position == [6, 7] or new_position == [7, 7])):

            self.pieces[4][7] = 0
            self.pieces[5][7] = 8
            self.pieces[6][7] = 12
            self.pieces[7][7] = 0
            self.castling_rights[2] = False
            castled = True

        elif (old_piece == 12 and old_position == [4, 7] and (new_position == [2, 7] or new_position == [1, 7])):

            self.pieces[0][0] = 0
            self.pieces[1][0] = 0
            self.pieces[2][0] = 12
            self.pieces[3][0] = 8
            self.pieces[4][0] = 0
            self.castling_rights[3] = False
            castled = True

        if(castled):
            self.halfmoves += 1
            if(not self.white_to_move):
                self.fullmoves += 1
            self.white_to_move = not self.white_to_move
            return True

        if ((2 >= old_piece >= 1) and np.abs(new_position[0] - old_position[0]) == 1 and np.abs(new_position[1] - old_position[1])==1 and np.array_equal(new_position, self.en_passant)):
            # if en passant is possible, allow a pawn to execute it (just need to remove the pawn that moved 2 spaces)

            if(old_piece%2 == 1):
                self.pieces[self.en_passant[0]][self.en_passant[1]-1] = 0

            if(old_piece % 2 == 0 and old_piece>0):
                self.pieces[self.en_passant[0]][self.en_passant[1]+1] = 0

        if ((2 >= old_piece >= 1) and np.abs(new_position[1]-old_position[1])==2): # if the move is a pawn moving 2 spaces, set en passant square
            if(old_piece%2 == 1):
                self.en_passant = np.asarray([old_position[0],old_position[1]+1])
            elif(old_piece%2 == 0 and old_piece>0):
                self.en_passant = np.asarray([old_position[0],old_position[1]-1])
        else:
            self.en_passant = np.asarray([-1,-1])

        self.pieces[new_position[0]][new_position[1]] = old_piece
        self.pieces[old_position[0]][old_position[1]] = 0
        if(promote_piece != 0):
            self.pieces[new_position[0]][new_position[1]] = promote_piece

        #check castling rights
        if (self.pieces[4][0] != 11):
            self.castling_rights[0] = False
            self.castling_rights[1] = False
        # Repeat for the two white rooks, and their black counterparts
        if (self.pieces[7][0] != 7):
            self.castling_rights[0] = False
        if (self.pieces[0][0] != 7):
            self.castling_rights[1] = False
        # Black king and rooks
        if (self.pieces[4][7] != 12):
            self.castling_rights[2] = False
            self.castling_rights[3] = False
        if (self.pieces[7][7] != 8):
            self.castling_rights[2] = False
        if (self.pieces[0][7] != 8):
            self.castling_rights[3] = False
        #update board elements based on move characteristics
        if(new_piece != 0 or 1<=old_piece<=2):
            #either of the above conditions revert the number of halfmoves to 0
            self.halfmoves = 0
        else:
            self.halfmoves += 1
        if(not self.white_to_move):
            self.fullmoves += 1
        self.white_to_move = not self.white_to_move

    def toggle_color(self):
        self.white_to_move = not self.white_to_move

def initialise_pieces():
    pieces = np.zeros((8,8),dtype="uint8")
    pieces[:,0] = np.array([7,3,5,9,11,5,3,7])
    pieces[:,1] = np.array([1,1,1,1,1,1,1,1])
    pieces[:,6]= np.array([2,2,2,2,2,2,2,2])
    pieces[:,7] = np.array([8,4,6,10,12,6,4,8])
    return pieces

def import_fen(fen_str): #standardised representation of a chess board using a single string
    #output a SimpleBoard matching the given fen

    fen_parts = fen_str.split(" ")
    white_to_move = True
    board_rows = fen_parts[0].split("/")
    pieces = np.zeros((8,8),dtype="uint8")
    for k in range(0,8):

        j = 7-k # y coord of current row
        curr_row = board_rows[k]
        piece_string = " PpNnBbRrQqKk"

        index = -1
        board_coord = 0 # x coord to place pieces
        for i in range(0,len(curr_row)): #iterate through chars in the current row (NOT through board positions)
            color = Color.NONE
            character = curr_row[i]

            if (not character.isdigit()):
                index = piece_string.index(character)
                pieces[board_coord][j] = index
                board_coord+=1 #if the last char was a letter, increment the board coordinate by 1
            else:
                num_to_move = int(character)
                board_coord += num_to_move # skip however many squares the number in the fen string tells you to

    if (fen_parts[1]=="b"):
        white_to_move = False
    if(fen_parts[1]=="w"):
        white_to_move = True
    castling_rights_str = fen_parts[2]
    castling_rights = np.asarray(["K" in castling_rights_str,"Q" in castling_rights_str, "k" in castling_rights_str, "q" in castling_rights_str])
    en_passant_str = fen_parts[3]
    alpha_string = "abcdefgh"
    if(en_passant_str == "-"):
        en_passant_out = np.asarray([-1,-1]) # will output the square where en passant is possible, if it exists
    else:
        idx = alpha_string.index(en_passant_str[0]) # get numerical rank of en passant square
        y_val = int(en_passant_str[1])-1 #file of en passant square
        en_passant_out = np.asarray([idx,y_val])
    if not(en_passant_str == "-"):
        x_coord = alpha_string.index(en_passant_str[0]) #first char in the string is the rank of the enpassant square
        y_coord = int(en_passant_str[1])-1
        en_passant_out = np.asarray[x_coord,y_coord]

    output_board = SimpleBoard(pieces,white_to_move,castling_rights,en_passant_out)
    return output_board