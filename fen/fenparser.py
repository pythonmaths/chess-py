"""FEN Parsing module"""

import re
import utils
from settings import NOTATION

class FENException(BaseException):
    """Exception to catch FEN validation errors"""

    def __init__(self, fen, messages=None):
        super(FENException, self).__init__()
        if messages is not None:
            self.message = 'Invalid FEN record: %s.\n%s' % (
                fen, '\n'.join(messages))
        else:
            self.message = 'Invalid FEN record: %s.' % fen
    def __str__(self):
        return self.message


class FENParser():
    """Container that checks and parses a FEN record"""

    def __init__(self, fen):
        self.fen = fen
        self.record = []
        self.validation_errors = []
        self.placement = None
        self.active_allegiance = None
        self.castling_rights = None
        self.enpassant_sq = None
        self.halfmove_clk = None
        self.fullmove_num = None

    def is_valid(self, verbose=False):
        """Validates FEN string and returns a boolean representing validity"""
        self._validate(verbose)
        if self.validation_errors:
            return False
        return True

    def _validate(self, verbose):
        """
        Make sure FEN record adheres to standard, if verbose is True, then
        print the result to console
        """
        self._extract()
        if self.validation_errors:
            if verbose:
                print('Invalid FEN record: %s.\n%s' % (
                    self.fen, '\n'.join(self.validation_errors)))
            return
        self._validate_placement_str()
        self._validate_active_allegiance_str()
        self._validate_castling_rights_str()
        self._validate_enpassant_sq_str()
        self._validate_int(self.halfmove_clk, self.fullmove_num)
        if self.validation_errors:
            if verbose:
                print('Invalid FEN record: %s.\n%s' % (
                    self.fen, '\n'.join(self.validation_errors)))

    def _extract(self):
        """Extract the component parts of the FEN string"""
        if len(self.fen.split(' ')) != 6:
            self.validation_errors.append(
                'A FEN record contains six fields. The separator between '
                'fields is a space.')
        else:
            (self.placement, self.active_allegiance,
             self.castling_rights, self.enpassant_sq,
             self.halfmove_clk, self.fullmove_num) = self.fen.split(' ')

    def parse(self):
        """Parse the FEN string into it's constituent information"""
        self._extract()
        if self.validation_errors:
            raise FENException(self.fen, messages=self.validation_errors)
        self._parse_placement()
        self._parse_castling_rights()
        self._parse_enapassant_sq()
        self.halfmove_clk = int(self.halfmove_clk)
        self.fullmove_num = int(self.fullmove_num)

    def _parse_placement(self):
        """Convert FEN record placement into the piece positions"""
        pl = self.placement.replace('/', '')
        idx = 0
        for itm in pl:
            if itm.isdigit():
                idx += int(itm)
            else:
                piece_name = NOTATION[itm.lower()]
                allegiance = 'black' if itm.islower() else 'white'
                self.record.append({'piece_name': piece_name,
                                    'pos_idx': idx,
                                    'allegiance': allegiance})
                idx += 1

    def _parse_castling_rights(self):
        """Update FEN record dictionary list with castling avaialbility"""
        for avail in self.castling_rights:
            if avail == '-':
                return
            allegiance = 'black' if avail.islower() else 'white'
            side = 'king' if avail.lower() == 'k' else 'queen'
            try:
                piece = next(itm for itm in self.record
                             if (itm['piece_name'] == 'king' and
                                 itm['allegiance'] == allegiance))
                piece['%s_side_castle_allowed' % side] = True
            except StopIteration:
                pass

    def _parse_enapassant_sq(self):
        """Update FEN record dictionary list with enpassant_sq"""
        if self.enpassant_sq == '-':
            return
        idx = utils.algebra_to_idx(self.enpassant_sq)
        direction = 1 if self.active_allegiance == 'w' else -1
        piece_idx = idx + (direction*8)
        try:
            piece = next(itm for itm in self.record
                         if (itm['piece_name'] == 'pawn' and
                             itm['pos_idx'] == piece_idx))
            piece['enpassant_sq'] = idx
        except StopIteration:
            pass

    def _validate_placement_str(self):
        """
        Make sure FEN record placement part adheres to standard.
        Ranks should add up to 8
        Only certain characters allowed
        """
        str_ = self.placement
        error_msg = '%s is not a recognized placement string.' % str_
        ranks = str_.split('/')
        if len(ranks) != 8:
            self.validation_errors.append('%s Not enough ranks.' % error_msg)
        for rank in ranks:
            if not re.match(r'[rnbqkpPRKBNQ1-8]+', rank):
                self.validation_errors.append(
                    '%s Invalid characters in rank: %s.' % (error_msg, rank))
            squares = 0
            for sq in rank:
                if sq.isnumeric():
                    squares += int(sq)
                else:
                    squares += 1
            if squares != 8:
                self.validation_errors.append(
                    '%s Rank does not equate to 8 squares: %s.' % (error_msg, rank))

    def _validate_active_allegiance_str(self):
        """
        Make sure FEN record active allegiance part adheres to standard.
        Should either be w or b
        """
        str_ = self.active_allegiance
        error_msg = '%s is not a recognized active allegiance.' % str_
        if str_ not in ['w', 'b']:
            self.validation_errors.append(error_msg)

    def _validate_castling_rights_str(self):
        """
        Make sure FEN record castling availability part adheres to standard.
        Should contain any of KQkq
        """
        str_ = self.castling_rights
        error_msg = '%s is not a recognized castling availability.' % str_
        if not re.match(r'[KQkq-]+', str_):
            self.validation_errors.append(error_msg)
        for letter in set(str_):
            if str_.count(letter) > 1:
                self.validation_errors.append(
                    '%s Too many %s\'s.' % (error_msg, letter))

    def _validate_enpassant_sq_str(self):
        """
        Make sure FEN record enpassant square part adheres to standard.
        Should contain any of valid file then valid rank
        """
        str_ = self.enpassant_sq
        error_msg = '%s is not recognized as algebraic notation for rank 3 or 6' % str_
        if not re.match(r'[abcdefgh][36]|-', str_):
            self.validation_errors.append(error_msg)

    def _validate_int(self, *strings):
        """Make sure string is a valid integer"""
        for str_ in strings:
            error_msg = '%s is not an integer.' % str_
            if not str_.isdigit():
                self.validation_errors.append(error_msg)
