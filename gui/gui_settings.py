"""Settings for pygame gui"""

from pygame import font, image, transform, Rect

font.init()
HELVETICA_FONT = font.Font(r'art\Helvetica.ttf', 30)
FONT_COLOUR = 'black'

# Screen settings
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
CELL_SIZE = 80

# Pop up Screen settings
POPUP_SCREEN_WIDTH = 480
POPUP_SCREEN_WIDTH_OFFSET = (SCREEN_WIDTH - POPUP_SCREEN_WIDTH)/2
POPUP_SCREEN_HEIGHT = 320
POPUP_SCREEN_HEIGHT_OFFSET = (SCREEN_HEIGHT - POPUP_SCREEN_HEIGHT)/2
POPUP_SCREEN_COLOUR = 'sepia_translucent150'

# rbg colours
COLOURS = {'white': (255, 255, 255),
           'black': (0, 0, 0),
           'sepia': (224, 154, 84),
           'cyan':  (0, 255, 255),
           'magenta':  (255, 0, 255),
           'red': (255, 0, 0),
           'black_transparent': (0, 0, 0, 0),
           'black_translucent100': (0, 0, 0, 100),
           'black_translucent50': (0, 0, 0, 50),
           'sepia_translucent150': (224, 154, 84, 150),
           'black_opaque': (0, 0, 0, 255)}

DARK_SQUARES = 'sepia'
LIGHT_SQUARES = 'white'
SELECTED_PIECE = 'cyan'
LEGAL_MOVES = 'cyan'
CASTLING_MOVES = 'magenta'
ENPASSANT_MOVES = 'magenta'
SPECIAL_MOVES = 'red'

ENDGAME_BUTTON_SETTINGS = {"colour": COLOURS['black'],
                           "width": 1,
                           "font": HELVETICA_FONT,
                           "hover_colour": COLOURS['cyan'],
                           "hover_width": 5,
                           "clicked_colour": COLOURS['cyan'],
                           "clicked_width": 5,
                           "font_colour": COLOURS['black'],
                           "hover_font_colour": COLOURS['black'],
                           "clicked_font_colour": COLOURS['black'],
                           "click_sound": None,
                           "hover_sound": None}

ENDGAME_RESTART_BUTTON_RECT = (120, 360, 160, 80)
ENDGAME_QUIT_BUTTON_RECT = (360, 360, 160, 80)

PIECE_IMAGES = {'pawn':
                    {'cburnett': {'white': image.load(r'art\cburnett\80\WhitePawn.png'),
                                  'black': image.load(r'art\cburnett\80\BlackPawn.png')}},
                'knight':
                    {'cburnett': {'white': image.load(r'art\cburnett\80\WhiteKnight.png'),
                                  'black': image.load(r'art\cburnett\80\BlackKnight.png')}},
                'bishop':
                    {'cburnett': {'white': image.load(r'art\cburnett\80\WhiteBishop.png'),
                                  'black': image.load(r'art\cburnett\80\BlackBishop.png')}},
                'rook':
                    {'cburnett': {'white': image.load(r'art\cburnett\80\WhiteRook.png'),
                                  'black': image.load(r'art\cburnett\80\BlackRook.png')}},
                'queen':
                    {'cburnett': {'white': image.load(r'art\cburnett\80\WhiteQueen.png'),
                                  'black': image.load(r'art\cburnett\80\BlackQueen.png')}},
                'king':
                    {'cburnett': {'white': image.load(r'art\cburnett\80\WhiteKing.png'),
                                  'black': image.load(r'art\cburnett\80\BlackKing.png')}}}

# Pawn Promotion Screen
PROMOTION_PIECES = ['q', 'r', 'b', 'n', 'p']
PROMOTION_HOVER = 'cyan'
PROMOTION_SPRITES = {
    'white': [
        (transform.smoothscale(PIECE_IMAGES['queen']['cburnett']['white'], (100, 100)),
         Rect(110, 190, 100, 100)),
        (transform.smoothscale(PIECE_IMAGES['rook']['cburnett']['white'], (100, 100)),
         Rect(270, 190, 100, 100)),
        (transform.smoothscale(PIECE_IMAGES['bishop']['cburnett']['white'], (100, 100)),
         Rect(430, 190, 100, 100)),
        (transform.smoothscale(PIECE_IMAGES['knight']['cburnett']['white'], (100, 100)),
         Rect(190, 350, 100, 100)),
        (transform.smoothscale(PIECE_IMAGES['pawn']['cburnett']['white'], (100, 100)),
         Rect(350, 350, 100, 100))],
    'black': [
        (transform.smoothscale(PIECE_IMAGES['queen']['cburnett']['black'], (100, 100)),
         Rect(110, 190, 100, 100)),
        (transform.smoothscale(PIECE_IMAGES['rook']['cburnett']['black'], (100, 100)),
         Rect(270, 190, 100, 100)),
        (transform.smoothscale(PIECE_IMAGES['bishop']['cburnett']['black'], (100, 100)),
         Rect(430, 190, 100, 100)),
        (transform.smoothscale(PIECE_IMAGES['knight']['cburnett']['black'], (100, 100)),
         Rect(190, 350, 100, 100)),
        (transform.smoothscale(PIECE_IMAGES['pawn']['cburnett']['black'], (100, 100)),
         Rect(350, 350, 100, 100))]}
