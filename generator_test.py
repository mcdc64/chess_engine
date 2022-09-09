import board_elements
from board_elements import Board,Color,Piece,PieceType,import_fen
import simple_board
import move_generator
import time
import sys

startTime = time.time()
pieces = board_elements.initialise_pieces()
board = Board(pieces)
simple_pieces = simple_board.initialise_pieces()
s_board = simple_board.SimpleBoard(simple_pieces)
board = board_elements.simple_to_normal(s_board)

s_board.move([1,1],[1,3],0)
s_board.move([2,6],[2,4],0)
s_board.move([1,3],[2,4],0)
print(board.pieces)

#fen = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"
#board = import_fen(fen)
print(sys.getsizeof(board))
print(sys.getsizeof(s_board))
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