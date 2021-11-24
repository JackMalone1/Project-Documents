from os import system
import pygame

from pygame.constants import FULLSCREEN, RESIZABLE
from board import Board
from player_turn import player_turn

import dearpygui.dearpygui as dpg


def main():
    pygame.init()
    logo = pygame.image.load("logo32x32.png")
    pygame.display.set_icon(logo)
    pygame.display.set_caption("test program")

    screen = pygame.display.set_mode((800, 800), RESIZABLE)

    running = True
    background = pygame.image.load("Assets//background.jpg")
    board = Board(background=background, size=19, font_path="MONOFONT.ttf",
                  piece_sound_effect_path="Assets//Sounds//place_piece.ogg")

    current_colour = player_turn.BLACK

    clock = pygame.time.Clock()

    while running:
        time_delta = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                width, height = event.size
                if width < 800:
                    width = 800
                if height < 800:
                    height = 800
                screen = pygame.display.set_mode((width, height), RESIZABLE)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                placed_piece = board.check_mouse_position(pygame.mouse.get_pos(), current_colour)
                if placed_piece:
                    if current_colour is player_turn.BLACK:
                        current_colour = player_turn.WHITE
                    elif current_colour is player_turn.WHITE:
                        current_colour = player_turn.BLACK

        board.render(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
