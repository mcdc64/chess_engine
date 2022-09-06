from board_elements import Board, Color, Piece, PieceType

def get_bishop_moves(board,i,j): #get moves of a bishop on board at position i,j

    out_moves = []


    for d in range(1,8): # upper right diagonal
        if((i+d<8) and (j+d<8)):
            if(board.pieces[i+d][j+d].piece_type == PieceType.EMPTY):
                out_moves.append([[i,j],[i+d,j+d]])
            else:
                if(board.pieces[i+d][j+d].color != board.color_to_move):
                    out_moves.append([[i,j],[i+d,j+d]])
                break
        else:
            break

    for d in range(1,8): # upper left diagonal
        if((i-d>=0) and (j+d<8)):
            if(board.pieces[i-d][j+d].piece_type == PieceType.EMPTY):
                out_moves.append([[i,j],[i-d,j+d]])
            else:
                if(board.pieces[i-d][j+d].color != board.color_to_move):
                    out_moves.append([[i,j],[i-d,j+d]])
                break
        else:
            break

    for d in range(1,8): # lower left diagonal
        if((i-d>=0) and (j-d>=0)):
            if(board.pieces[i-d][j-d].piece_type == PieceType.EMPTY):
                out_moves.append([[i,j],[i-d,j-d]])
            else:
                if(board.pieces[i-d][j-d].color != board.color_to_move):
                    out_moves.append([[i,j],[i-d,j-d]])
                break
        else:
            break

    for d in range(1,8): # lower right diagonal
        if((i+d<8) and (j-d>=0)):
            if(board.pieces[i+d][j-d].piece_type == PieceType.EMPTY):
                out_moves.append([[i,j],[i+d,j-d]])
            else:
                if(board.pieces[i+d][j-d].color != board.color_to_move):
                    out_moves.append([[i,j],[i+d,j-d]])
                break
        else:
            break
    return out_moves

def get_rook_moves(board,i,j):
    out_moves = []

    for d in range(1, 8):  # right rank
        if (i + d < 8):
            if (board.pieces[i + d][j].piece_type == PieceType.EMPTY):
                out_moves.append([[i, j], [i + d, j]])
            else:
                if (board.pieces[i + d][j].color != board.color_to_move):
                    out_moves.append([[i, j], [i + d, j]])
                break
        else:
            break

    for d in range(1, 8):  # left rank
        if (i - d >= 0):
            if (board.pieces[i - d][j].piece_type == PieceType.EMPTY):
                out_moves.append([[i, j], [i - d, j]])
            else:
                if (board.pieces[i - d][j].color != board.color_to_move):
                    out_moves.append([[i, j], [i - d, j]])
                break
        else:
            break

    for d in range(1, 8):  # upper file
        if (j + d < 8):
            if (board.pieces[i][j + d].piece_type == PieceType.EMPTY):
                out_moves.append([[i, j], [i, j + d]])
            else:
                if (board.pieces[i][j + d].color != board.color_to_move):
                    out_moves.append([[i, j], [i, j + d]])
                break
        else:
            break

    for d in range(1, 8):  # lower file
        if (j - d >= 0):
            if (board.pieces[i][j - d].piece_type == PieceType.EMPTY):
                out_moves.append([[i, j], [i, j - d]])
            else:
                if (board.pieces[i][j - d].color != board.color_to_move):
                    out_moves.append([[i, j], [i, j - d]])
                break
        else:
            break
    return out_moves

def get_knight_moves(board,i,j):
    eight_squares = [[i+2,j+1],[i+2,j-1],[i+1,j-2],[i-1,j-2],[i-2,j-1],[i-2,j+1],[i-1,j+2],[i+1,j+2]]

    out_moves = []
    for square in eight_squares:
        square_x = square[0]
        square_y = square[1]
        if(0<=square_x<8 and 0<=square_y<8): #making sure the squares are on the board
            if(board.pieces[square_x][square_y].color != board.color_to_move): #making sure another piece of the same color doesn't occupy the squares

                out_moves.append([[i,j],[square_x,square_y]])
    return out_moves

def get_pawn_moves(board,i,j):
    out_moves = []
    if(board.color_to_move==Color.WHITE):
        left_diagonal_move = [[i,j],[i-1,j+1]]
        right_diagonal_move = [[i,j],[i+1,j+1]]
        forward_move = [[i,j],[i,j+1]]
        two_forward_move = [[i,j],[i,j+2]]
        # pawn can move diagonally if an opposite-colour piece is there or if en passant is available on that square
        if(i-1>=0 and j+1<8 and (board.pieces[i-1][j+1].color == Color.BLACK or board.en_passant == [i-1,j+1])):
            out_moves.append(left_diagonal_move)
        if(i+1<8 and j+1<8 and (board.pieces[i+1][j+1].color == Color.BLACK or board.en_passant == [i+1,j+1])):
            out_moves.append(right_diagonal_move)

        if(j+1<8 and board.pieces[i][j+1].piece_type == PieceType.EMPTY):
            out_moves.append(forward_move)
        if(j==1 and board.pieces[i][2].piece_type == PieceType.EMPTY and board.pieces[i][3].piece_type == PieceType.EMPTY):
            out_moves.append(two_forward_move)
    if(board.color_to_move==Color.BLACK):
        left_diagonal_move = [[i,j],[i-1,j-1]]
        right_diagonal_move = [[i,j],[i+1,j-1]]
        forward_move = [[i,j],[i,j-1]]
        two_forward_move = [[i,j],[i,j-2]]
        # pawn can move diagonally if an opposite-colour piece is there or if en passant is available on that square
        if(i-1>=0 and j-1>=0 and (board.pieces[i-1][j-1].color == Color.WHITE or board.en_passant == [i-1,j-1])):
            out_moves.append(left_diagonal_move)
        if(i+1<8 and j-1>=0 and (board.pieces[i+1][j-1].color == Color.WHITE or board.en_passant == [i+1,j-1])):
            out_moves.append(right_diagonal_move)
        if(j-1>=0 and board.pieces[i][j-1].piece_type == PieceType.EMPTY):
            out_moves.append(forward_move)
        if(j==6 and board.pieces[i][5].piece_type == PieceType.EMPTY and board.pieces[i][4].piece_type == PieceType.EMPTY):
            out_moves.append(two_forward_move)
    return out_moves

def get_king_moves(board,i,j):
    eight_squares = [[i+1,j],[i+1,j-1],[i,j-1],[i-1,j-1],[i-1,j],[i-1,j+1],[i,j+1],[i+1,j+1]]
    out_moves = []
    for square in eight_squares:
        if(0<=square[0]<8 and 0<=square[1]<8):
            target_piece = board.pieces[square[0]][square[1]]
            if(target_piece.color != board.color_to_move or target_piece.piece_type == PieceType.EMPTY):
                out_moves.append([[i,j],[square[0],square[1]]])
    if(board.color_to_move==Color.WHITE):
        if("K" in board.castling_rights and board.pieces[5][0].piece_type == PieceType.EMPTY and board.pieces[6][0].piece_type == PieceType.EMPTY):
            out_moves.append([[i,j],[6,0]])
        if ("Q" in board.castling_rights and board.pieces[3][0].piece_type == PieceType.EMPTY and
                board.pieces[2][0].piece_type == PieceType.EMPTY and
                board.pieces[1][0].piece_type == PieceType.EMPTY):
            out_moves.append([[i, j], [1, 0]])
            out_moves.append([[i, j], [2, 0]])
    if (board.color_to_move == Color.BLACK):
        if ("q" in board.castling_rights and board.pieces[5][7].piece_type == PieceType.EMPTY and
                board.pieces[6][7].piece_type == PieceType.EMPTY):
            out_moves.append([[i, j], [6, 7]])
        if ("k" in board.castling_rights and board.pieces[3][7].piece_type == PieceType.EMPTY and
                board.pieces[2][7].piece_type == PieceType.EMPTY and
                board.pieces[1][7].piece_type == PieceType.EMPTY):
            out_moves.append([[i, j], [1, 7]])
            out_moves.append([[i, j], [2, 7]])
    return out_moves

def get_queen_moves(board,i,j):
    # use a lazy shortcut to get the queen moves
    bishop_moves = get_bishop_moves(board,i,j)
    rook_moves = get_rook_moves(board,i,j)
    out_moves = bishop_moves+rook_moves
    return out_moves

def generate_all_moves(board):
    moving_color = board.color_to_move
    # get all pieces of the moving color
    moving_piece_positions = []
    pseudo_legal_moves = []
    for i in range(0,8):
        for j in range(0,8):
            if(board.pieces[i][j].color == moving_color):
                moving_piece_positions.append([i,j])

    for position in moving_piece_positions:
        i = position[0]
        j = position[1]
        curr_piece = board.pieces[i][j]
        if(curr_piece.piece_type == PieceType.BISHOP):
            pseudo_legal_moves += get_bishop_moves(board,i,j)
        elif (curr_piece.piece_type == PieceType.ROOK):
            pseudo_legal_moves += get_rook_moves(board, i, j)
        elif (curr_piece.piece_type == PieceType.QUEEN):
            pseudo_legal_moves += get_queen_moves(board, i, j)
        elif (curr_piece.piece_type == PieceType.KNIGHT):
            pseudo_legal_moves += get_knight_moves(board, i, j)
        elif (curr_piece.piece_type == PieceType.PAWN):
            pseudo_legal_moves += get_pawn_moves(board, i, j)
        elif (curr_piece.piece_type == PieceType.KING):
            pseudo_legal_moves += get_king_moves(board, i, j)
    return pseudo_legal_moves

def one_piece_moves(board,i,j): #get the moves of just the piece at i,j (mainly used for highlighting the board)
    curr_piece = board.pieces[i][j]

    pseudo_legal_moves = []
    if (curr_piece.piece_type == PieceType.BISHOP):
        pseudo_legal_moves += get_bishop_moves(board, i, j)
    elif (curr_piece.piece_type == PieceType.ROOK):
        pseudo_legal_moves += get_rook_moves(board, i, j)
    elif (curr_piece.piece_type == PieceType.QUEEN):
        pseudo_legal_moves += get_queen_moves(board, i, j)
    elif (curr_piece.piece_type == PieceType.KNIGHT):
        pseudo_legal_moves += get_knight_moves(board, i, j)
    elif (curr_piece.piece_type == PieceType.PAWN):
        pseudo_legal_moves += get_pawn_moves(board, i, j)
    elif (curr_piece.piece_type == PieceType.KING):
        pseudo_legal_moves += get_king_moves(board, i, j)
    return pseudo_legal_moves


