"""Knight sprite and moves"""

import utils
from chessboard.piece import Piece
from settings import KNIGHT_MOVES

class Knight(Piece):
    """Knight class"""

    def __init__(self, init_position=None, allegiance=None):
        super(Knight, self).__init__()
        self.pos_idx = init_position
        self.allegiance = allegiance

    def __str__(self):
        return 'knight'

    def get_char(self):
        """Return the character epresentation of this piece"""
        return 'N' if self.allegiance == 'white' else 'n'

    def get_move_pool(self, pos_idx=False):
        """Get move pool"""
        return {'knight_moves': self._get_knight_moves(pos_idx=pos_idx)}

    def _get_knight_moves(self, pos_idx=False):
        """Get the knights available moves"""
        moves = [self.pos_idx + m
                 for m in KNIGHT_MOVES if not clipped(self.pos_idx, self.pos_idx + m)]
        if pos_idx:
            return moves
        return utils.idx_to_algebra(*moves)

    def update_legal_moves(self, report):
        """Calculate this pieces legal moves given a report"""
        self._clear_moves()
        for pos_reports in report.values():
            for pos_report in pos_reports:
                location = [pos_report['loc']]
                if pos_report['ally_occupied']:
                    self.allies_in_legal_moves += location
                else:
                    self.legal_moves += location
                self.illegal_enemy_king_moves += location

def clipped(piece_idx, move_idx):
    """
    Determines whether the move is a valid knight move and is not clipped given
    the 8x8 geometry
    """
    if move_idx not in range(64):
        return True
    move_x, move_y = (move_idx % 8, move_idx // 8)
    piece_x, piece_y = (piece_idx % 8, piece_idx // 8)
    x_diff = (piece_x - move_x)
    y_diff = (piece_y - move_y)
    return bool(x_diff**2 > 9 or y_diff**2 > 9)
