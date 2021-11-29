import string
from typing import Tuple
from piece import Piece
import pygame
from pygame import freetype
from colours import Colour
from player_turn import player_turn
from string import ascii_uppercase
from rules_check import *


class Text:
    def __init__(self, text: str, position: tuple):
        self.string = text
        self.position = position


class Board:
    def __init__(self, background: pygame.image, size: int, font_path: string, piece_sound_effect_path):
        self.size = size - 1
        self.font = freetype.Font(font_path, 24)
        self.numbers = ['' for i in range(self.size + 1)]
        self.letters = ['' for x in range(self.size + 1)]
        self.board = [[0 for x in range(self.size)] for y in range(self.size)]
        self.board_intersections = [[0 for x in range(self.size + 1)] for y in range(self.size + 1)]
        self.background = background
        self.background_rect = background.get_rect()
        w, h = pygame.display.get_surface().get_size()
        self.tile_size = (w / self.size) * 0.9
        self.offset = 30
        self.set_up_grid()
        self.piece_matrix = [[Piece((-10, -10), Colour.CLEAR, row, col) for col in range(self.size + 1)] for row in
                             range(self.size + 1)]
        self.play_piece_sound = pygame.mixer.Sound(piece_sound_effect_path)
        self.current_colour = player_turn.BLACK

    def render(self, screen: pygame.display) -> None:
        screen.blit(self.background, self.background_rect)
        [[pygame.draw.rect(screen, pygame.Color(0, 0, 0), col, 3) for col in row] for row in self.board]

        for row in self.piece_matrix:
            for piece in row:
                piece.render(screen)
        [self.font.render_to(screen, number.position, number.string, (0, 0, 0)) for number in self.numbers]
        [self.font.render_to(screen, letter.position, letter.string, (0, 0, 0)) for letter in self.letters]

    def check_mouse_position(self, mouse_position, current_colour: player_turn) -> bool:
        for x in range(self.size + 1):
            for y in range(self.size + 1):
                if self.board_intersections[x][y].collidepoint(mouse_position):
                    if self.piece_matrix[x][y].colour is Colour.CLEAR:
                        self.play_piece_sound.play()
                        return self.place_piece_at_position(current_colour, (x, y))
        return False

    def place_piece_at_position(self, current_colour: player_turn, position: tuple) -> bool:
        has_placed_piece = False
        if current_colour is player_turn.BLACK and self.is_move_legal(position, Colour.BLACK):
            self.piece_matrix[position[0]][position[1]].set_position(
                self.board_intersections[position[0]][position[1]].center)
            self.piece_matrix[position[0]][position[1]].set_colour(Colour.BLACK)
            has_placed_piece = True
        elif current_colour is player_turn.WHITE and self.is_move_legal(position, Colour.WHITE):
            self.piece_matrix[position[0]][position[1]].set_position(
                self.board_intersections[position[0]][position[1]].center)
            self.piece_matrix[position[0]][position[1]].set_colour(Colour.WHITE)
            has_placed_piece = True
        if has_placed_piece:
            group = self.create_group_from_piece(position[0], position[1], [],
                                                 self.piece_matrix[position[0]][position[1]].colour)
            for piece in group:
                print("Row: ", piece.col, " Col: ", piece.row, " Colour: ", piece.colour)
            liberties = self.get_liberties_for_group(group)
            print("Number of liberties for group: ", len(liberties))
            self.remove_captured_groups_from_board()
        return has_placed_piece

    def set_up_numbers(self) -> None:
        starting_position = (self.board_intersections[-1][-1].x, self.board_intersections[-1][-1].y)
        x = self.board[0][0].x
        y = starting_position[1] + 25
        letters = list(ascii_uppercase)
        letters = [letter for letter in letters if 'I' not in letter]  # I does not show up on the board so remove
        # from list
        for i in range(self.size + 1):
            x = self.offset + (i * self.tile_size)
            self.letters[i] = Text(text=letters[i], position=(x, y))

        x = self.board[0][0].x - 25
        y = self.board[0][0].y
        number = 19
        for i in range(self.size + 1):
            y = self.offset + (i * self.tile_size)
            self.numbers[i] = Text(text=str(number), position=(x, y))
            number -= 1

    def set_up_grid(self) -> None:
        for y in range(self.size + 1):
            y_position = self.offset + (y * self.tile_size)
            for x in range(self.size + 1):
                if x < self.size and y < self.size:
                    x_position = self.offset + (x * self.tile_size)
                    rect = pygame.Rect(x_position, y_position, self.tile_size, self.tile_size)
                    intersection = pygame.Rect(x_position - 5, y_position - 5, 10, 10)
                    self.board[x][y] = rect
                    self.board_intersections[x][y] = intersection
                else:
                    x_position = self.offset + (x * self.tile_size)
                    intersection = pygame.Rect(x_position - 5, y_position - 5, 10, 10)
                    self.board_intersections[x][y] = intersection
        self.set_up_numbers()

    def get_piece_at_position(self, row: int, col: int) -> Piece:
        return self.piece_matrix[row][col]

    def is_koish(self, row: int, col: int) -> Colour:
        piece = self.get_piece_at_position(row, col)
        if piece.colour is not Colour.CLEAR:
            return None
        colour = Colour.CLEAR
        if row - 1 > 0 and self.get_piece_at_position(row - 1, col).colour is not Colour.CLEAR:
            colour = self.get_piece_at_position(row - 1, col).colour
        if col - 1 > 0 and self.get_piece_at_position(row, col - 1).colour is not colour:
            return None
        if row + 1 < self.size and self.get_piece_at_position(row + 1, col).colour is not colour:
            return None
        if col + 1 < self.size and self.get_piece_at_position(row, col + 1).colour is not colour:
            return None
        return colour

    def get_adjacent_of_colour(self, row: int, col: int, colour: Colour) -> list:
        adjacent_pieces = []
        if row - 1 >= 0 and self.get_piece_at_position(row - 1, col).colour is colour:
            adjacent_pieces.append(self.get_piece_at_position(row - 1, col))
        if col - 1 >= 0 and self.get_piece_at_position(row, col - 1).colour is colour:
            adjacent_pieces.append(self.get_piece_at_position(row, col - 1))
        if row + 1 <= self.size and self.get_piece_at_position(row + 1, col).colour is colour:
            adjacent_pieces.append(self.get_piece_at_position(row + 1, col))
        if col + 1 <= self.size and self.get_piece_at_position(row, col + 1).colour is colour:
            adjacent_pieces.append(self.get_piece_at_position(row, col + 1))
        return adjacent_pieces

    def is_move_legal(self, position: tuple, colour: Colour) -> bool:
        if self.get_piece_at_position(position[0], position[1]).colour is not Colour.CLEAR:
            return False
        liberties = self.get_adjacent_of_colour(position[0], position[1], Colour.CLEAR)
        surrounded_by_same_colour = self.get_adjacent_of_colour(position[0], position[1], colour)
        opposite_colour = Colour.BLACK if colour is Colour.WHITE else Colour.WHITE
        if not liberties and not surrounded_by_same_colour:
            return False
        if len(self.get_adjacent_of_colour(position[0], position[1], opposite_colour)) == 4:
            return False
        return True

    def get_liberties_for_group(self, group: list) -> set:
        liberties = set()

        for piece in group:
            piece_liberties = self.get_adjacent_of_colour(piece.row, piece.col, Colour.CLEAR)
            [liberties.add(liberty) for liberty in piece_liberties]

        return liberties

    def create_group_from_piece(self, row: int, col: int, group: list, colour: Colour) -> list:
        if row > self.size or row < 0 or col < 0 or col > self.size:
            return list()
        if not group:
            group = [self.get_piece_at_position(row, col)]
        else:
            group.append(self.get_piece_at_position(row, col))
        adjacent_pieces = self.get_adjacent_of_colour(row, col, colour)
        for piece in adjacent_pieces:
            if piece not in group:
                self.create_group_from_piece(piece.row, piece.col, group, colour)
        return group

    def get_all_groups_on_board(self):
        groups = [[]]
        has_been_checked = [[False for row in range(self.size)] for col in range(self.size)]

        for row in range(self.size):
            for col in range(self.size):
                if self.piece_matrix[row][col].colour is not Colour.CLEAR:
                    if has_been_checked[row][col] is False:
                        group = self.create_group_from_piece(row, col, [], self.piece_matrix[row][col].colour)
                        has_been_checked[row][col]
                        groups.append(group)
        return groups

    def get_liberties_for_group(self, group) -> list:
        all_liberties = []
        for piece in group:
            liberties = self.get_adjacent_of_colour(piece.row, piece.col, Colour.CLEAR)
            all_liberties.extend(liberties)
        return list(set(all_liberties))

    def get_legal_spots_to_play(self):
        possible_moves = []
        free_spaces = [piece for piece in self.piece_matrix if piece.colour is Colour.CLEAR]
        for piece in free_spaces:
            if len(self.get_adjacent_of_colour(piece.row, piece.col, Colour.CLEAR)) > 0:
                possible_moves.append(tuple(piece.row, piece.col))

    def remove_pieces(self, group: list):
        for piece in group:
            piece.colour = Colour.CLEAR

    def remove_captured_groups_from_board(self):
        groups = self.get_all_groups_on_board()
        for group in groups:
            if len(group) > 0:
                if self.current_colour is player_turn.BLACK and group[0].colour is not Colour.BLACK \
                        or self.current_colour is player_turn.WHITE and group[0].colour is not Colour.WHITE:
                    liberties = self.get_liberties_for_group(group)
                    if len(liberties) == 0:
                        self.remove_pieces(group)

        for group in groups:
            if len(group) > 0:
                if self.current_colour is player_turn.BLACK and group[0].colour is Colour.BLACK \
                        or self.current_colour is player_turn.WHITE and group[0].colour is Colour.WHITE:
                    liberties = self.get_liberties_for_group(group)
                    if len(liberties) == 0:
                        self.remove_pieces(group)