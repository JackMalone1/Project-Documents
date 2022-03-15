import math
from copy import copy, deepcopy
from datetime import datetime, timedelta
from random import choice, random

from board import Board
from colours import Colour
from go_rules import GoRules
from node import Node
from playerturn import PlayerTurn


class MonteCarloTreeSearch:
    def __init__(self, board: Board, colour: Colour):
        self.calculation_time = 20
        self.board = board
        self.board.piece_matrix = deepcopy(board.piece_matrix)
        self.states = []
        self.max_moves = 10
        self.colour = colour
        self.player_turn = (
            PlayerTurn.WHITE if self.colour == Colour.WHITE else PlayerTurn.BLACK
        )
        self.start_time = datetime.utcnow()
        self.exploration = 320
        self.size = 0
        self.current_colour = PlayerTurn.BLACK
        self.use_early_cutoff = False
        self.current_step = 0
        self.minimum_steps = 15
        self.moves_calculated = 0
        self.calculation_time = 5

    def get_moves_calculated(self) -> int:
        return self.moves_calculated

    def get_best_move_in_time(self, board):
        rules = GoRules(copy(board.piece_matrix), board.size)
        self.current_step = 0
        self.size = board.size
        available_moves = rules.get_legal_spots_to_play(copy(board.piece_matrix))
        best_value = -math.inf
        best_move = Node(
            None,
            self.player_turn,
            choice(available_moves),
            copy(board.piece_matrix),
        )
        moves = []
        self.current_colour = board.current_colour
        self.moves_calculated = 0

        if len(available_moves) > 0:
            root = Node(
                None,
                self.player_turn,
                choice(available_moves),
                copy(board.piece_matrix),
            )
            self.player_turn = (
                PlayerTurn.WHITE if self.colour == Colour.WHITE else PlayerTurn.BLACK
            )

            if root is not None:
                difference = datetime.utcnow() - self.start_time

                for _ in range(self.exploration):
                    if difference < timedelta(seconds=self.calculation_time):
                        n = self.expansion(copy(root))
                        root.children.extend(n.children)
                        n.backup(self.run_simulation(n))
                        difference = datetime.utcnow() - self.start_time
                        self.moves_calculated += 1

                for node in root.children:
                    if node.visited == 0:
                        continue
                    ucb = node.uct1(math.sqrt(2))
                    if ucb > best_value:
                        best_move = node
                        best_value = ucb

                moves.append((0, best_move.position))
        return best_move

    def expansion(self, node: Node):
        rules = GoRules(node.board, self.size)
        moves = rules.get_legal_spots_to_play(node.board)
        original_board = node.board
        node.board = deepcopy(node.board)

        while len(moves) > 0:
            node.get_more_moves(rules.get_legal_spots_to_play(node.board))
            if len(node.possible_moves) > 0:
                node.board = original_board
                return node.expand_node()
            else:
                node = node.get_best_child()
        node.board = original_board
        return node

    def run_simulation(self, node: Node):
        states_copy = deepcopy(node.board)
        rules = GoRules(states_copy, self.size)

        while len(rules.get_legal_spots_to_play(states_copy)) > 0:
            possible_moves = rules.get_legal_spots_to_play(states_copy)
            move = choice(possible_moves)
            if self.current_colour == PlayerTurn.BLACK:
                states_copy[move[0]][move[1]].colour = Colour.BLACK
                self.current_colour = PlayerTurn.WHITE
            else:
                states_copy[move[0]][move[1]].colour = Colour.WHITE
                self.current_colour = PlayerTurn.BLACK
        return rules.score(states_copy)

    def early_cutoff(self) -> bool:
        if not self.use_early_cutoff:
            return False
        if self.current_step < self.minimum_steps:
            return False
        if self.is_goal_stable():
            return self.current_step >= 10

    def is_goal_stable(self):
        return True
