"""
Module containing the 'Board' which consists of the piece positions and piece state
"""
# pylint: disable=no-value-for-parameter
# pylint: disable=import-outside-toplevel
import re
import utils
from fen import FENParser, FENBuilder
from settings import FEN_START_STATE, UNICODE_PIECES, FILE_NUMBERS, NOTATION, ALLEGIANCES
from chessboard.players import Players, Human, Computer
from chessboard.pieces import Pieces
from chessboard.move import Move

DECODE_PLAYER = {'h': Human, 'human': Human, 'c': Computer, 'computer': Computer}

class Board():
    """Piece positions and state"""
    def __init__(self, start_state=FEN_START_STATE, white='h', black='h'):

        self.pieces = Pieces()
        self.players = Players(DECODE_PLAYER[white](), DECODE_PLAYER[black]())

        self.positions = [None]*64
        self.halfmove_clk = None
        self.fullmove_num = None

        self.last_move_info = {'success': True, 'check_attackers': []}
        self.turn_clock = 0

        self.reset(start_state=start_state)

        self.update()

    def reset(self, start_state=None):
        """Empty the board of pieces and state"""
        self.positions = [None]*64
        self.pieces.reset()
        self.players.reset()
        self.halfmove_clk = None
        self.fullmove_num = None
        self.last_move_info = {'success': True, 'check_attackers': []}
        if start_state is not None:
            self._init_board_from_FEN(start_state)
        else:
            self._init_board_from_FEN(FEN_START_STATE)
        self.update()

    @utils.algebraic
    def is_occupied(self, idx):
        """Return True if idx is occupied by a piece"""
        return self.positions[idx] is not None

    @utils.algebraic
    def get_piece(self, idx):
        """Return the piece inst by idx or algebraic expression"""
        return self.positions[idx]

    @utils.algebraic
    def get_piece_name(self, idx):
        """Return the piece name by idx or algebraic expression"""
        return str(self.positions[idx])

    def __str__(self):
        return self.to_string(unicode=True, rank_file=True)

    def __repr__(self):
        return self.to_string(unicode=True, rank_file=True)

    def to_string(self, unicode=False, rank_file=False, empty_symbol='-'):
        """Pretty print the positions in a human readable format to the console"""
        lines = []
        if rank_file:
            lines.append('  ' + ' '.join(FILE_NUMBERS.keys()))
        for i in range(8):
            line = ''
            if rank_file:
                line += '%d ' % (8-i)
            for j in range(8):
                p = self.positions[i*8 + j]
                if p is not None:
                    piece = UNICODE_PIECES[p.get_char()] if unicode else p.get_char()
                    line += piece + ' '*len(empty_symbol)
                else:
                    piece = empty_symbol
                    line += piece + ' '
            lines.append(line)
        return '\n'.join(lines)

    def _init_board_from_FEN(self, fen):
        """Reset the board and initiliase a game state from an FEN string"""
        parser = FENParser(fen)
        if parser.is_valid():
            parser.parse()
        self.halfmove_clk = parser.halfmove_clk
        self.fullmove_num = parser.fullmove_num
        for piece_dict in parser.record:
            piece_inst = self._create_piece(piece_dict)
            self.pieces.add(piece_inst)
            self.positions[piece_dict['pos_idx']] = piece_inst
        self.players.set_current_player(parser.active_allegiance)

    def _create_piece(self, piece_dict):
        """Return a piece instance from a name, board index and allegiance"""
        piece_module = __import__('%s.%s' % (__name__.split('.')[0],
                                             piece_dict['piece_name']))
        piece_class = getattr(piece_module, piece_dict['piece_name'].capitalize())
        piece_inst = piece_class(init_position=piece_dict['pos_idx'],
                                 allegiance=piece_dict['allegiance'])
        piece_inst.__dict__ = {**piece_inst.__dict__, **piece_dict}
        return piece_inst

    def _create_promotion_piece(self, promotion_choice):
        """
        Initiliase a piece from the promotion choice without a position or allegiance
        """
        if promotion_choice is not None:
            piece_dict = {}
            try:
                promotion_choice = NOTATION[promotion_choice.lower()]
            except KeyError:
                raise utils.PromotionException('Unrecognised choice of piece for '
                                               'promotion %s' % promotion_choice.lower())
            if promotion_choice == 'king':
                raise utils.PromotionException('Promotion to a king is not allowed')
            piece_dict['piece_name'] = promotion_choice
            piece_dict['pos_idx'] = None
            piece_dict['allegiance'] = None
            return self._create_piece(piece_dict)
        return None

    def get_FEN(self) -> str:
        """Returns the current state of the board as an FEN string"""
        return FENBuilder(self.pieces, self.players, self.halfmove_clk, self.fullmove_num).build()

    def move(self, move):
        """Do a move 2 turns"""
        turns = move.split(' ')
        for turn in turns:
            self.turn(turn)

    @utils.algebraic_move
    def turn(self, piece, end_idx, promotion_choice=None):
        """Move the given piece to the given positional index"""
        if end_idx not in piece.legal_moves:
            raise utils.InvalidMoveException(
                '%s is not a legal move for the piece %s' % (utils.idx_to_algebra(end_idx),
                                                             piece.get_overview()))
        self.pieces.reset_promotion()
        promotion_piece = self._create_promotion_piece(promotion_choice)
        move = Move(self.positions, piece, end_idx, promotion_piece=promotion_piece)
        self.pieces.mask(*move.pieces_to_remove)
        self.update()
        self.pieces.masked_pieces.clear()
        if self.is_in_check(self.players.current_player.allegiance):
            self.last_move_info['success'] = False
            self.last_move_info['check_attackers'] = self.get_check_attackers(
                self.players.current_player.allegiance, pos_idx=True)
            move.revert()
            self.update()
        else:
            self.last_move_info['success'] = True
            self.last_move_info['check_attackers'] = []
        move.do_post_move()
        self.pieces.remove(*move.pieces_to_remove)
        self.pieces.add(*move.pieces_to_add)
        self.pieces.reset_enpassant()
        move.check_double_pawn_move()
        if move.switch_players:
            self.players.switch_player()
            if self.players.current_player.allegiance == 'white':
                self.fullmove_num += 1
        if move.capture or move.pawn_advance:
            self.halfmove_clk = 0
        else:
            self.halfmove_clk += 1
        self.update()
        self.turn_clock = not self.turn_clock

    def do_computer_move(self):
        """If the current player is a computer, execute their move"""
        if self.players.current_player.is_human:
            print('Current player is Human. This has no effect')
        else:
            self.update()
            self.players.current_player.set_position(self.get_FEN())
            best_move = self.players.current_player.get_best_move()
            piece_alg, end_alg, promotion_choice = utils.long_algebra_to_move(best_move)
            piece = self.get_piece(piece_alg)
            end_idx = utils.algebra_to_idx(end_alg)
            if not promotion_choice:
                promotion_choice = None
            self.turn(piece, end_idx, promotion_choice=promotion_choice)

    @utils.algebraic
    def scout(self, idx):
        """Provide scout report for a piece"""
        if not self.is_occupied(idx):
            return None
        piece = self.get_piece(idx)
        return self.pieces.scout_move_pool(piece)

    @utils.algebraic
    def get_legal_moves(self, idx, pos_idx=False):
        """Given the board state get the legal moves of a piece"""
        if not self.is_occupied(idx):
            return None
        legal_moves = self.get_piece(idx).legal_moves
        if pos_idx:
            return legal_moves
        algs = utils.idx_to_algebra(*legal_moves)
        return algs if isinstance(algs, list) else [algs]

    def get_check_attackers(self, allegiance, pos_idx=False):
        """
        Return a list of piece positions that are currently placing the king
        with the given allegiance in check
        """
        attackers = []
        king_loc = self.pieces.get_king(allegiance).pos_idx
        z = ALLEGIANCES.index(allegiance)
        for piece in self.pieces.get_pieces_by_allegiance(ALLEGIANCES[not z]):
            if king_loc in piece.legal_moves:
                attackers.append(piece.pos_idx)
        if pos_idx:
            return attackers
        return utils.idx_to_algebra(*attackers)

    def update(self):
        """Update the board elements after a change in positions"""
        self.pieces.update(self.positions)

    def _update_mate(self):
        """Update the board elements to check for mate"""
        self.pieces.update(self.positions, mate=True)

    def is_in_check(self, allegiance):
        """Returns whether the king with the given allegiance is in check"""
        return self.pieces.get_king(allegiance).in_check

    def promote_pawn(self, promotion_choice):
        """Promote a pawn with a selected piece if a pawn needs promoting"""
        promotion_piece = self._create_promotion_piece(promotion_choice)
        piece_to_be_promoted = self.pieces.get_pawn_promotion_piece()
        promotion_piece.pos_idx = piece_to_be_promoted.pos_idx
        promotion_piece.allegiance = piece_to_be_promoted.allegiance
        promotion_piece.promoted_piece = True
        self.pieces.remove(piece_to_be_promoted)
        self.pieces.add(promotion_piece)
        self.positions[piece_to_be_promoted.pos_idx] = promotion_piece

    def check_endgame(self):
        """
        This function will check whether we have transitioned to a checkmate or
        stalemate state
        """
        self._update_mate()
        current_player_allegiance = self.players.current_player.allegiance
        move_check_status = []
        in_check = self.is_in_check(current_player_allegiance)
        for piece in self.pieces.get_pieces_by_allegiance(current_player_allegiance):
            for legal_move in piece.legal_moves:
                move = Move(self.positions, piece, legal_move)
                self.pieces.mask(*move.pieces_to_remove)
                self._update_mate()
                self.pieces.masked_pieces.clear()
                move_check_status.append(self.is_in_check(current_player_allegiance))
                move.revert()
                self._update_mate()
        if all(move_check_status):
            if in_check:
                return 'Checkmate'
            return 'Stalemate'
        return None

    def PGN(self, str_):
        """Do some moves from a PGN string"""
        moves = re.split(r'\s?[0-9]+\.', str_)[1:]
        for move in moves:
            self.move(move)

    def gui(self):
        """Start the gui from the board state"""
        import gui
        gui.run(self)
