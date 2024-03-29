from board_elements import Board,Color,Piece,PieceType
import move_generator
import random as rand
class Engine():
    def __init__(self,color):
        self.color = color

    def next_move(self,board):
        if(len(allowed_moves)>0):
            allowed_moves = move_generator.generate_pseudo_moves(board)
            i = rand.randint(0,len(allowed_moves)-1)
            return allowed_moves[i]
        return [[-1,-1],[-1,-1],PieceType.EMPTY]