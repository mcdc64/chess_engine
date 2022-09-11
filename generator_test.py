import board_elements
from board_elements import Board,Color,Piece,PieceType,Move,import_fen,generate_fen
import simple_board
import move_generator

import time
import sys



#simple_pieces = simple_board.initialise_pieces()
#s_board = simple_board.SimpleBoard(simple_pieces)
#board = board_elements.simple_to_normal(s_board)

#s_board.move([1,1],[1,3],0)
#s_board.move([2,6],[2,4],0)
#s_board.move([1,3],[2,4],0)
#print(board.pieces)

fen = "k1K5/8/8/2pP4/8/8/8/8 w - c6 1 8" # fen to test doing/undoing en passant
fen = "k/8/8/8/8/8/8/4K2R w K - 1 8" # fen to test castling
fen = "K7/3P4/8/8/8/8/8/k w - c6 1 8" # fen to test promotion

board = import_fen(fen)
pieces = board_elements.initialise_pieces()
board = Board(pieces)
board.make_move(Move([4,1],[4,3]))
board.make_move(Move([4,6],[4,4]))
board.make_move(Move([6,0],[5,2]))
board.make_move(Move([1,7],[2,5]))
board.make_move(Move([5,0],[1,4]))
board.make_move(Move([3,6],[3,5]))
board.make_move(Move([1,4],[2,5])) #Ruy Lopez, followed by Old Steinitz defense and capture of knight on c6
board.make_move(Move([1,6],[2,5]))
print(generate_fen(board))



startTime = time.time()
depth = 2
move_history = []
def Search(board,depth):

    legal_moves = move_generator.generate_legal_moves(board)
    total = 0
    if(depth == 1):
        return len(legal_moves)
    for move in legal_moves:
        board.make_move(move)
        total += Search(board,depth-1)
        board.unmake_move(move)
    return total
print(Search(board,depth))
print("Time: "+str(time.time()-startTime))