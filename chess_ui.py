import random

import numpy as np
import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.button import ButtonArray
from pygame_widgets.textbox import TextBox
import board_elements
import computer_engine

import time
import copy
from pygame.locals import K_p
from enum import Enum





def coords_to_pygame(coords,height):
    return (coords[0],height-coords[1])


def draw_board(board, x1,y1, board_length, screen, screen_height,selected_piece):
    square_length = board_length // 8

    for i in range(0, 8):
        for j in range(0, 8):
            curr_col = (80 + 175 * ((i + j) % 2), 150 + 105 * ((i + j) % 2),
                        180 + 75 * ((i + j) % 2))  # 0 for black squares, 1 for white squares

            curr_piece = board.pieces[i][j]
            if (board.color_at_bottom == board_elements.Color.BLACK):
                curr_piece = board.pieces[7-i][7 - j]
            x_coord, y_coord = coords_to_pygame((x1 + (square_length * i), y1 + (square_length * j)),
                                                screen_height)
            curr_rect = pygame.Rect(x_coord, y_coord, square_length, square_length)
            if(board.color_at_bottom == board_elements.Color.BLACK and selected_piece == [7-i,7-j]):
                curr_col = (50,200,150)
            elif (board.color_at_bottom == board_elements.Color.WHITE and selected_piece == [i, j]):
                curr_col = (50, 200, 150)
            pygame.draw.rect(screen, curr_col, curr_rect)

            piece_filename = "images/empty.png"


            if (curr_piece.piece_type != board_elements.PieceType.EMPTY):
                piece_filename = "images/" + curr_piece.color.name.lower() + "_" + curr_piece.piece_type.name.lower() + ".png";
            piece_img = pygame.transform.scale(pygame.image.load(piece_filename), (square_length, square_length))
            piece_rect = pygame.Rect(x_coord, y_coord, square_length, square_length)
            screen.blit(piece_img, piece_rect)

def draw_move_history(game_move_strs,x1,y1,box_width,box_height,screen,screen_height,num_moves=30):
    font = pygame.font.SysFont(None, int(40*screen_height/880))
    for i in range(0,num_moves//2):
        if(len(game_move_strs)>(2*i)+1):
            first_str = game_move_strs[2*i]
            second_str = game_move_strs[(2*i)+1]
        elif(len(game_move_strs)>(2*i)):
            first_str = game_move_strs[2*i]
            second_str = ""
        else:
            first_str = ""
            second_str = ""
        x_coord,y_coord = x1,(y1+i*box_height)
        second_x_coord = x1+box_width
        number_label = font.render(str(i+1)+".",False,(0,0,0))
        first_label = font.render(first_str, False, (0, 0, 0))
        second_label = font.render(second_str, False, (0, 0, 0))

        number_rect = pygame.Rect(x_coord - box_height,y_coord+box_height//4,box_height,box_height)
        first_rect = pygame.Rect(x_coord,y_coord,box_width,box_height)
        second_rect = pygame.Rect(second_x_coord,y_coord,box_width,box_height)

        first_col = np.asarray([50,97,47])+ np.asarray([77*(i%2),30*(i%2),80*(i%2)])
        second_col = np.asarray([50,97,47])+ np.asarray([77*((i+1)%2),30*((i+1)%2),80*((i+1)%2)])

        pygame.draw.rect(screen,first_col,first_rect)
        pygame.draw.rect(screen, second_col, second_rect)
        screen.blit(first_label,first_rect)
        screen.blit(second_label,second_rect)
        screen.blit(number_label,number_rect)




def board_square(board,x1,y1,board_length,pyg_x,pyg_y,screen_height): # find the board square containing given x and y screen coords
    x,y = coords_to_pygame((pyg_x,pyg_y),screen_height) # convert the screen coords to space coords
    # note coords_to_pygame is its own inverse function so we don't need to worry about which direction...

    i = int((x - x1)/(board_length//8))
    j = int((y-y1+(board_length//8))/(board_length//8))
    if(not(0<=i<=7)or not(0<=j<=7)):
        return(-1,-1)
    elif((y-y1+(board_length//8))<0 or(x-x1)<0):
        return (-1, -1)
    if(board.color_at_bottom==board_elements.Color.BLACK):
        return(7-i,7-j)
    return (i,j)

def start_game():
    global on_menu
    on_menu = False
def flip_board(board):
    if(board.color_at_bottom==board_elements.Color.WHITE):
        board.color_at_bottom=board_elements.Color.BLACK
    else:
        board.color_at_bottom=board_elements.Color.WHITE

def change_fen(forward):
    global fen_to_display
    global game_fens
    max_fen = len(game_fens)-1
    if(forward and fen_to_display<max_fen):
        fen_to_display += 1
    if(not forward and fen_to_display>0):
        fen_to_display -= 1

def handle_board_click(board,first_sq, second_sq, mouse_down_sq, mouse_up_sq): # decides what happens if board clicked
    if (first_sq == [-1, -1]):  # if no square is selected up to now, select the clicked square
        if not (board.pieces[mouse_up_sq[0]][mouse_up_sq[1]].piece_type == board_elements.PieceType.EMPTY):
            if(board.pieces[mouse_up_sq[0]][mouse_up_sq[1]].color == board.color_to_move): #only allow pieces to be selected if it is their move
                first_sq = mouse_up_sq

        mouse_down_sq = [-1, -1]
        mouse_up_sq = [-1, -1]
    elif (first_sq == mouse_up_sq):  # deselect the first square if it is clicked twice
        first_sq = [-1, -1]
        mouse_down_sq = [-1, -1]
        mouse_up_sq = [-1, -1]
    else:  # if a first square is already selected, assign a second square
        second_sq = mouse_up_sq
        mouse_down_sq = [-1, -1]
        mouse_up_sq = [-1, -1]
    return first_sq,second_sq,mouse_down_sq,mouse_up_sq,

pygame.init()
font = pygame.font.SysFont(None, 50)

aspect_ratio = 1.6
screen_height = 880
screen_width = aspect_ratio*screen_height
board_length = int(0.85*screen_height)-int(0.85*screen_height)%8 # MUST BE A MULTIPLE OF 8!! Divisibility by 8 ensures the 64 squares are of integer length
board_x = (screen_width-board_length)//4
board_y = 150
screen = pygame.display.set_mode([screen_width, screen_height])
running = True
on_menu = True

mouse_down_button = ""
mouse_down_square = [-1,-1]
mouse_up_square = [-1,-1]
first_square = [-1,-1]
second_square = [-1,-1]

pieces = board_elements.initialise_pieces()
fen_str = "rnbk2nr/ppp2Bpp/8/2b8/4N8/5Q8/PPPP1PPP/R1B1K2R b KQkq - 0 8"
#board = board_elements.import_fen(fen_str)
board = board_elements.Board(pieces)
game_fens = [board_elements.generate_fen(board)] # save all fen strings for the board so it can be replayed
fen_to_display = 0 # the current fen being displayed
game_move_strs = []
selected_piece = [-1,-1]


menu_buttons = [Button(screen,500,300,80,40,image=pygame.transform.scale(pygame.image.load("images/start_button.png"),(80,40)),onClick=start_game)]

game_button_width = int(0.08*screen_width)
game_button_height = int(0.05*screen_height)
flip_button = Button(screen,int((screen_width)*0.66),int(0.88*screen_height),game_button_width,game_button_height,text="Flip Board",fontSize = 30,onClick=flip_board,onClickParams=[board])
forward_back_array = ButtonArray(screen,int((screen_width)*0.75),int(0.88*screen_height),2*game_button_width,game_button_height,(2,1),fontSizes = (30,30),texts=("<",">"),onClicks=(change_fen,change_fen),onClickParams=([False],[True]))
turn_label = font.render(str(board.fullmoves),False,(0,0,0))
game_widgets= [flip_button,forward_back_array]

player_types = ["Computer","Human"] # first position is black, second position is white
engine = computer_engine.Engine(board_elements.Color.BLACK)

for button in game_widgets:
    button.hide()

while running:
    events = pygame.event.get()
    if on_menu:
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        screen.fill((80, 182, 153))
        pygame_widgets.update(events)

        pygame.display.update()
        continue
    allow_board_clicks = False
    at_present_board = (fen_to_display == len(game_fens)-1)
    if(at_present_board and player_types[board.color_to_move.value]=="Human"): #if the display fen is the current board, allow moves
        allow_board_clicks = True
    if(not allow_board_clicks): #reset the first and second selected squares each frame to prevent board clicks
        first_square = [-1,-1]
        second_square= [-1,-1]

    for button in menu_buttons:
        button.hide()
    for button in game_widgets:
        button.show()
    for event in events:
        mouse_pos = pygame.mouse.get_pos()
        x = mouse_pos[0]
        y = mouse_pos[1]
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down_square = list(board_square(board,board_x,board_y,board_length,x,y,screen_height)) #square that is mouseddown on

        if event.type == pygame.MOUSEBUTTONUP:

            mouse_down_button = ""
            mouse_up_square = list(board_square(board,board_x,board_y,board_length,x,y,screen_height)) # square that is moused up on
            if (mouse_up_square == mouse_down_square and allow_board_clicks): #only register a "click" on a board square if these are equal
                first_square, second_square, mouse_down_square,mouse_up_square = handle_board_click(board,
                first_square,second_square,mouse_down_square,mouse_up_square)

    if(not(first_square ==[-1,-1]) and not(second_square ==[-1,-1]) and allow_board_clicks): # if both a first and second square are selected, move the piece on the 1st to the 2nd
        moving_color = board.pieces[first_square[0]][first_square[1]].color

        game_move_strs.append(board.move_string(first_square, second_square))
        board.move(first_square,second_square) # add checks that the move is legal later (if we ever get there)
        game_fens.append(board_elements.generate_fen((board)))
        print(game_fens[-1])
        fen_to_display += 1
        first_square = [-1,-1]
        second_square= [-1,-1]
    if(at_present_board and player_types[board.color_to_move.value]=="Computer"):
        engine_first,engine_second = engine.next_move(board)
        print(str(engine_first)+" "+str(engine_second))
        print("Start Col:"+str(board.color_to_move))
        board.move(engine_first,engine_second)
        print("End Col:"+str(board.color_to_move))

    selected_piece = first_square
    screen.fill((205,189,163))

    board_to_display = board_elements.import_fen(game_fens[fen_to_display])

    draw_board(board_to_display, board_x, board_y, board_length,screen,screen_height,selected_piece)
    draw_move_history(game_move_strs,0.75*screen_width,0.1*screen_height,game_button_width,game_button_height,screen,screen_height)
    pygame_widgets.update(events)
    pygame.display.update()

