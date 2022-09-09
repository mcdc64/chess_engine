import random

import numpy as np
import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.button import ButtonArray
from pygame_widgets.textbox import TextBox
from pygame_widgets.slider import Slider
from pygame_widgets.toggle import Toggle
import board_elements
import simple_board
from board_elements import Board,Color,Piece,PieceType
import computer_engine
import move_generator

import time
import copy
from pygame.locals import K_p
from enum import Enum





def coords_to_pygame(coords,height): #switches from space coords (positive y is up) to pygame coords (positive y down)
    return (coords[0],height-coords[1])


def draw_board(board, x1,y1, board_length, screen, screen_height,selected_piece,moving_squares,moving_piece,move_progress):
    if(selected_piece!=[-1,-1] and draw_move_choices):
        move_choices = [[move[0],move[1]] for move in move_generator.one_legal_moves(board,selected_piece[0],selected_piece[1])]
    else:
        move_choices = []
    squares_to_highlight = [choice[1] for choice in move_choices] # all possible squares the selected piece can move to
    square_length = board_length // 8
    origin_square = moving_squares[0] # used to calculate the path of the current moving piece if there is one
    target_square = moving_squares[1]
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
                curr_col = (50,200,150) # color the selected piece's square green
            elif (board.color_at_bottom == board_elements.Color.WHITE and selected_piece == [i, j]):
                curr_col = (50, 200, 150)
            elif((board.color_at_bottom == board_elements.Color.BLACK and [7-i,7-j] in squares_to_highlight)or board.color_at_bottom == board_elements.Color.WHITE and [i, j] in squares_to_highlight):
                # color the possible move squares differently
                if((i+j)%2 == 1):
                    curr_col = (200,200,200)
                else:
                    curr_col = (50,100,130)
            pygame.draw.rect(screen, curr_col, curr_rect)

            piece_filename = "images/empty.png"


            if (curr_piece.piece_type != board_elements.PieceType.EMPTY): # load the images of the different pieces
                if([i,j]!=origin_square and [i,j]!=target_square and board.color_at_bottom == board_elements.Color.WHITE):
                    piece_filename = "images/" + curr_piece.color.name.lower() + "_" + curr_piece.piece_type.name.lower() + ".png"
                if([7-i,7-j]!=origin_square and [7-i,7-j]!=target_square and board.color_at_bottom == board_elements.Color.BLACK):
                    piece_filename = "images/" + curr_piece.color.name.lower() + "_" + curr_piece.piece_type.name.lower() + ".png"

            piece_img = pygame.transform.scale(pygame.image.load(piece_filename), (square_length, square_length))
            piece_rect = pygame.Rect(x_coord, y_coord, square_length, square_length)
            screen.blit(piece_img, piece_rect) # draw each piece...


        origin_coords = coords_to_pygame((x1 + (square_length * origin_square[0]), y1 + (square_length * origin_square[1])), screen_height)
        target_coords = coords_to_pygame((x1 + (square_length * target_square[0]), y1 + (square_length * target_square[1])), screen_height)
        if (board.color_at_bottom == board_elements.Color.BLACK):
            origin_coords = coords_to_pygame((x1 + (square_length * (7 - origin_square[0])), y1 + (square_length * (7 - origin_square[1]))),screen_height)
            target_coords = coords_to_pygame((x1 + (square_length * (7 - target_square[0])), y1 + (square_length * (7 - target_square[1]))),screen_height)

        moving = (target_square != [-1,-1])
        if (moving):

            if(0<=move_progress<1): # linear weight the origin and target coords by move_progress
                move_x = (1 - move_progress) * origin_coords[0] + move_progress * target_coords[0]
                move_y = (1 - move_progress) * origin_coords[1] + move_progress * target_coords[1]
            else:
                move_x = target_coords[0]
                move_y = target_coords[1]
            move_rect = pygame.Rect(move_x, move_y, square_length, square_length)

            move_filename = "images/" + moving_piece.color.name.lower() + "_" + moving_piece.piece_type.name.lower() + ".png"
            move_img = pygame.transform.scale(pygame.image.load(move_filename), (square_length, square_length))
            screen.blit(move_img, move_rect) # draw the moving piece

def open_promote_menu(promote_color): # allow users to promote when a pawn reaches the end of the board
    global promote_array,game_button_width,game_button_height
    if(promote_color == board_elements.Color.BLACK):
        img_names = ["images/black_queen.png","images/black_rook.png","images/black_bishop.png","images/black_knight.png"]
    if (promote_color == board_elements.Color.WHITE):
        img_names = ["images/white_queen.png", "images/white_rook.png", "images/white_bishop.png",
                     "images/white_knight.png"]
    promote_imgs = []
    for img_name in img_names:
        promote_imgs.append(pygame.transform.scale(pygame.image.load(img_name),(int(game_button_width*0.75),int(game_button_width*0.75))))
    promote_array = ButtonArray(screen, int(screen_width) * 0.02, int(0.25 * screen_height), game_button_width,
4* game_button_width, (1, 4),images = promote_imgs, onClicks=(set_promote_piece,set_promote_piece,set_promote_piece,set_promote_piece),
                                onClickParams=([board_elements.PieceType.QUEEN], [board_elements.PieceType.ROOK],
                                               [board_elements.PieceType.BISHOP], [board_elements.PieceType.KNIGHT]))
    return promote_array

def set_promote_piece(piece_type):
    global promote_piece
    global promote_array
    promote_piece = piece_type
    promote_array.hide()

def draw_move_history(game_move_strs,x1,y1,box_width,box_height,screen,screen_height,position_offset,num_moves=30):
    # draws the record of moves played during the game
    num_offset = position_offset
    position_offset = 2*position_offset
    font = pygame.font.SysFont(None, int(40*screen_height/880))
    for i in range(0,num_moves//2):
        if(len(game_move_strs)>(2*i)+1+position_offset):
            first_str = game_move_strs[2*i+position_offset]
            second_str = game_move_strs[(2*i)+1+position_offset]
        elif(len(game_move_strs)>(2*i+position_offset)):
            first_str = game_move_strs[2*i+position_offset]
            second_str = ""
        else:
            first_str = ""
            second_str = ""
        x_coord,y_coord = x1,(y1+i*box_height)
        second_x_coord = x1+box_width
        number_label = font.render(str(i+1+num_offset)+".",False,(0,0,0))
        first_label = font.render(first_str, False, (0, 0, 0))
        second_label = font.render(second_str, False, (0, 0, 0))

        number_rect = pygame.Rect(x_coord - int(1.25*box_height),y_coord+box_height//4,box_height,box_height)
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
def flip_board():
    global board
    if(board.color_at_bottom==board_elements.Color.WHITE):
        board.color_at_bottom=board_elements.Color.BLACK
    else:
        board.color_at_bottom=board_elements.Color.WHITE

def reset_game(): # start the game over in case we want to play again
    global board,game_fens,fen_to_display,first_square,second_square,game_move_strs,game_over,allowed_moves
    game_over = False
    bottom_col = board.color_at_bottom
    board = board_elements.Board(board_elements.initialise_pieces(),color_at_bottom=bottom_col)
    game_fens = [board_elements.generate_fen(board)]
    allowed_moves = move_generator.generate_legal_moves(board)
    game_move_strs = []
    fen_to_display = 0
    first_square = [-1,-1]
    second_square = [-1,-1]


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
pygame.display.set_caption("Chess")
clock = pygame.time.Clock()
clock.tick(60)
font = pygame.font.SysFont(None, 50)

aspect_ratio = 1.6
screen_height = 880
screen_width = aspect_ratio*screen_height
board_length = int(0.85*screen_height)-int(0.85*screen_height)%8 # MUST BE A MULTIPLE OF 8!! Divisibility by 8 ensures the 64 squares are of integer length
board_x = (screen_width-board_length)//4
board_y = 150
screen = pygame.display.set_mode(([screen_width, screen_height]))#,pygame.FULLSCREEN)
running = True
on_menu = True

mouse_down_button = ""
mouse_down_square = [-1,-1]
mouse_up_square = [-1,-1]
first_square = [-1,-1]
second_square = [-1,-1]
origin_square = [-1, -1]
target_square = [-1, -1]

first_trans_square = [-1,-1]
second_trans_square = [-1,-1]

draw_move_choices = True
translate_pieces = True #slide moved pieces to their destination instead of "teleporting" them
move_speed = 5
move_progress = 1
moving_piece = board_elements.Piece(board_elements.Color.NONE,board_elements.PieceType.EMPTY)

game_over = False
promoting_menu_open = False
promote_piece = board_elements.PieceType.EMPTY
promote_position = [-1,-1]

pieces = board_elements.initialise_pieces()
#fen_str = "rnbk2nr/ppp2Bpp/8/2b8/4N8/5Q8/PPPP1PPP/R1B1K2R b KQkq - 0 8"
fen_str = "8/1K6/8/2Q5/8/3k4/2p5/8 w - - 0 8"
#fen_str = "8/2p5/8/KP5r/8/8/8/7k b - - 0 8"
fen_str = "rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8"
board = board_elements.import_fen(fen_str)
simple_pieces = simple_board.initialise_pieces()

board = board_elements.simple_to_normal(s_board)
print(board.white_piece_positions)
allowed_moves = move_generator.generate_legal_moves(board)
#board = board_elements.Board(pieces)
game_fens = [board_elements.generate_fen(board)] # save all fen strings for the board so it can be replayed
fen_to_display = 0 # the current fen being displayed
game_move_strs = []
selected_piece = [-1,-1]

menu_buttons = [Button(screen,500,300,80,40,text="Start",fontSize=30,onClick=start_game)]

game_button_width = int(0.08*screen_width)
game_button_height = int(0.05*screen_height)
flip_button = Button(screen,int((screen_width)*0.66),int(0.86*screen_height),game_button_width,game_button_height,text="Flip Board",fontSize = 30,onClick=flip_board)
reset_button = Button(screen,int((screen_width)*0.66),int(0.86*screen_height+1.2*game_button_height),game_button_width,game_button_height,text="Reset",fontSize = 30,onClick=reset_game)
forward_back_array = ButtonArray(screen,int((screen_width)*0.75),int(0.88*screen_height),2*game_button_width,game_button_height,(2,1),fontSizes = (30,30),texts=("<",">"),onClicks=(change_fen,change_fen),onClickParams=([False],[True]))
promote_array = ButtonArray(screen,int(screen_width)*0.1,int(0.5*screen_height),game_button_width,4*game_button_width,(1,4),onClicks = (set_promote_piece,set_promote_piece,set_promote_piece,set_promote_piece),
                            onClickParams=[board_elements.PieceType.QUEEN,board_elements.PieceType.ROOK,board_elements.PieceType.BISHOP,board_elements.PieceType.KNIGHT])

last_board = None

slider_max = 85
history_slider = Slider(screen, int((screen_width)*0.93),int(0.1*screen_height+game_button_height//4),game_button_width//4,int(0.75*screen_height-(game_button_height//2)), vertical = True,min=0, max=slider_max, step=1,handleRadius = game_button_width//8)
history_slider.setValue(slider_max)

game_widgets= [flip_button,reset_button,forward_back_array,history_slider,promote_array]

player_types = ["Human","Human"] # first position is black, second position is white
engine = computer_engine.Engine(board_elements.Color.WHITE)
first_time = True
for widget in game_widgets:
    widget.hide()

while running:

    board_changed = False
    #print(clock.get_fps())
    delta_time = (clock.tick()/1000.0)
    events = pygame.event.get()
    if on_menu:
        for event in events:
            if event.type == pygame.QUIT:
                running = False

        screen.fill((80, 182, 153))
        pygame_widgets.update(events)

        pygame.display.update()
        continue

    if(first_time):
        allowed_moves = move_generator.generate_legal_moves(board)
        for button in menu_buttons:
            button.hide()
        for button in game_widgets:
            button.show()
        promote_array.hide()

    if(move_progress >= 1):
        move_progress = 1
        first_trans_square = [-1,-1]
        second_trans_square = [-1,-1]
    if(move_progress < 1):
        move_progress += move_speed*delta_time

    if(promoting_menu_open and (promote_piece != board_elements.PieceType.EMPTY)):
        promoting_menu_open = False
        allow_board_clicks = True

        promote_array.hide()



    allow_board_clicks = False
    at_present_board = (fen_to_display == len(game_fens)-1)
    if(at_present_board and player_types[board.color_to_move.value]=="Human" and not promoting_menu_open and not game_over): #if the display fen is the current board, allow moves
        allow_board_clicks = True
    if(not allow_board_clicks): #reset the first and second selected squares each frame to prevent board clicks
        first_square = [-1,-1]
        second_square= [-1,-1]


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

    if(first_square!=[-1,-1] and second_square!=[-1,-1]):
        origin_square = first_square # make copies of first and second square to prevent the values being overwritten
        target_square = second_square # need this for when the promotion menu is open



    if(not(origin_square ==[-1,-1]) and not(target_square ==[-1,-1]) and not game_over): # time to make a human move

        moving_piece = copy.deepcopy(board.pieces[origin_square[0]][origin_square[1]])
        moving_color = moving_piece.color

        pawn_moves = [[move[0],move[1]] for move in move_generator.one_legal_moves(board,origin_square[0],origin_square[1])]
        # if the move requires a promotion, open the promotion menu
        if (target_square[1] == 7 and moving_piece.piece_type == board_elements.PieceType.PAWN and moving_color == board_elements.Color.WHITE and not promoting_menu_open):
            if(promote_piece == PieceType.EMPTY and [origin_square,target_square] in pawn_moves):
                promote_array = open_promote_menu(moving_color)
                promote_array.show()
                promoting_menu_open = True
                allow_board_clicks = False
                initial_promote_position = origin_square
                promote_position = target_square


        if (target_square[1] == 0 and moving_piece.piece_type == board_elements.PieceType.PAWN and moving_color == board_elements.Color.BLACK and not promoting_menu_open):
            if(promote_piece == PieceType.EMPTY and [origin_square,target_square] in pawn_moves):
                promote_array = open_promote_menu(moving_color)
                promote_array.show()
                promoting_menu_open = True
                allow_board_clicks = False
                initial_promote_position = origin_square
                promote_position = target_square

        #generate allowed moves and check whether or not the given move is allowed
        allowed_moves = move_generator.generate_legal_moves(board)

        if(([origin_square,target_square,promote_piece] in allowed_moves) and not promoting_menu_open):

            game_move_strs.append(move_generator.move_string(board,origin_square, target_square, promote_choice=promote_piece))
            board.move(origin_square,target_square,promote_piece) # add checks that the move is legal later (if we ever get there)

            game_fens.append(board_elements.generate_fen((board)))
            print("Castling rights: "+str(board.castling_rights))
            if(promote_piece != board_elements.PieceType.EMPTY):

                promote_array.hide()
                promote_piece = board_elements.PieceType.EMPTY
                board_changed = True

            print(game_fens[-1])
            fen_to_display += 1


            if(translate_pieces):
                first_trans_square = first_square
                second_trans_square = second_square
                move_progress = 0
            board_changed = True

            origin_square = [-1,-1]
            target_square= [-1,-1]
            first_square = [-1,-1]
            second_square = [-1,-1]
        elif(([origin_square,target_square,promote_piece]not in allowed_moves) and not(promoting_menu_open or promote_piece!=PieceType.EMPTY)):
            origin_square = [-1, -1]
            target_square = [-1, -1]
            first_square = [-1,-1]
            second_square = [-1,-1]


    if(at_present_board and player_types[board.color_to_move.value]=="Computer" and move_progress == 1 and not game_over):


        engine_first,engine_second,engine_promote = engine.next_move(board)
        if(engine_first == [-1,-1]):
            continue
        comp_moving_piece = board.pieces[engine_first[0]][engine_first[1]]
        last_board = copy.deepcopy(board)
        if(comp_moving_piece.color == board.color_to_move):
            game_move_strs.append(move_generator.move_string(board,engine_first, engine_second,promote_choice=engine_promote))

            board.move(engine_first, engine_second,engine_promote)
            game_fens.append(board_elements.generate_fen((board)))
            fen_to_display += 1
            if(translate_pieces):
                first_trans_square = engine_first
                second_trans_square = engine_second
                moving_piece = copy.deepcopy(comp_moving_piece)
                move_progress = 0
            board_changed = True

    if(selected_piece != first_square):
        board_changed = True
        selected_piece = first_square

    if(board_changed):
        allowed_moves = move_generator.generate_legal_moves(board)

    if(allowed_moves == [] or board.halfmoves == 100):
        allow_board_clicks = False
        game_over = True
    screen.fill((205,189,163))

    board_to_display = board_elements.import_fen(game_fens[fen_to_display])
    board_to_display.color_at_bottom = board.color_at_bottom

    draw_board(board_to_display, board_x, board_y, board_length,screen,screen_height,selected_piece,[first_trans_square,second_trans_square],moving_piece,move_progress)
    draw_move_history(game_move_strs,0.75*screen_width,0.1*screen_height,game_button_width,game_button_height,screen,screen_height,slider_max-history_slider.getValue())


    if game_over:
        if(move_generator.in_check(board)):
            if(board.color_to_move == Color.WHITE):
                win_text = font.render("Checkmate - Black wins!",30,(0,0,0))
                screen.blit(win_text,(int(0.4*screen_width), int(0.05*screen_height)))
            if (board.color_to_move == Color.BLACK):
                win_text = font.render("Checkmate - White wins!",30,(0,0,0))
                screen.blit(win_text, (int(0.4*screen_width), int(0.05*screen_height)))
        else:
            stale_text = font.render("Stalemate!",30,(0,0,0))
            screen.blit(stale_text, (int(0.4*screen_width), int(0.05*screen_height)))
    first_time = False
    pygame_widgets.update(events)
    pygame.display.update()