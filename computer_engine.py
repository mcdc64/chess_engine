from board_elements import Board,Color,Piece,PieceType
import random as rand
class Engine():
    def __init__(self,color):
        self.color = color

    def next_move(self,board):
        i = rand.randint(0,6)
        j = rand.randint(0,6)
        while(board.pieces[i][j].color != self.color):
            i = rand.randint(0, 6)
            j = rand.randint(0, 6)
        return [i,j],[i,j-1]