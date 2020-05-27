"""Some useful functions"""

import re
import string
import functools
from settings import (FILE_NUMBERS, CASTLING_MOVE_NOTATION, ALGEBRAIC_MOVE_ENDINGS,
                      ALGEBRAIC_MOVE_BEGINNINGS, NOTATION)

class AlgebraicFuncException(BaseException):
    """
    Exception to catch input type errors to functions that use both int
    and algebraic types
    """

    def __init__(self, func, arg):
        super(AlgebraicFuncException, self).__init__()
        self.message = ('%s of type %s is a bad input to %s() function. This function '
                        'accepts only integer or algebraic inputs' % (
                            str(arg), type(arg), func.__name__))
    def __str__(self):
        return self.message


class AlgebraicMoveFuncException(BaseException):
    """
    Exception to catch input type errors to functions that use algebraic move input
    """

    def __init__(self, func, arg):
        super(AlgebraicMoveFuncException, self).__init__()
        self.message = ('%s of type %s is a bad input to %s() function. This function '
                        'accepts only one algebraic move notation argument or two '
                        'arguments: a piece instance to move and a board location in '
                        'positional index or algebraic notation' % (str(arg), type(arg),
                                                                    func.__name__))

    def __str__(self):
        return self.message


class InvalidAlgebraException(BaseException):
    """Exception to catch invalid algebraic expressions"""

    def __init__(self, alg):
        super(InvalidAlgebraException, self).__init__()
        self.message = ('%s is not a valid algebraic expression. A valid algebraic '
                        'expression consists of a string of 2 characters representing '
                        'file position (a-h) and rank position (1-8) Examples: a8, h1' % str(alg))

    def __str__(self):
        return self.message


class InvalidLongAlgebraException(BaseException):
    """Exception to catch invalid algebraic expressions"""

    def __init__(self, alg):
        super(InvalidLongAlgebraException, self).__init__()
        self.message = ('%s is not a valid long algebraic expression.' % str(alg))

    def __str__(self):
        return self.message


class InvalidPosIdxException(BaseException):
    """Exception to catch invalid positional index expressions"""

    def __init__(self, idx):
        super(InvalidPosIdxException, self).__init__()
        self.message = ('%s is not a valid positional index. A valid positional '
                        'index is an integer between 0 and 63' % str(idx))

    def __str__(self):
        return self.message


class InvalidAlgebraicMoveException(BaseException):
    """Exception to catch invalid algebraic move expressions"""

    def __init__(self, move):
        super(InvalidAlgebraicMoveException, self).__init__()
        self.message = ('%s is not a valid move in algebraic notation.' % str(move))

    def __str__(self):
        return self.message


class InvalidMoveException(BaseException):
    """Exception to catch invalid board moves"""

    def __init__(self, msg):
        super(InvalidMoveException, self).__init__()
        self.message = 'Invalid move! ' + msg

    def __str__(self):
        return self.message

class PromotionException(BaseException):
    """Exception to catch promotion errors"""

    def __init__(self, msg):
        super(PromotionException, self).__init__()
        self.message = msg

    def __str__(self):
        return self.message


def algebra_to_idx(*args):
    """Convert algebraic notation to positional index"""
    output = [_algebra_to_idx(arg) for arg in args]
    return output if len(output) != 1 else output[0]


def idx_to_algebra(*args):
    """Convert positional index to algebraic notation"""
    output = [_idx_to_algebra(arg) for arg in args]
    return output if len(output) != 1 else output[0]

def idx_to_rect(*args, multiplier=1, offset=0):
    """Convert positional index to rect coordinates"""
    output = [_idx_to_rect(arg, multiplier, offset) for arg in args]
    return output if len(output) != 1 else output[0]

def long_algebra_to_move(arg):
    """Converts UCI long algebraic notation to a chessplay move"""
    if not is_long_algebraic(arg):
        raise InvalidLongAlgebraException(arg)
    match = re.match(
        r'([abcdefgh][12345678])([abcdefgh][12345678])([qrbnp]?)', arg)
    return match.groups()

def _algebra_to_idx(alg: str) -> int:
    """Convert algebraic notation to positional index"""
    if not is_algebraic(alg):
        raise InvalidAlgebraException(alg)
    rank, file = 9 - int(alg[1]), FILE_NUMBERS[alg[0]]
    return ((rank-1)*8) + (file-1)


def _idx_to_algebra(idx: int) -> str:
    """Convert positional index to algebraic notation"""
    if not is_pos_idx(idx):
        raise InvalidPosIdxException(idx)
    file = string.ascii_lowercase[idx % 8]
    rank = str(8 - (idx // 8))
    return file + rank


def _idx_to_rect(idx, multiplier, offset):
    """Convert positional index to rect coordinates"""
    if not is_pos_idx(idx):
        raise InvalidPosIdxException(idx)
    x = ((idx % 8)*multiplier) + offset
    y = ((idx // 8)*multiplier) + offset
    return (x, y)


def decode_algebraic_move(move, pieces, players):
    """
    Convert a move in algebraic notation into a piece instance to move and a
    destination board position
    """
    if not is_algebraic_move(move):
        raise InvalidAlgebraicMoveException(move)
    allegiance = players.current_player.allegiance
    move_info = _extract_move_info(move)
    promo_choice = move_info['promotion'] if 'promotion' in move_info else None
    if 'queen_side_castle' in move_info:
        piece = pieces.get_king(allegiance)
        end_idx = piece.queen_side_transition[-1]
        if end_idx not in piece.legal_moves:
            raise InvalidMoveException(
                'Queen side castling is not legal for %s' % piece.get_overview())
    elif 'king_side_castle' in move_info:
        piece = pieces.get_king(allegiance)
        end_idx = piece.king_side_transition[-1]
        if end_idx not in piece.legal_moves:
            raise InvalidMoveException(
                'King side castling is not legal for %s' % piece.get_overview())
    else:
        end_idx = algebra_to_idx(re.findall(r'[abcdefgh][12345678]', move)[-1])
        if 'non_pawn_move' in move_info:
            piece_name = move_info['non_pawn_move']
        else:
            piece_name = 'p'
        ambg = move_info['ambg'] if 'ambg' in move_info else None
        piece = pieces.get_piece_from_properties(allegiance, piece_name, end_idx, ambg=ambg)
        if piece is None:
            raise InvalidMoveException('Allegiance: %s, Name: %s, Move: %s. Either there is '
                                       'no piece with the allegiance and name on the board '
                                       'or no pieces with allegiance and name can make the '
                                       'move legally' % (allegiance,
                                                         NOTATION[piece_name.lower()],
                                                         idx_to_algebra(end_idx)))
    return piece, end_idx, promo_choice


def _extract_move_info(move):
    """Uses regular expressions to determine certain move properties"""
    move_info = {}
    if move in [CASTLING_MOVE_NOTATION['queen_side'], CASTLING_MOVE_NOTATION['queen_side_alt']]:
        return {'queen_side_castle': True}
    if move in [CASTLING_MOVE_NOTATION['king_side'], CASTLING_MOVE_NOTATION['king_side_alt']]:
        return {'king_side_castle': True}
    merge_dict = {**ALGEBRAIC_MOVE_BEGINNINGS, **ALGEBRAIC_MOVE_ENDINGS}
    del merge_dict['normal']
    for key, value in merge_dict.items():
        for regex in value:
            search = re.search(regex, move)
            if search:
                move_info[key] = search.group(1)
    search = re.search(r'([x:])', move)
    if search and 'capture' not in move_info:
        move_info['capture'] = search.group(1)
    return move_info


def is_algebraic(arg: str) -> bool:
    """Return True if arg matches algebraic notation"""
    if not isinstance(arg, str):
        return False
    return bool(re.match(r'^[abcdefgh][12345678]$', arg))

def is_long_algebraic(arg: str) -> bool:
    """Return True if arg matches long algebraic notation used in UCI"""
    if not isinstance(arg, str):
        return False
    return bool(re.match(r'^[abcdefgh][12345678][abcdefgh][12345678][qrbnp]?$', arg))

def is_pos_idx(arg: int) -> bool:
    """Return True if arg matches positional index notation"""
    if not isinstance(arg, int):
        return False
    return bool(0 <= arg <= 63)


def is_algebraic_move(arg: str) -> bool:
    """Return True if arg is a valid FIDE alebraic move"""
    if arg in CASTLING_MOVE_NOTATION.values():
        return True
    pos = re.findall(r'[abcdefgh][12345678]', arg)
    if len(pos) not in [1, 2]:
        return False
    beginnings = flatten(ALGEBRAIC_MOVE_BEGINNINGS.values())
    endings = flatten(ALGEBRAIC_MOVE_ENDINGS.values())
    if not any([bool(re.search(x, arg)) for x in beginnings]):
        return False
    if not any([bool(re.search(x, arg)) for x in endings]):
        return False
    return True


def algebraic(func):
    """Wrapper function for functions that accept algebraic or int types"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        new_args = []
        if callable(getattr(args[0], func.__name__)):
            new_args.append(args[0])
        for arg in args[1:]:
            if isinstance(arg, int) and is_pos_idx(arg):
                new_args.append(arg)
            elif isinstance(arg, str) and is_algebraic(arg):
                new_args.append(algebra_to_idx(arg))
            else:
                raise AlgebraicFuncException(func, arg)
        return func(*new_args, **kwargs)
    return wrapper


def algebraic_move(func):
    """Wrapper function for functions that can use algebraic move notation"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        new_args = []
        if callable(getattr(args[0], func.__name__)):
            new_args.append(args[0])
        if len(args[1:]) == 1 and isinstance(args[1], str):
            if is_algebraic_move(args[1]):
                pieces = getattr(args[0], 'pieces')
                players = getattr(args[0], 'players')
                piece, end_idx, promo_choice = decode_algebraic_move(args[1], pieces, players)
                new_args.extend([piece, end_idx])
                kwargs['promotion_choice'] = promo_choice
            else:
                raise InvalidAlgebraicMoveException(args[1])
        elif len(args[1:]) == 2:
            new_args.append(args[1])
            if isinstance(args[2], int) and is_pos_idx(args[2]):
                new_args.append(args[2])
            elif isinstance(args[2], str) and is_algebraic(args[2]):
                new_args.append(algebra_to_idx(args[2]))
            else:
                raise AlgebraicMoveFuncException(func, args[2])
        else:
            # Act invisible and allow normal internal error
            new_args = args
        return func(*new_args, **kwargs)
    return wrapper


def flatten(list_):
    """Returns a flattened list"""
    return [item for sublist in list_ for item in sublist]
