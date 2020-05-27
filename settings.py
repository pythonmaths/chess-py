"""ChessPlay engine settings"""

# Piece notation
NOTATION = {'r': 'rook', 'n': 'knight', 'b': 'bishop',
            'q': 'queen', 'k': 'king', 'p': 'pawn'}

FILE_NUMBERS = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8}

#FEN Format
FEN_START_STATE = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

TOP_EDGE = {-1: [0, 1, 2, 3, 4, 5, 6, 7], 1: [56, 57, 58, 59, 60, 61, 62, 63]}
LEFT_EDGE = {-1: [0, 8, 16, 24, 32, 40, 48, 56],
             1: [7, 15, 23, 31, 39, 47, 55, 63]}
RIGHT_EDGE = {1: [0, 8, 16, 24, 32, 40, 48, 56], -
              1: [7, 15, 23, 31, 39, 47, 55, 63]}
BOTTOM_EDGE = {1: [0, 1, 2, 3, 4, 5, 6, 7], -
               1: [56, 57, 58, 59, 60, 61, 62, 63]}

PROMOTION_PIECES = ['queen', 'rook', 'bishop', 'knight', 'pawn']

PAWN_RANK = {'white': 2, 'black': 7}

MAX_RANK = {'white': 8, 'black': 1}

ALLEGIANCES = ['white', 'black']

KNIGHT_MOVES = [-17, -15, -10, -6, 10, 6, 17, 15]

CASTLING_POSITIONS = {'white': {'king_home_square': 60,
                                'king_side_rook_pos': 63,
                                'king_side_transition': [61, 62],
                                'king_side_empty_squares': [61, 62],
                                'queen_side_rook_pos': 56,
                                'queen_side_transition': [59, 58],
                                'queen_side_empty_squares': [59, 58, 57]},
                      'black': {'king_home_square': 4,
                                'king_side_rook_pos': 7,
                                'king_side_transition': [5, 6],
                                'king_side_empty_squares': [5, 6],
                                'queen_side_rook_pos': 0,
                                'queen_side_transition': [3, 2],
                                'queen_side_empty_squares': [3, 2, 1]},
                      }

CASTLING_MOVE_NOTATION = {'king_side': 'O-O', 'queen_side': 'O-O-O',
                          'king_side_alt': '0-0', 'queen_side_alt': '0-0-0'}

UNICODE_PIECES = {
    "r": "♖", "R": "♜",
    "n": "♘", "N": "♞",
    "b": "♗", "B": "♝",
    "q": "♕", "Q": "♛",
    "k": "♔", "K": "♚",
    "p": "♙", "P": "♟",
}

ALGEBRAIC_MOVE_BEGINNINGS = {'pawn_move': [r'^([abcdefgh][12345678])[:x]?'],
                             'non_pawn_move': [r'^([RBNQK])[:x]?'],
                             'ambg': [r'^([abcdefgh])([:x]|[abcdefgh])',
                                      r'^[RBNQK]([abcdefgh12345678]+)[:x]?[abcdefgh][12345678]']}

ALGEBRAIC_MOVE_ENDINGS = {'normal': [r'[abcdefgh][12345678]$'],
                          'capture': [r'(:)$', r'(x)$'],
                          'enapssant': [r'(\s?e.p.)$'],
                          'promotion': [r'([pPRNBQ])$', r'=([pPRNBQ])$',
                                        r'\(([pPRNBQ])\)$', r'/([pPRNBQ])$'],
                          'check': [r'(\+)$', r'(†)$', r'(\s?ch.)$']}

ENGINE_CONFIGURATION_FILE = './engine.cfg'
DEFAULT_ENGINE = 'stockfish_11'
