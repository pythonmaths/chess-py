"""Bishop sprite and moves"""

from chessboard.piece import Piece

class Bishop(Piece):
    """Bishop class"""

    def __init__(self, init_position=None, allegiance=None):
        super(Bishop, self).__init__()
        self.pos_idx = init_position
        self.allegiance = allegiance

    def __str__(self):
        return 'bishop'

    def get_char(self):
        """Return the character epresentation of this piece"""
        return 'B' if self.allegiance == 'white' else 'b'

    def get_move_pool(self, pos_idx=False):
        """Get move pool"""
        return {'dgfl': self.dgfl(pos_idx=pos_idx),
                'dgfr': self.dgfr(pos_idx=pos_idx),
                'dgbl': self.dgbl(pos_idx=pos_idx),
                'dgbr': self.dgbr(pos_idx=pos_idx)}

    def update_legal_moves(self, report):
        """Calculate this pieces legal moves given a report"""
        self._clear_moves()
        for pos_reports in report.values():
            encountered_king = False
            for pos_report in pos_reports:
                location = [pos_report['loc']]
                # Pre king
                if not encountered_king:
                    if pos_report['enemy_king_occupied']:
                        self.legal_moves += location
                        encountered_king = True
                        break
                    elif pos_report['enemy_occupied']:
                        self.legal_moves += location
                        break
                    elif pos_report['ally_occupied']:
                        self.allies_in_legal_moves += location
                        break
                    self.legal_moves += location
                    self.illegal_enemy_king_moves += location
                # Go one square past king
                else:
                    self.illegal_enemy_king_moves += location
                    break
