"""FEN Building module"""

import re
import utils

class FENBuilder():
    """Container that creates a FEN standard string from a provided state"""
    def __init__(self, pieces, players, halfmove_clk, fullmove_num):
        self.pieces = pieces
        self.players = players
        self.halfmove_clk = halfmove_clk
        self.fullmove_num = fullmove_num

    def build(self):
        """Construct the FEN string from the board state"""
        return '%s %s %s %s %d %d' % (self._build_placement(),
                                      self.players.current_player.allegiance[0],
                                      self._build_castling_rights(),
                                      self._build_enpassant_sq(),
                                      self.halfmove_clk,
                                      self.fullmove_num)

    def _build_placement(self):
        """Construct the placement part of the FEN string"""
        piece_list = [(piece.get_char(), piece.pos_idx)
                      for piece in self.pieces]
        piece_list = sorted(piece_list, key=lambda piece: piece[1])
        board_list = [' ']*64
        for piece_name, piece_pos_idx in piece_list:
            board_list[piece_pos_idx] = piece_name
        for i in range(1, 8):
            board_list.insert((i*9)-1, '/')
        placement = re.sub(r'(\s+)', lambda m: str(len(m.group())), ''.join(board_list))
        return placement

    def _build_castling_rights(self):
        """Construct the castling availability part of the FEN string"""
        castling_rights = ''
        white_king = self.pieces.get_king('white')
        black_king = self.pieces.get_king('black')
        if white_king.king_side_castle_allowed:
            castling_rights += 'K'
        if white_king.queen_side_castle_allowed:
            castling_rights += 'Q'
        if black_king.king_side_castle_allowed:
            castling_rights += 'k'
        if black_king.queen_side_castle_allowed:
            castling_rights += 'q'
        if not castling_rights:
            castling_rights = '-'
        return castling_rights

    def _build_enpassant_sq(self):
        """Construct the algebraic enpassant square"""
        double_move_pawn = self.pieces.get_double_move_pawn()
        if double_move_pawn is None:
            return '-'
        return utils.idx_to_algebra(double_move_pawn.enpassant_sq)
