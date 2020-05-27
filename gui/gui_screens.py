"""Module containing various pop up display settings"""
# pylint: disable=E0203
# pylint: disable=E1101

from pygame import mouse, Surface, Rect, font, draw
from gui.gui_settings import (POPUP_SCREEN_WIDTH_OFFSET, POPUP_SCREEN_HEIGHT_OFFSET,
                              POPUP_SCREEN_HEIGHT, POPUP_SCREEN_WIDTH, HELVETICA_FONT,
                              COLOURS, POPUP_SCREEN_COLOUR, FONT_COLOUR, PROMOTION_SPRITES,
                              PROMOTION_HOVER, PROMOTION_PIECES, ENDGAME_BUTTON_SETTINGS,
                              ENDGAME_QUIT_BUTTON_RECT, ENDGAME_RESTART_BUTTON_RECT)

class PopUpScreen():
    """Base class for basic pop up screen"""

    def __init__(self, host_screen):
        self.host_screen = host_screen
        self.surface = Surface((POPUP_SCREEN_WIDTH, POPUP_SCREEN_HEIGHT)).convert_alpha()
        self.surface_rect = self.surface.get_rect()
        self.surface_rect.move_ip(POPUP_SCREEN_WIDTH_OFFSET, POPUP_SCREEN_HEIGHT_OFFSET)
        self.block = False

    def blit_popup_screen(self):
        """Add the basic pop up screen surface to the host screen"""
        self.surface.fill(COLOURS[POPUP_SCREEN_COLOUR])
        self.host_screen.blit(self.surface, self.surface_rect)

    def get_multiline_surf(self, message, font_=HELVETICA_FONT, font_colour=FONT_COLOUR):
        """Returns a surface with message text on multiple lines"""
        multiline_surf = MultiLineSurface(
            message,
            font_,
            Rect(POPUP_SCREEN_WIDTH_OFFSET, POPUP_SCREEN_HEIGHT_OFFSET,
                 POPUP_SCREEN_WIDTH, POPUP_SCREEN_HEIGHT),
            COLOURS[font_colour],
            COLOURS[POPUP_SCREEN_COLOUR],
            justification=1)
        return multiline_surf

class PromotionScreen(PopUpScreen):
    """Handles special pawn promotion flow"""

    def __init__(self, host_screen):
        super(PromotionScreen, self).__init__(host_screen)
        self.text = self.get_multiline_surf(
            'Promote Pawn:\nHover to select piece')

    def blit(self, allegiance):
        """Decide screen propeties and blit Pop up screen"""
        self.blit_popup_screen()
        if self.surface_rect.collidepoint(mouse.get_pos()):
            self.host_screen.blits(PROMOTION_SPRITES[allegiance])
            rects = list(zip(*PROMOTION_SPRITES[allegiance]))[1]
            for rect in rects:
                if rect.collidepoint(mouse.get_pos()):
                    draw.rect(self.host_screen, COLOURS[PROMOTION_HOVER], rect, 5)
        else:
            self.host_screen.blit(self.text.surf, self.text.rect)

    def get_selection(self):
        """Determine selected promotion piece"""
        rects = list(zip(*PROMOTION_SPRITES['white']))[1]
        pieces = PROMOTION_PIECES
        for rect, piece in zip(rects, pieces):
            if rect.collidepoint(mouse.get_pos()):
                return piece
        return None

    def reset(self):
        """REset the promotion screen state"""
        self.block = False


class EndGameScreen(PopUpScreen):
    """Handles what to do when the endgame is reached"""

    def __init__(self, host_screen):
        super(EndGameScreen, self).__init__(host_screen)
        self.quit_button = None
        self.restart_button = None
        self.reset()

    def blit(self, result, allegiance):
        """Decide screen propeties and blit to main screen"""
        self.blit_popup_screen()
        screen_message = self.get_screen_message(result, allegiance)
        text = self.get_multiline_surf(screen_message)
        self.host_screen.blit(text.surf, text.rect)
        self.restart_button.update(self.host_screen)
        self.quit_button.update(self.host_screen)

    def handle_selection(self):
        """See which button was clicked if any"""
        self.restart_button.check_click()
        self.quit_button.check_click()

    def reset(self):
        """Reset buttons"""
        self.block = False
        self.quit_button = Button(ENDGAME_QUIT_BUTTON_RECT,
                                  text='Quit',
                                  **ENDGAME_BUTTON_SETTINGS)
        self.restart_button = Button(ENDGAME_RESTART_BUTTON_RECT,
                                     text='Restart',
                                     **ENDGAME_BUTTON_SETTINGS)

    @staticmethod
    def get_screen_message(result, allegiance):
        """Produce the endgame screen message"""
        if result == 'Checkmate':
            return 'Checkmate!\n%s Wins' % allegiance.capitalize()
        return 'Stalemate!\nThe Game is Drawn'


class MultiLineSurface(Surface):
    """Class for surface containing the passed text string, reformatted
    to fit within the given rect, word-wrapping as necessary. The text
    will be anti-aliased.

    Parameters
    ----------
    string - the text you wish to render. \n begins a new line.
    font - a Font object
    rect - a rect style giving the size of the surface requested.
    font_colour - a three-byte tuple of the rgb value of the
             text colour. ex (0, 0, 0) = BLACK
    bg_colour - a three-byte tuple of the rgb value of the surface.
    justification - 0 (default) left-justified
                1 horizontally centered
                2 right-justified
    """

    def __init__(self, string, font_, rect, font_colour, bg_colour, justification=0):
        self.string = string
        self.font = font_
        self.rect_ext = rect
        self.font_colour = font_colour
        self.bg_colour = bg_colour
        self.justification = justification

        super(MultiLineSurface, self).__init__(self.rect_ext.size)

        self.surf = self.convert_alpha()
        self.rect = self.surf.get_rect()

        self.move_rect_ip(self.rect_ext.left, self.rect_ext.top)
        self.surf.fill(self.bg_colour)

        self.lines = []
        self.get_lines()
        self.do_blit()

    def move_rect_ip(self, left, top):
        """Move rect inplace"""
        self.rect.move_ip(left, top)

    def get_lines(self):
        """Create a series of lines that will fit on the provided rect"""
        font.init()
        requested_lines = self.string.splitlines()
        for requested_line in requested_lines:
            if self.font.size(requested_line)[0] > self.rect_ext.width:
                words = requested_line.split(' ')
                # if any of our words are too long to fit, return.
                for word in words:
                    if self.font.size(word)[0] >= self.rect_ext.width:
                        raise Exception(
                            'The word %s is too long to fit in the rect '
                            'passed.' % word)
                # Start a new line
                accumulated_line = ''
                for word in words:
                    test_line = accumulated_line + word + ' '
                    # Build the line while the words fit.
                    if self.font.size(test_line)[0] < self.rect_ext.width:
                        accumulated_line = test_line
                    else:
                        self.lines.append(accumulated_line)
                        accumulated_line = word + ' '
                self.lines.append(accumulated_line)
            else:
                self.lines.append(requested_line)

    def do_blit(self):
        """Blit text to the surface given the justification"""
        accumulated_height = self.rect_ext.height / \
            2 - self.font.size(self.lines[0])[1]
        for line in self.lines:
            if accumulated_height + self.font.size(line)[1] >= self.rect_ext.height:
                raise Exception(
                    'Once word-wrapped, the text string was too tall to fit '
                    'in the rect.')
            if line != '':
                temp_surface = self.font.render(line, 1, self.font_colour)
            if self.justification == 0:
                self.surf.blit(temp_surface, (0, accumulated_height))
            elif self.justification == 1:
                self.surf.blit(temp_surface,
                               ((self.rect_ext.width - temp_surface.get_width()) / 2,
                                accumulated_height))
            elif self.justification == 2:
                self.surf.blit(temp_surface,
                               (self.rect_ext.width - temp_surface.get_width(),
                                accumulated_height))
            else:
                raise Exception(
                    "Invalid justification argument: %s" % str(self.justification))
            accumulated_height += self.font.size(line)[1]


class Button(object):
    """A fairly straight forward button class."""

    def __init__(self, rect, colour, **kwargs):
        self.rect = Rect(rect)
        self.colour = colour
        self.clicked = False
        self.hovered = False
        self.hover_text = None
        self.clicked_text = None
        self.process_kwargs(kwargs)
        self.render_text()

    def process_kwargs(self, kwargs):
        """Various optional customization you can change by passing kwargs."""
        settings = {"text": None,
                    "width": 0,
                    "font": font.Font(None, 16),
                    "hover_colour": None,
                    "hover_width": 0,
                    "clicked_colour": None,
                    "clicked_width": 0,
                    "font_colour": (255, 255, 255),
                    "hover_font_colour": None,
                    "clicked_font_colour": None,
                    "click_sound": None,
                    "hover_sound": None}
        for kwarg in kwargs:
            if kwarg in settings:
                settings[kwarg] = kwargs[kwarg]
            else:
                raise AttributeError("Button has no keyword: %s" % kwarg)
        self.__dict__.update(settings)

    def render_text(self):
        """Pre render the button text."""
        if self.text:
            if self.hover_font_colour:
                colour = self.hover_font_colour
                self.hover_text = self.font.render(self.text, True, colour)
            if self.clicked_font_colour:
                colour = self.clicked_font_colour
                self.clicked_text = self.font.render(self.text, True, colour)
            self.text = self.font.render(self.text, True, self.font_colour)

    def check_click(self):
        """Check mouse position has collided with this button, if so it is clicked"""
        if self.rect.collidepoint(mouse.get_pos()):
            self.clicked = True

    def check_hover(self):
        """Check mouse position has collided with this button, if so it is hovering"""
        if self.rect.collidepoint(mouse.get_pos()):
            if not self.hovered:
                self.hovered = True
                if self.hover_sound:
                    self.hover_sound.play()
        else:
            self.hovered = False

    def update(self, surface):
        """Update needs to be called every frame in the main loop."""
        colour = self.colour
        text = self.text
        width = self.width
        self.check_hover()
        if self.clicked and self.clicked_colour:
            colour = self.clicked_colour
            width = self.clicked_width
            if self.clicked_font_colour:
                text = self.clicked_text
        elif self.hovered and self.hover_colour:
            colour = self.hover_colour
            width = self.hover_width
            if self.hover_font_colour:
                text = self.hover_text
        draw.rect(surface, colour, self.rect, width)
        if self.text:
            text_rect = text.get_rect(center=self.rect.center)
            surface.blit(text, text_rect)
