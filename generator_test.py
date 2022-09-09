from board_elements import Board,Color,Piece,PieceType,initialise_pieces,import_fen
import move_generator
import time
import sys

startTime = time.time()
pieces = initialise_pieces()
board = Board(pieces)
#fen = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"
#board = import_fen(fen)
print(sys.getsizeof(board))
depth = 3
def Search(board,depth):

    legal_moves = move_generator.generate_pseudo_moves(board)
    total = 0
    if(depth == 1):
        return len(legal_moves)
    for move in legal_moves:
        new_board = board.hypo_move(move[0],move[1],move[2])
        total += Search(new_board,depth-1)
    return total
print(Search(board,depth))
print("Time: "+str(time.time()-startTime))