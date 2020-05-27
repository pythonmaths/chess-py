"""Pawn sprite and moves"""

from chessboard.piece import Piece
from settings import PAWN_RANK

class Pawn(Piece):
    """Pawn class"""

    def __init__(self, init_position=None, allegiance=None):
        super(Pawn, self).__init__()
        self.pos_idx = init_position
        self.allegiance = allegiance

        self.enpassant = False
        self.enpassant_move = []
        self.enpassant_enemy = None
        self.enpassant_sq = None

        self.up_for_promotion = False

    def __str__(self):
        return 'pawn'

    def get_char(self):
        """Return the character epresentation of this piece"""
        return 'P' if self.allegiance == 'white' else 'p'

    def get_move_pool(self, pos_idx=False):
        """Get move pool"""
        return {'fwd': self.fwd(1, 2, pos_idx=pos_idx),
                'dgfl': self.dgfl(1, pos_idx=pos_idx),
                'dgfr': self.dgfr(1, pos_idx=pos_idx)}

    def update_legal_moves(self, report):
        """Calculate this pieces legal moves given a report"""
        self._clear_moves()
        for direction, pos_reports in report.items():
            for i, pos_report in enumerate(pos_reports):
                location = [pos_report['loc']]
                if direction == 'dgfl':
                    if pos_report['enemy_occupied']:
                        self.legal_moves += location
                    elif pos_report['ally_occupied']:
                        self.allies_in_legal_moves += location
                    self.illegal_enemy_king_moves += location
                if direction == 'dgfr':
                    if pos_report['enemy_occupied']:
                        self.legal_moves += location
                    elif pos_report['ally_occupied']:
                        self.allies_in_legal_moves += location
                    self.illegal_enemy_king_moves += location
                if direction == 'fwd':
                    if pos_report['occupied'] or (i > 0 and not self.on_home_rank()):
                        break
                    self.legal_moves += location

    def on_home_rank(self):
        """
        Retrun True if the pawn is currently situated on the rank on which it
        starts
        """
        return self.is_on_rank(str(PAWN_RANK[self.allegiance]))

    def enable_enpassant(self, enpassant_move, enpassant_enemy):
        """Function to enable enpassant for this pawn"""
        self.enpassant = True
        self.enpassant_move.append(enpassant_move)
        self.enpassant_enemy = enpassant_enemy

    def reset_enpassant(self):
        """Function to reset enpassant for this pawn"""
        self.enpassant = False
        self.enpassant_move = []
        self.enpassant_enemy = None
        self.enpassant_sq = None

    def add_enpassant_move(self):
        """Add the enpassant move to the legal moves"""
        self.legal_moves += self.enpassant_move
