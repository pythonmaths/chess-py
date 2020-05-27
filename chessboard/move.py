"""Module for the Move container"""

from settings import MAX_RANK

class Move():
    """
    Container to perform a simple chess move and store some state about that move
    in order to revert it
    """

    def __init__(self, positions, piece, end_idx, promotion_piece=None):
        self.piece = piece
        self.positions = positions
        self.end_idx = end_idx
        self.promotion_piece = promotion_piece

        self.start_idx = self.piece.pos_idx
        self.end_piece = self.positions[self.end_idx]

        self.switch_players = True
        self.disable_castle_move = False
        self.capture = False
        self.pawn_advance = False
        self.move_reverted = False

        self.pieces_to_add = []
        self.pieces_to_remove = []

        self._do_move()

    def _do_move(self):
        """Execute the move"""
        if self.end_piece is not None:
            self.capture = True
            self.pieces_to_remove.append(self.end_piece)
            self.positions[self.start_idx] = None
            self.positions[self.end_idx] = self.piece
        else:
            self._handle_castling()
            self.positions[self.start_idx] = None
            self.positions[self.end_idx] = self.piece
            if str(self.piece) == 'pawn':
                self.pawn_advance = True
        self.piece.pos_idx = self.end_idx

    def do_post_move(self):
        """Execute tasks required after a move has been made"""
        self._handle_enpassant()
        self._handle_promotion()
        if self.disable_castle_move:
            self.piece.disable_castle_move()
        self.piece.move_cnt += 1

    def revert(self):
        """Reverse the move just played"""
        if self.move_reverted:
            raise RevertException()
        self.piece.pos_idx = self.start_idx
        if self.end_piece is not None:
            self.positions[self.start_idx] = self.piece
            self.positions[self.end_idx] = self.end_piece
        else:
            if self.disable_castle_move:
                self._revert_castling()
            self.positions[self.start_idx] = self.piece
            self.positions[self.end_idx] = None
        self._clear_lists()
        self.pawn_advance = False
        self.switch_players = False
        self.move_reverted = True

    def _handle_castling(self):
        """Run through the castling steps"""
        if str(self.piece) == 'king' and self.piece.home_square == self.start_idx:
            if self.end_idx == self.piece.king_side_transition[-1]:
                self.positions[self.piece.king_side_rook_pos] = None
                self.positions[
                    self.piece.king_side_transition[-2]] = self.piece.king_side_rook_piece
                self.disable_castle_move = True
            elif self.end_idx == self.piece.queen_side_transition[-1]:
                self.positions[self.piece.queen_side_rook_pos] = None
                self.positions[
                    self.piece.queen_side_transition[-2]] = self.piece.queen_side_rook_piece
                self.disable_castle_move = True

    def _handle_enpassant(self):
        """This function will check if enpassant is being played and execute
        the move"""
        if (str(self.piece) == 'pawn' and self.piece.enpassant and
                self.end_idx in self.piece.enpassant_move):
            self.capture = True
            self.positions[self.piece.enpassant_enemy.pos_idx] = None
            self.pieces_to_remove.append(self.piece.enpassant_enemy)

    def _handle_promotion(self):
        """Run through the pawn promotion steps"""
        if (str(self.piece) == 'pawn' and not self.piece.promoted_piece and
                self.piece.is_on_rank(MAX_RANK[self.piece.allegiance])):
            if self.promotion_piece is not None:
                self.promotion_piece.pos_idx = self.piece.pos_idx
                self.promotion_piece.allegiance = self.piece.allegiance
                self.promotion_piece.promoted_piece = True
                self.pieces_to_remove.append(self.piece)
                self.pieces_to_add.append(self.promotion_piece)
                self.positions[self.end_idx] = self.promotion_piece
            else:
                self.piece.up_for_promotion = True

    def check_double_pawn_move(self):
        """If a pawn has made a double move record this"""
        if str(self.piece) == 'pawn' and abs(self.end_idx - self.start_idx) == 16:
            self.piece.enpassant_sq = self.end_idx - (8*self.piece.get_direction())

    def _revert_castling(self):
        """Revert a castling move"""
        if str(self.piece) == 'king':
            if self.end_idx == self.piece.king_side_transition[-1]:
                self.positions[self.piece.king_side_rook_pos] = self.piece.king_side_rook_piece
                self.positions[
                    self.piece.king_side_transition[-2]] = None
                self.disable_castle_move = False
            elif self.end_idx == self.piece.queen_side_transition[-1]:
                self.positions[self.piece.queen_side_rook_pos] = self.piece.queen_side_rook_piece
                self.positions[
                    self.piece.queen_side_transition[-2]] = None
                self.disable_castle_move = False

    def _clear_lists(self):
        """Clear the lists indicating the pieces to add/remove"""
        self.pieces_to_remove.clear()
        self.pieces_to_add.clear()



class RevertException(BaseException):
    """Moves are not meant to be reverted twice"""

    def __init__(self):
        super(RevertException, self).__init__()
        self.message = ('This Move object has already had revert() called')

    def __str__(self):
        return self.message
