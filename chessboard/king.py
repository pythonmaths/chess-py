"""King sprite and moves"""

from chessboard.piece import Piece
from settings import CASTLING_POSITIONS

class King(Piece):
    """King class"""

    def __init__(self, init_position=None, allegiance=None):
        super(King, self).__init__()
        self.pos_idx = init_position
        self.allegiance = allegiance
        self.home_square = None

        self.king_side_castle_allowed = False  # Switched on by FEN record
        self.king_side_castle_valid = False
        self.king_side_rook_piece = None
        self.king_side_rook_pos = None
        self.king_side_transition = None
        self.king_side_empty_squares = None

        self.queen_side_castle_allowed = False  # Switched on by FEN record
        self.queen_side_castle_valid = False
        self.queen_side_rook_piece = None
        self.queen_side_rook_pos = None
        self.queen_side_transition = None
        self.queen_side_empty_squares = None

        if self.allegiance is not None:
            self._get_castling_positions()

        self.in_check = False
        self.checked_by = None
        self.enemy_attacks = []

        self.checkmate = False
        self.stalemate = False

    def __str__(self):
        return 'king'
    
    def get_char(self):
        """Return the character epresentation of this piece"""
        return 'K' if self.allegiance == 'white' else 'k'

    def get_move_pool(self, pos_idx=False):
        """Get move pool"""
        return {'fwd': self.fwd(1, pos_idx=pos_idx),
                'bkwd': self.bkwd(1, pos_idx=pos_idx),
                'left': self.left(1, pos_idx=pos_idx),
                'right': self.right(1, pos_idx=pos_idx),
                'dgfl': self.dgfl(1, pos_idx=pos_idx),
                'dgfr': self.dgfr(1, pos_idx=pos_idx),
                'dgbl': self.dgbl(1, pos_idx=pos_idx),
                'dgbr': self.dgbr(1, pos_idx=pos_idx)}

    def _get_castling_positions(self):
        """Update the king's castling positional information"""
        self.home_square = CASTLING_POSITIONS[self.allegiance][
            'king_home_square']

        self.king_side_rook_pos = CASTLING_POSITIONS[self.allegiance][
            'king_side_rook_pos']
        self.king_side_transition = CASTLING_POSITIONS[self.allegiance][
            'king_side_transition']
        self.king_side_empty_squares = CASTLING_POSITIONS[self.allegiance][
            'king_side_empty_squares']

        self.queen_side_rook_pos = CASTLING_POSITIONS[self.allegiance][
            'queen_side_rook_pos']
        self.queen_side_transition = CASTLING_POSITIONS[self.allegiance][
            'queen_side_transition']
        self.queen_side_empty_squares = CASTLING_POSITIONS[self.allegiance][
            'queen_side_empty_squares']

    def update_check(self):
        """Set in check if currently positioned in an enemy attack"""
        self.in_check = self.pos_idx in self.enemy_attacks

    def update_legal_moves(self, report):
        """Calculate this pieces legal moves given a report"""
        self._clear_moves()
        for pos_reports in report.values():
            for pos_report in pos_reports:
                location = [pos_report['loc']]
                if pos_report['ally_occupied']:
                    self.allies_in_legal_moves += location
                    break
                if pos_report['enemy_occupied']:
                    self.legal_moves += location
                    break
                self.legal_moves += location
                self.illegal_enemy_king_moves += location

    def disable_castle_move(self, side=None):
        """Disable both castle moves for this king since once you have done
        one you can't do the other. Or disable a given side"""
        if side == 'king' or side is None:
            self.king_side_castle_valid = False
            self.king_side_rook_piece = None
        if side == 'queen' or side is None:
            self.queen_side_castle_valid = False
            self.queen_side_rook_piece = None

    def add_castling_legal_moves(self):
        """
        If the castling move for each side is valid and allowed then add the
        move to the legal moves
        """
        if self.king_side_castle_allowed and self.king_side_castle_valid:
            self.legal_moves += [self.king_side_transition[-1]]
        if self.queen_side_castle_allowed and self.queen_side_castle_valid:
            self.legal_moves += [self.queen_side_transition[-1]]
