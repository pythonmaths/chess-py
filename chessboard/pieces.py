"""Store a collection of chess pieces"""

from operator import truth
from collections import OrderedDict
from chessboard.piece import Piece
import utils
from settings import ALLEGIANCES

class Pieces():
    """Class for a piece collection"""

    def __init__(self):
        self.pieces_dict = OrderedDict()
        self.lost_pieces = []
        self.masked_pieces = []

    def __iter__(self):
        return iter(self.pieces())

    def __nonzero__(self):
        return truth(self.pieces())

    def __len__(self):
        """Return number of pieces in group"""
        return len(self.pieces())

    def __repr__(self):
        return "<%s(%d pieces)>" % (self.__class__.__name__, len(self))

    def reset(self):
        """Clear lists"""
        self.pieces_dict = OrderedDict()
        self.lost_pieces = []
        self.masked_pieces = []

    def pieces(self):
        """Get a list of pieces in the collection"""
        pieces = list(self.pieces_dict)
        return [piece for piece in pieces if piece not in self.masked_pieces]

    def get_pieces_by_allegiance(self, allegiance):
        """Get the pieces that belong to an allegiance"""
        return [piece for piece in self.pieces() if piece.allegiance == allegiance]

    def add(self, *pieces):
        """Add piece(s) to collection, ensure kings stay last since they are the
           last to be updated"""
        for piece in pieces:
            if not isinstance(piece, Piece):
                raise TypeError('Pieces container can only contain pieces that '
                                'inherit the Piece class.')
            self.pieces_dict[piece] = 0
            if str(piece) == 'king':
                self.pieces_dict.move_to_end(piece)
            else:
                self.pieces_dict.move_to_end(piece, last=False)

    def mask(self, *pieces):
        """Mask pieces in collection"""
        for piece in pieces:
            if self.has(piece):
                self.masked_pieces.append(piece)

    def remove(self, *pieces):
        """Remove piece(s) to collection"""
        for piece in pieces:
            if self.has(piece):
                self.lost_pieces.append(piece)
                del self.pieces_dict[piece]

    def has(self, piece):
        """Does the collection have a piece"""
        return piece in self.pieces_dict

    def pawn_needs_promotion(self):
        """Return True if pawn is up for promotion"""
        for piece in self.pieces():
            if str(piece) == 'pawn' and piece.up_for_promotion:
                return True
        return False

    def reset_promotion(self):
        """Before each move all promotion should have occured"""
        for piece in self.pieces():
            if str(piece) == 'pawn':
                piece.up_for_promotion = False

    def get_king(self, allegiance):
        """Return the king piece of a given allegiance"""
        for piece in self.pieces():
            if str(piece) == 'king' and piece.allegiance == allegiance:
                return piece
        return None

    def get_kings(self):
        """Return the king pieces in a list"""
        return [self.get_king(allegiance) for allegiance in ALLEGIANCES
                if self.get_king(allegiance) is not None]

    def get_double_move_pawn(self):
        """Returns a pawn if any that has just moved two squares"""
        for piece in self.pieces():
            if str(piece) == 'pawn' and piece.enpassant_sq is not None:
                return piece
        return None

    def get_pawn_promotion_piece(self):
        """Return the pawn piece that needs promoting"""
        for piece in self.pieces():
            if str(piece) == 'pawn' and piece.up_for_promotion:
                return piece
        return None

    def get_promoted_pieces(self):
        """Return all pieces that are promoted pawns"""
        return [piece for piece in self.pieces() if piece.promoted_piece]

    def reset_enpassant(self):
        """After each move all enpassant info is reset"""
        for piece in self.pieces():
            if str(piece) == 'pawn':
                piece.reset_enpassant()

    def _get_piece_if_occupied(self, idx):
        """Return a piece by looking for its position index return None if no match"""
        for piece in self.pieces():
            if piece.pos_idx == idx:
                return piece
        return None

    def get_piece_from_properties(self, allegiance, name, move, ambg=None):
        """
        Return a specific piece that matches the given properties. If more than
        one piece matches the properties and ambg doesn't differentiate then an
        error is thrown
        """
        candidates = []
        unique_piece = []
        for piece in self.pieces():
            if (piece.get_char().lower() == name.lower() and
                    piece.allegiance == allegiance and
                    move in piece.legal_moves):
                candidates.append(piece)
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            for candidate in candidates:
                if ambg in utils.idx_to_algebra(candidate.pos_idx):
                    unique_piece.append(candidate)
            if not unique_piece or len(unique_piece) > 1:
                candidate_pos = [utils.idx_to_algebra(x.pos_idx) for x in candidates]
                raise Exception('Found candidates: %s by the ambiguity string %s does'
                                'not differentiate them' % (candidate_pos, ambg))
            return unique_piece[0]
        return None

    def scout_move_pool(self, piece):
        """Return a scout report for a piece"""
        if str(piece) == 'king':
            illegal_moves = self.get_king_illegal_moves(piece.allegiance)
        else:
            illegal_moves = []
        report = {}
        move_pool = piece.get_move_pool(pos_idx=True)
        for direction, positions in move_pool.items():
            for position in positions:
                if position in illegal_moves:
                    continue
                scouted_piece = self._get_piece_if_occupied(position)
                if scouted_piece:
                    enemy_occupied = scouted_piece.allegiance != piece.allegiance
                    enemy_king_occupied = str(scouted_piece) == 'king' and enemy_occupied
                    ally_occupied = not enemy_occupied
                else:
                    enemy_occupied = enemy_king_occupied = ally_occupied = False
                pos_report = {'loc': position,
                              'occupied': bool(scouted_piece),
                              'enemy_occupied': enemy_occupied,
                              'enemy_king_occupied': enemy_king_occupied,
                              'ally_occupied': ally_occupied}
                report[direction] = (report[direction] + [pos_report]
                                     if direction in report
                                     else [pos_report])
        return report

    def get_king_illegal_moves(self, allegiance):
        """Return all the illegal moves of the king piece with a given allegiance"""
        king_illegal_moves = []
        for piece in self.pieces():
            if piece.allegiance != allegiance:
                if str(piece) == 'pawn':
                    # ignore forward legal moves if its a pawn
                    king_illegal_moves.extend(
                        piece.allies_in_legal_moves + piece.illegal_enemy_king_moves)
                elif str(piece) == 'king':
                    # king can't move next to its opposite king
                    enemy_king_move_pool = piece.get_move_pool(pos_idx=True)
                    enemy_king_move_pool = [item for sublist in enemy_king_move_pool.values()
                                            for item in sublist]
                    king_illegal_moves.extend(enemy_king_move_pool)
                else:
                    king_illegal_moves.extend(piece.legal_moves +
                                              piece.allies_in_legal_moves +
                                              piece.illegal_enemy_king_moves)
        return list(set(king_illegal_moves))

    def _get_king_attackers(self, king_piece):
        """Get all pieces currently attacking the given king"""
        attackers = [piece for piece in self.pieces()
                     if (king_piece.pos_idx in piece.legal_moves and
                         king_piece.allegiance != piece.allegiance)]
        return attackers

    def _update_piece_positions(self, positions):
        """
        Update the position of each piece given its index in the board position
        list
        """
        for piece in self.pieces():
            piece.pos_idx = positions.index(piece)

    def _update_legal_moves(self):
        """Update the legal moves of all the pieces"""
        for piece in self.pieces():
            piece_scout_report = self.scout_move_pool(piece)
            piece.update_legal_moves(piece_scout_report)

    def _update_in_check(self):
        """Update the 'in check' and 'checked by' status of the kings"""
        for king in self.get_kings():
            enemy_attacks = self.get_king_illegal_moves(king.allegiance)
            king_attackers = self._get_king_attackers(king)
            king.enemy_attacks = enemy_attacks
            king.checked_by = king_attackers
            king.update_check()

    def _update_castling_rights(self):
        """Update the castling rights of the kings"""
        for king in self.get_kings():
            if king.move_cnt > 0:
                king.king_side_castle_allowed = False
                king.queen_side_castle_allowed = False
            else:
                king_side_piece = self._get_piece_if_occupied(king.king_side_rook_pos)
                queen_side_piece = self._get_piece_if_occupied(king.queen_side_rook_pos)
                king.king_side_rook_piece = king_side_piece
                king.queen_side_rook_piece = queen_side_piece
                if not (str(king_side_piece) == 'rook' and king_side_piece.move_cnt == 0):
                    king.king_side_castle_allowed = False
                if not (str(queen_side_piece) == 'rook' and queen_side_piece.move_cnt == 0):
                    king.queen_side_castle_allowed = False

    def _update_castling(self, mate=False):
        """Update the validity of castling on each side for each king"""
        for king in self.get_kings():
            if not king.in_check:
                cond_ak = all([not self._get_piece_if_occupied(pos)
                               for pos in king.king_side_empty_squares])
                cond_aq = all([not self._get_piece_if_occupied(pos)
                               for pos in king.queen_side_empty_squares])

                enemy_attacks = self.get_king_illegal_moves(king.allegiance)
                cond_bk = all([pos not in enemy_attacks
                               for pos in king.king_side_transition])
                cond_bq = all([pos not in enemy_attacks
                               for pos in king.queen_side_transition])

                if cond_ak and cond_bk:
                    king.king_side_castle_valid = True
                else:
                    king.disable_castle_move(side='king')

                if cond_aq and cond_bq:
                    king.queen_side_castle_valid = True
                else:
                    king.disable_castle_move(side='queen')
            else:
                king.disable_castle_move()

            if not mate:
                king.add_castling_legal_moves()

    def _update_enpassant(self):
        """This function will check if enpassant is a viable move and enable the
           enpassant pawn with its legal moves"""
        piece = self.get_double_move_pawn()
        if piece is not None:
            pos = piece.pos_idx
            # If pawn and moved two squares
            adjacent_positions = [pos + x for x in [-1, 1]
                                  if (pos + x) // 8 == pos // 8]
            for idx in adjacent_positions:
                adjacent_piece = self._get_piece_if_occupied(idx)
                if (adjacent_piece is not None and str(adjacent_piece) == 'pawn' and
                        adjacent_piece.allegiance != piece.allegiance):
                    adjacent_piece.enable_enpassant(pos - (8*piece.get_direction()),
                                                    piece)
                    adjacent_piece.add_enpassant_move()

    def update(self, positions, mate=False):
        """Ordered update of piece state"""
        self._update_piece_positions(positions)
        self._update_legal_moves()
        if not mate:
            self._update_enpassant()
        self._update_in_check()
        if not mate:
            self._update_castling_rights()
        self._update_castling(mate=mate)
