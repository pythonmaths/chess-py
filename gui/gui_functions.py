"""Functions used in the pygame gui"""

from pygame import Surface, Rect, draw, MOUSEMOTION, MOUSEBUTTONDOWN, MOUSEBUTTONUP
from gui.gui_settings import (CELL_SIZE, COLOURS, LIGHT_SQUARES, DARK_SQUARES,
                              SELECTED_PIECE, LEGAL_MOVES, ENPASSANT_MOVES,
                              CASTLING_MOVES, SPECIAL_MOVES, PIECE_IMAGES)
import utils

def update_screen(screen, board, legal_moves):
    """Draw the board and pieces"""
    draw_board(screen)
    draw_selected_cell(screen, board.pieces)
    draw_legal_moves(screen, legal_moves)
    draw_check_attackers(screen, board)
    draw_castling_moves(screen, board.pieces)
    draw_enpassant_moves(screen, board.pieces)
    draw_pieces(screen, board.pieces)


def draw_board(screen):
    """Draw the chess board surface"""
    board_surf = Surface((CELL_SIZE * 8, CELL_SIZE * 8))
    board_surf.fill(COLOURS[LIGHT_SQUARES])
    for x in range(8):
        for y in range(8):
            if (x % 2 == 1 and y % 2 == 0) or (x % 2 == 0 and y % 2 == 1):
                draw.rect(board_surf, COLOURS[DARK_SQUARES], (
                    x*CELL_SIZE, y*CELL_SIZE, CELL_SIZE, CELL_SIZE))
    screen.blit(board_surf, board_surf.get_rect())


def draw_selected_cell(screen, pieces):
    """Draw the currently selected cell"""
    for piece in pieces:
        if piece.selected:
            rect = get_rect(piece.pos_idx)
            draw.rect(screen, COLOURS[SELECTED_PIECE], rect)


def draw_legal_moves(screen, legal_moves):
    """Draw the legal moves for the currently selected player"""
    colour = COLOURS[LEGAL_MOVES]
    for legal_move in legal_moves:
        rect = get_rect(legal_move)
        draw.rect(screen, colour, rect, 5)


def draw_check_attackers(screen, board):
    """Draw the check attackers if any"""
    colour = COLOURS[SPECIAL_MOVES]
    if not board.last_move_info['success'] and get_selected_piece(board.pieces) is None:
        current_allegiance = board.players.current_player.allegiance
        rect = get_rect(board.pieces.get_king(current_allegiance).pos_idx)
        draw.rect(screen, colour, rect, 5)
        attackers = list(set(board.last_move_info['check_attackers']))
        for attacker in attackers:
            rect = get_rect(attacker)
            draw.rect(screen, colour, rect, 5)


def draw_castling_moves(screen, pieces):
    """Draw the castling moves for the currently selected player"""
    colour = COLOURS[CASTLING_MOVES]
    castle_moves = []
    for piece in pieces:
        if str(piece) == 'king' and piece.selected:
            if piece.king_side_castle_allowed and piece.king_side_castle_valid:
                castle_moves += [piece.king_side_transition[-1]]
            if piece.queen_side_castle_allowed and piece.queen_side_castle_valid:
                castle_moves += [piece.queen_side_transition[-1]]
            for castle_move in castle_moves:
                rect = get_rect(castle_move)
                draw.rect(screen, colour, rect, 5)


def draw_enpassant_moves(screen, pieces):
    """Draw the enpassant moves for the currently selected player"""
    colour = COLOURS[ENPASSANT_MOVES]
    for piece in pieces:
        if str(piece) == 'pawn' and piece.selected:
            for enpassant_move in piece.enpassant_move:
                rect = get_rect(enpassant_move)
                draw.rect(screen, colour, rect, 5)


def draw_pieces(screen, pieces):
    """Draw the pieces on the chess board"""
    for piece in pieces:
        piece_surf = PIECE_IMAGES[str(piece)]['cburnett'][piece.allegiance]
        piece_rect = get_rect(piece.pos_idx)
        if piece.dragging:
            piece_rect.x = piece.drag_x
            piece_rect.y = piece.drag_y
        screen.blit(piece_surf, piece_rect)


def get_rect(pos_idx):
    """
    Given a chessboard positional index return a rect with the correct x,y postion
    """
    x, y = utils.idx_to_rect(pos_idx, multiplier=CELL_SIZE)
    rect = Rect(x, y, CELL_SIZE, CELL_SIZE)
    return rect


def get_idx_from_mouse(mouse_pos):
    """Return index of mouse pos in unwrapped chessboard list"""
    x, y = mouse_pos
    cell_coords = [utils.idx_to_rect(i, multiplier=CELL_SIZE, offset=CELL_SIZE//2)
                   for i in range(64)]
    closest_coord = cell_coords[0]
    closest_coord_dist = (x-closest_coord[0])**2 + (y-closest_coord[1])**2
    for coord in cell_coords[1:]:
        dist = (x - coord[0])**2 + (y - coord[1])**2
        if dist <= closest_coord_dist:
            closest_coord_dist = dist
            closest_coord = coord
    idx = cell_coords.index(closest_coord)
    return idx


def get_closest_idx(piece):
    """Return the positional index of the square closest to dragged piece"""
    closest_idx = None
    closest_coord_dist = (piece.drag_x)**2 + (piece.drag_y)**2
    for i in range(64):
        x, y = utils.idx_to_rect(i, multiplier=CELL_SIZE)
        dist = (piece.drag_x - x)**2 + (piece.drag_y - y)**2
        if dist <= closest_coord_dist:
            closest_coord_dist = dist
            closest_idx = i
    return closest_idx


def get_clicked_piece(pieces, mouse):
    """Given the mouse position get the piece that was clicked if any"""
    for piece in pieces:
        piece_rect = get_rect(piece.pos_idx)
        if piece_rect.collidepoint(mouse):
            return piece
    return None


def get_selected_piece(pieces):
    """Return a piece if it has been selected"""
    for piece in pieces:
        if piece.selected:
            return piece
    return None

def update_pos_mouse(piece, mouse_pos):
    """Update the pieces offsets with a position from a mouse"""
    mouse_x, mouse_y = mouse_pos
    piece.drag_x = piece.offset_x + mouse_x
    piece.drag_y = piece.offset_y + mouse_y


def activate_piece(piece, mouse):
    """Activate a piece in the gui"""
    piece.selected = True
    piece.dragging = True
    x, y = utils.idx_to_rect(piece.pos_idx, multiplier=CELL_SIZE)
    piece.offset_x = x - mouse[0]
    piece.offset_y = y - mouse[1]
    piece.drag_x = x
    piece.drag_y = y


def deactivate_piece(piece):
    """Initialise piece with gui state"""
    piece.selected = False
    piece.dragging = False


def init_gui_piece(piece):
    """Initialise piece with gui state"""
    setattr(piece, 'selected', False)
    setattr(piece, 'dragging', False)
    setattr(piece, 'offset_x', None)
    setattr(piece, 'offset_y', None)
    setattr(piece, 'drag_x', None)
    setattr(piece, 'drag_y', None)


def handle_mouse_event(event, board, legal_moves):
    """This method controls the logic for various mouse interactions"""
    if board.players.current_player.is_human:
        if event.type == MOUSEBUTTONDOWN:
            handle_mouse_down_event(board, legal_moves, event.pos)
        elif event.type == MOUSEBUTTONUP:
            handle_mouse_up_event(board, legal_moves)
        elif event.type == MOUSEMOTION:
            handle_mouse_motion_event(board, event.pos)


def handle_mouse_down_event(board, legal_moves, mouse):
    """This method defines what happens on a mouse down click"""
    board.update()
    clicked_piece = get_clicked_piece(board.pieces, mouse)
    selected_piece = get_selected_piece(board.pieces)
    # Nothing Selected
    if selected_piece is None:
        # Clicked a piece
        if (clicked_piece is not None and
                clicked_piece.allegiance == board.players.current_player.allegiance):
            activate_piece(clicked_piece, mouse)
            legal_moves.update(clicked_piece.legal_moves)
            for piece in board.pieces:
                if piece != clicked_piece:
                    deactivate_piece(piece)
        # Clicked an empty square
        else:
            legal_moves.clear()
    # Piece Selected
    else:
        # Clicked a piece
        if clicked_piece is not None:
            if clicked_piece == selected_piece:
                activate_piece(clicked_piece, mouse)
            elif clicked_piece.pos_idx in legal_moves:
                board.turn(selected_piece, clicked_piece.pos_idx)
                deactivate_piece(selected_piece)
                legal_moves.clear()
            elif clicked_piece.allegiance == board.players.current_player.allegiance:
                deactivate_piece(selected_piece)
                activate_piece(clicked_piece, mouse)
                legal_moves.update(clicked_piece.legal_moves)
            else:
                deactivate_piece(selected_piece)
                legal_moves.clear()
        # Clicked an empty square
        else:
            clicked_idx = get_idx_from_mouse(mouse)
            if clicked_idx in legal_moves:
                board.turn(selected_piece, clicked_idx)
                deactivate_piece(selected_piece)
                legal_moves.clear()
            else:
                deactivate_piece(selected_piece)
                legal_moves.clear()


def handle_mouse_up_event(board, legal_moves):
    """This method defines what happens on a mouse up click"""
    selected_piece = get_selected_piece(board.pieces)
    if selected_piece is not None:
        selected_piece.dragging = False
        drag_idx = get_closest_idx(selected_piece)
        if selected_piece.pos_idx != drag_idx:
            if drag_idx in legal_moves:
                board.turn(selected_piece, drag_idx)
            #else:
            #    selected_piece.update_pos(selected_piece.pos_idx)
            deactivate_piece(selected_piece)
            legal_moves.clear()


def handle_mouse_motion_event(board, mouse):
    """This method defines what happens on mouse motion"""
    for piece in board.pieces:
        if piece.dragging:
            update_pos_mouse(piece, mouse)
