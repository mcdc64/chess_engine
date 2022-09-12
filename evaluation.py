from board_elements import Board,Piece,PieceType,Color,Move
import move_generator
import numpy as np

def evaluate(board):

    piece_value_dict = {PieceType.PAWN:1,PieceType.KNIGHT:3,PieceType.BISHOP:3,PieceType.ROOK:5,PieceType.QUEEN:9
        ,PieceType.KING:0,PieceType.EMPTY:0}
    # empty squares, and kings have no value (giving kings infinite value causes issues)
    # count material for both sides
    white_material = 0
    black_material = 0
    white_piece_positions = np.asarray(board.white_piece_positions)
    black_piece_positions = np.asarray(board.black_piece_positions)
    white_pawn_positions = []
    black_pawn_positions = []
    for position in white_piece_positions:
        piece = board.pieces[position[0]][position[1]]
        white_material += piece_value_dict[piece.piece_type]
        if(piece.piece_type == PieceType.PAWN):
            white_pawn_positions.append(position)
    for position in black_piece_positions:
        piece = board.pieces[position[0]][position[1]]
        black_material += piece_value_dict[piece.piece_type]
        if(piece.piece_type == PieceType.PAWN):
            black_pawn_positions.append(position)
    material_diff = white_material - black_material # positive if white has more material, negative if black has more

    # get number of files with doubled or tripled pawns
    white_pawn_positions = np.asarray(white_pawn_positions)
    black_pawn_positions = np.asarray(black_pawn_positions)
    doubled_white_files = np.shape(white_pawn_positions)[0] - len(np.unique(white_pawn_positions))
    doubled_black_files = np.shape(black_pawn_positions)[0] - len(np.unique(black_pawn_positions))

    in_check = int(move_generator.in_check(board))
    if(board.color_to_move == Color.BLACK):
        in_check = -in_check

    white_hanging_material = 0
    black_hanging_material = 0
    white_attacked_squares = move_generator.get_attacked_squares(board,Color.WHITE)
    black_attacked_squares = move_generator.get_attacked_squares(board, Color.BLACK)
    for pos in white_piece_positions:
        if(black_attacked_squares[pos[0],pos[1]] and not white_attacked_squares[pos[0],pos[1]]):
            white_hanging_material += piece_value_dict[board.pieces[pos[0]][pos[1]].piece_type]
            print("Hanging piece at " + str(pos) + ", piece is " + str(board.pieces[pos[0]][pos[1]].piece_type))
    for pos in black_piece_positions:
        if(white_attacked_squares[pos[0],pos[1]] and not black_attacked_squares[pos[0],pos[1]]):
            black_hanging_material += piece_value_dict[board.pieces[pos[0]][pos[1]].piece_type]
            print("Hanging piece at "+str(pos)+", piece is "+str(board.pieces[pos[0]][pos[1]].piece_type))

    # set weights of each factor involved in evaluation
    # factors that are "bad" for the moving color if higher should have negative weight (e.g. number of doubled files)
    material_weight = 1
    doubled_pawn_weight = -0.4 # incrementally worse depending on no. of double files
    in_check_weight = -0.2 # not so bad on its own
    color_to_move_hang_weight = -0.6 # hanging pieces are fixable if you are about to move, so not as bad
    opposite_color_hang_weight = 0.8
    if(board.color_to_move==Color.WHITE):
        hang_term = (white_hanging_material*color_to_move_hang_weight)+(black_hanging_material)*opposite_color_hang_weight
    else:
        hang_term = -(black_hanging_material*color_to_move_hang_weight)-(white_hanging_material)*opposite_color_hang_weight

    output = (white_material-black_material)*material_weight + (doubled_white_files-doubled_black_files)*doubled_pawn_weight
    output += (in_check*in_check_weight) + hang_term
    return output

