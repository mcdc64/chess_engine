import random

import numpy as np
import pygame
import board_elements

import time
import copy
from pygame.locals import K_p
from enum import Enum

class Button(pygame.sprite.Sprite):
    def __init__(self,name,x1,y1,width,height,image_path,click_fcn):
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x1,y1,width,height)
        self.image_path = image_path
        self.image = pygame.transform.scale(pygame.image.load(image_path),(width,height))
        self.click_fcn = click_fcn

    def draw(self,screen):
        screen.blit(self.image,self.rect)



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


def board_square(board,x1,y1,board_length,pyg_x,pyg_y,screen_height): # find the board square containing given x and y screen coords
    x,y = coords_to_pygame((pyg_x,pyg_y),screen_height) # convert the screen coords to space coords

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
    on_menu = False;
def flip_board(board):
    if(board.color_at_bottom==board_elements.Color.WHITE):
        board.color_at_bottom=board_elements.Color.BLACK
    else:
        board.color_at_bottom=board_elements.Color.WHITE

def handle_board_click(board,first_sq, second_sq, mouse_down_sq, mouse_up_sq):
    if (first_sq == [-1, -1]):  # if no square is selected up to now, select the clicked square
        if not (board.pieces[mouse_up_sq[0]][mouse_up_sq[1]].piece_type == board_elements.PieceType.EMPTY):
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

screen_width = 1280
screen_height = 720
board_length = 512 # MUST BE A MULTIPLE OF 8!! Divisibility by 8 ensures the 64 squares are of integer length
board_x = (screen_width-board_length)//2
board_y = 100
screen = pygame.display.set_mode([screen_width, screen_height])
running = True
on_menu = True

mouse_down_button = ""
mouse_down_square = [-1,-1]
mouse_up_square = [-1,-1]
first_square = [-1,-1]
second_square = [-1,-1]

menu_buttons = [Button("Start",500,300,80,40,"images/start_button.png",start_game)]
game_buttons = [Button("Flip Board",int((screen_width)*0.75),500,120,40,"images/flip_button.png",flip_board)]

pieces = board_elements.initialise_pieces()
fen_str = "6k1/2rp1ppp/b2P3n/pp6/5n2/PBN2N2/1P3PPP/R3R1K1 b - - 0 27"
board = board_elements.Board(pieces)
selected_piece = [-1,-1]
while running:
    if on_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONUP:
                for button in menu_buttons:
                    mouse_pos = pygame.mouse.get_pos()
                    if button.rect.collidepoint(mouse_pos):
                       button.click_fcn()
        screen.fill((80, 182, 153))
        for button in menu_buttons:
            button.draw(screen)
        pygame.display.flip()
        continue

    for event in pygame.event.get():
        mouse_pos = pygame.mouse.get_pos()
        x = mouse_pos[0]
        y = mouse_pos[1]
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_down_square = list(board_square(board,board_x,board_y,board_length,x,y,screen_height)) #square that is mouseddown on
            for button in game_buttons:
                if button.rect.collidepoint(mouse_pos):
                    mouse_down_button = button.name
        if event.type == pygame.MOUSEBUTTONUP:
            for button in game_buttons: # execute the function of any button the mouse is over

                if button.rect.collidepoint(mouse_pos) and (mouse_down_button == button.name):
                    button.click_fcn(board)
            mouse_down_button = ""
            mouse_up_square = list(board_square(board,board_x,board_y,board_length,x,y,screen_height)) # square that is moused up on
            if (mouse_up_square == mouse_down_square): #only register a "click" on a board square if these are equal
                first_square, second_square, mouse_down_square,mouse_up_square = handle_board_click(board,
                first_square,second_square,mouse_down_square,mouse_up_square)

    if(not(first_square ==[-1,-1]) and not(second_square ==[-1,-1])): # if both a first and second square are selected, move the piece on the 1st to the 2nd
        board.move(first_square,second_square,False) # add checks that the move is legal later (if we ever get there)
        first_square = [-1,-1]
        second_square= [-1,-1]

    selected_piece = first_square
    screen.fill((140,122,103))
    draw_board(board, board_x, board_y, board_length,screen,screen_height,selected_piece)

    for button in game_buttons:
        button.draw(screen)
    pygame.display.flip()

