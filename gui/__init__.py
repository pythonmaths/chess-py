"""Pygame game loop for gui"""

import pygame
from pygame import MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION
from chessboard import Board
from gui.gui_settings import SCREEN_HEIGHT, SCREEN_WIDTH
from gui.gui_screens import PromotionScreen, EndGameScreen
import gui.gui_functions as gf
from uci import UCI
import utils

def run(board):
    """Initialize game, settings and create a screen object"""
    pygame.init()
    reset_gui_pieces(board)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('Chess')
    pygame.display.set_icon(pygame.image.load(r'art/WhiteKnightIcon.png'))

    promotion_screen = PromotionScreen(screen)
    endgame_screen = EndGameScreen(screen)
    endgame_result = None

    running = True
    legal_moves = LegalMoves([])
    while running:
        turn_clock = board.turn_clock
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False  # Quit pygame if window in closed
            elif event.type in [MOUSEBUTTONDOWN, MOUSEBUTTONUP, MOUSEMOTION]:
                if not (promotion_screen.block or endgame_screen.block):
                    gf.handle_mouse_event(event, board, legal_moves)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if promotion_screen.block:
                        promotion_choice = promotion_screen.get_selection()
                        if promotion_choice is not None:
                            board.promote_pawn(promotion_choice=promotion_choice)
                            reset_gui_pieces(board)
                            promotion_screen.reset()
                    elif endgame_screen.block:
                        endgame_screen.handle_selection()
                        if endgame_screen.restart_button.clicked:
                            board.reset()
                            reset_gui_pieces(board)
                            endgame_result = None
                            endgame_screen.reset()
                        elif endgame_screen.quit_button.clicked:
                            running = False
        if not running:
            break
        if not (board.players.current_player.is_human or
                endgame_screen.block):
            #for event in pygame.event.get():
                #if event.type == MOUSEBUTTONDOWN and event.button == 2:
            board.do_computer_move()
            reset_gui_pieces(board)
        gf.update_screen(screen, board, legal_moves)
        # This is here mainly to reduce the lag coming from the check_endgame
        if endgame_result is None and not promotion_screen.block:
            pygame.display.update()
        if board.pieces.pawn_needs_promotion():
            promotion_screen.block = True
            promotion_screen.blit(board.players.get_idle_player().allegiance)
        if turn_clock != board.turn_clock:
            endgame_result = board.check_endgame()
        if endgame_result is not None:
            endgame_screen.block = True
            endgame_screen.blit(endgame_result,
                                board.players.get_idle_player().allegiance)
        pygame.display.update()
    pygame.quit()

def reset_gui_pieces(board):
    """Resets all the gui specific piece information"""
    for piece in board.pieces:
        gf.init_gui_piece(piece)


class LegalMoves():
    """Simple container that acts like a list"""

    def __init__(self, lst):
        self.lst = lst

    def __getitem__(self, item):
        return self.lst[item]

    def update(self, lst):
        """Override list with provided list"""
        self.lst = lst

    def clear(self):
        """Clear list"""
        self.lst = []
