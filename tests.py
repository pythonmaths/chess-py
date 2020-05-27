"""ChessPlay test suite"""
import unittest
from collections.abc import Iterable
import re
import chessboard
import fen
import settings
import utils

VALID_FEN_STRINGS = [settings.FEN_START_STATE,
                     'r6r/1b2k1bq/8/8/7B/8/8/R3K2R b QK - 3 2',
                     '8/8/8/2k5/2pP4/8/B7/4K3 b - d3 5 3',
                     'r1bqkbnr/pppppppp/n7/8/8/P7/1PPPPPPP/RNBQKBNR w QqKk - 2 2',
                     'r3k2r/p1pp1pb1/bn2Qnp1/2qPN3/1p2P3/2N5/PPPBBPPP/R3K2R b QqKk - 3 2',
                     '2kr3r/p1ppqpb1/bn2Qnp1/3PN3/1p2P3/2N5/PPPBBPPP/R3K2R b QK - 3 2',
                     'rnb2k1r/pp1Pbppp/2p5/q7/2B5/8/PPPQNnPP/RNB1K2R w QK - 3 9',
                     '2r5/3pk3/8/2P5/8/2K5/8/8 w - - 5 4',
                     'rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KQ - 1 8',
                     'r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10',
                     '3k4/3p4/8/K1P4r/8/8/8/8 b - - 0 1',
                     '8/8/4k3/8/2p5/8/B2P2K1/8 w - - 0 1',
                     '8/8/1k6/2b5/2pP4/8/5K2/8 b - d3 0 1',
                     '5k2/8/8/8/8/8/8/4K2R w K - 0 1',
                     '3k4/8/8/8/8/8/8/R3K3 w Q - 0 1',
                     'r3k2r/1b4bq/8/8/8/8/7B/R3K2R w KQkq - 0 1',
                     'r3k2r/8/3Q4/8/8/5q2/8/R3K2R b KQkq - 0 1',
                     '2K2r2/4P3/8/8/8/8/8/3k4 w - - 0 1',
                     '8/8/1P2K3/8/2n5/1q6/8/5k2 b - - 0 1',
                     '4k3/1P6/8/8/8/8/K7/8 w - - 0 1',
                     '8/P1k5/K7/8/8/8/8/8 w - - 0 1',
                     'K1k5/8/P7/8/8/8/8/8 w - - 0 1',
                     '8/k1P5/8/1K6/8/8/8/8 w - - 0 1',
                     '8/8/2k5/5q2/5n2/8/5K2/8 b - - 0 1']

INVALID_FEN_STRINGS = ['r6r1b2k1bq/8/8/7B/8/8/R3K2R b QK - 3 2',
                       '8/8/8/2Z5/2pP4/8/w7/4K3 b - d3 5 3',
                       'r1bqkbnr/pppppppp/n6/8/8/P7/1PPPPPPP/RNBQKBNR w QqKk - 2 2',
                       'r3k2r/p1pp1pb1/bn2np1/2qPN3/1p2P3/2N5/PPPBBPPP/R3K2R b QqKk - 3 2',
                       '2kr3r/p1ppqpb1/bn2Qnp1/3PN3/1p2P3/2N5/PPPBBPPP/R3K2R B QK - 3 2',
                       'rnb2k1r/pp1Pbppp/2p5/q7/2B5/8/PPPQNnPP/RNB1K2R x QK - 3 9',
                       '2r5/3pk3/8/2P5/8/2K5/8/8 w pQ - 5 4',
                       'rnbq1k1r/pp1Pbppp/2p5/8/2B5/8/PPP1NnPP/RNBQK2R w KKQ - 1 8',
                       'r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w KKQQq - 0 10',
                       '3k4/3p4/8/K1P4r/8/8/8/8 b - d4 0 1',
                       '8/8/4k3/8/2p5/8/B2P2K1/8 w - e7 0 1',
                       '8/8/1k6/2b5/2pP4/8/5K2/8 b - ee 0 1',
                       '5k2/8/8/8/8/8/8/4K2R w K 33 0 1',
                       '3k4/8/8/8/8/8/8/R3K3 w Q - 0 v',
                       'r3k2r/1b4bq/8/8/8/8/7B/R3K2R w KQkq - z 1',
                       'r3k2r/8/3Q4/8/8/5q2/8/R3K2R b KQkq - Z 1',
                       'defo_invalid',
                       '8/8/1P2K3/8/2n5/1q6/8/5k2']

class TestBoard(unittest.TestCase):
    """Test the Board class"""

    def test_board_initialisation(self):
        """Make sure the FEN string used to initialise the board is reproduced"""
        for input_str in VALID_FEN_STRINGS:
            board = chessboard.Board(start_state=input_str)
            output_str = board.get_FEN()
            # Sort the castling part of input str as output str always sorts
            input_str = re.sub(r'\s([KkQq-]+)\s',
                               lambda m: ' ' + ''.join(sorted(m.group(1))) + ' ',
                               input_str)
            self.assertEqual(input_str, output_str)

    def test_board_initialisation_w_reset(self):
        """
        Make sure the FEN string used to initialise the board is reproduced
        even after a rest
        """
        for input_str in VALID_FEN_STRINGS:
            board = chessboard.Board()
            board.reset(start_state=input_str)
            output_str = board.get_FEN()
            # Sort the castling part of input str as output str always sorts
            input_str = re.sub(r'\s([KkQq-]+)\s',
                               lambda m: ' ' +
                               ''.join(sorted(m.group(1))) + ' ',
                               input_str)
            self.assertEqual(input_str, output_str)

    def test_algebraic_board_funcs(self):
        """
        Algebraic functions should except both algebraic format and positional
        indexes
        """
        board = chessboard.Board()
        self.assertEqual(board.is_occupied(0), board.is_occupied('a8'))
        self.assertEqual(board.is_occupied(56), board.is_occupied('a1'))
        self.assertEqual(board.is_occupied(31), board.is_occupied('h5'))
        self.assertEqual(board.get_piece(0), board.get_piece('a8'))
        self.assertEqual(board.get_piece(56), board.get_piece('a1'))
        self.assertEqual(board.get_piece(31), board.get_piece('h5'))
        self.assertEqual(board.get_piece_name(0), board.get_piece_name('a8'))
        self.assertEqual(board.get_piece_name(56), board.get_piece_name('a1'))
        self.assertEqual(board.get_piece_name(31), board.get_piece_name('h5'))

    def test_algebraic_board_funcs_error(self):
        """
        Algebraic functions should error for inputs other than algebraic format
        and positional indexes (int)
        """
        board = chessboard.Board()
        with self.assertRaises(utils.AlgebraicFuncException):
            board.get_piece('0')
        with self.assertRaises(utils.AlgebraicFuncException):
            board.get_piece('a')
        with self.assertRaises(utils.AlgebraicFuncException):
            board.get_piece('k8')
        with self.assertRaises(utils.AlgebraicFuncException):
            board.get_piece(64)
        with self.assertRaises(utils.AlgebraicFuncException):
            board.get_piece(1.0)
        with self.assertRaises(utils.AlgebraicFuncException):
            board.get_piece(board)
        with self.assertRaises(utils.AlgebraicFuncException):
            board.get_piece(board.get_FEN)
        with self.assertRaises(utils.AlgebraicFuncException):
            board.get_piece(board.get_FEN())

class TestPieces(unittest.TestCase):
    """Test the Piece container class/Ordered Dict"""

    def test_pieces_ordered_dict(self):
        """
        Pieces should be added to front of list and stay in order
        Kings should be added to the back of the list
        """
        pieces = chessboard.Pieces()
        rook0 = chessboard.Rook()
        rook1 = chessboard.Rook()
        rook2 = chessboard.Rook()
        pieces.add(rook0, rook1, rook2)
        self.assertEqual(pieces.pieces()[2], rook0)
        self.assertEqual(pieces.pieces()[1], rook1)
        self.assertEqual(pieces.pieces()[0], rook2)

        king0 = chessboard.King()
        king1 = chessboard.King()
        pieces.add(king0, king1)
        self.assertEqual(pieces.pieces()[3], king0)
        self.assertEqual(pieces.pieces()[4], king1)

        self.assertTrue(pieces.has(rook0))
        self.assertTrue(pieces.has(king1))

        pieces.remove(rook2, king1)
        self.assertEqual(pieces.pieces()[2], king0)
        self.assertEqual(pieces.pieces()[1], rook0)
        self.assertEqual(pieces.pieces()[0], rook1)

        pieces.reset()
        self.assertFalse(bool(pieces.pieces_dict))

    def test_pieces_is_a_list(self):
        """Pieces class should act like a list"""
        pieces = chessboard.Pieces()
        self.assertFalse(bool(pieces))
        rook0 = chessboard.Rook()
        rook1 = chessboard.Rook()
        rook2 = chessboard.Rook()
        pieces.add(rook0, rook1, rook2)
        self.assertTrue(bool(pieces))
        self.assertTrue(isinstance(pieces, Iterable))

    def test_piece_rejection(self):
        """Pieces class should reject pieces that don't inherit them piece class"""
        pieces = chessboard.Pieces()
        non_piece = chessboard.Human()
        with self.assertRaises(TypeError):
            pieces.add(non_piece)


class TestPieceMovePool(unittest.TestCase):
    """
    Test the move pool of both generic and specific pieces in different board
    positions
    """

    def test_generic_piece_move_pool(self):
        """
        Place a generic piece in the middle of the board/corner and make sure the
        returned directional moves are correct
        """
        piece = chessboard.Piece()
        piece.pos_idx = 26
        piece.allegiance = 'white'

        self.assertEqual(piece.fwd(1), ['c6'])
        self.assertEqual(piece.bkwd(1), ['c4'])
        self.assertEqual(piece.left(1), ['b5'])
        self.assertEqual(piece.right(1), ['d5'])
        self.assertEqual(piece.dgfl(1), ['b6'])
        self.assertEqual(piece.dgfr(1), ['d6'])
        self.assertEqual(piece.dgbl(1), ['b4'])
        self.assertEqual(piece.dgbr(1), ['d4'])

        self.assertEqual(piece.fwd(1, pos_idx=True), [18])
        self.assertEqual(piece.bkwd(1, pos_idx=True), [34])
        self.assertEqual(piece.left(1, pos_idx=True), [25])
        self.assertEqual(piece.right(1, pos_idx=True), [27])
        self.assertEqual(piece.dgfl(1, pos_idx=True), [17])
        self.assertEqual(piece.dgfr(1, pos_idx=True), [19])
        self.assertEqual(piece.dgbl(1, pos_idx=True), [33])
        self.assertEqual(piece.dgbr(1, pos_idx=True), [35])

        self.assertEqual(piece.fwd(), ['c6', 'c7', 'c8'])
        self.assertEqual(piece.bkwd(), ['c4', 'c3', 'c2', 'c1'])
        self.assertEqual(piece.left(), ['b5', 'a5'])
        self.assertEqual(piece.right(), ['d5', 'e5', 'f5', 'g5', 'h5'])
        self.assertEqual(piece.dgfl(), ['b6', 'a7'])
        self.assertEqual(piece.dgfr(), ['d6', 'e7', 'f8'])
        self.assertEqual(piece.dgbl(), ['b4', 'a3'])
        self.assertEqual(piece.dgbr(), ['d4', 'e3', 'f2', 'g1'])

        piece = chessboard.Piece()
        piece.pos_idx = 0
        piece.allegiance = 'white'

        self.assertEqual(piece.fwd(1), [])
        self.assertEqual(piece.bkwd(1), ['a7'])
        self.assertEqual(piece.left(1), [])
        self.assertEqual(piece.right(1), ['b8'])
        self.assertEqual(piece.dgfl(1), [])
        self.assertEqual(piece.dgfr(1), [])
        self.assertEqual(piece.dgbl(1), [])
        self.assertEqual(piece.dgbr(1), ['b7'])

        self.assertEqual(piece.fwd(1, pos_idx=True), [])
        self.assertEqual(piece.bkwd(1, pos_idx=True), [8])
        self.assertEqual(piece.left(1, pos_idx=True), [])
        self.assertEqual(piece.right(1, pos_idx=True), [1])
        self.assertEqual(piece.dgfl(1, pos_idx=True), [])
        self.assertEqual(piece.dgfr(1, pos_idx=True), [])
        self.assertEqual(piece.dgbl(1, pos_idx=True), [])
        self.assertEqual(piece.dgbr(1, pos_idx=True), [9])

        self.assertEqual(piece.fwd(), [])
        self.assertEqual(piece.bkwd(), ['a7', 'a6', 'a5', 'a4', 'a3', 'a2', 'a1'])
        self.assertEqual(piece.left(), [])
        self.assertEqual(piece.right(), ['b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8'])
        self.assertEqual(piece.dgfl(), [])
        self.assertEqual(piece.dgfr(), [])
        self.assertEqual(piece.dgbl(), [])
        self.assertEqual(piece.dgbr(), ['b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1'])

        piece = chessboard.Piece()
        piece.pos_idx = 26
        piece.allegiance = 'black'

        self.assertEqual(piece.fwd(1), ['c4'])
        self.assertEqual(piece.bkwd(1), ['c6'])
        self.assertEqual(piece.left(1), ['d5'])
        self.assertEqual(piece.right(1), ['b5'])
        self.assertEqual(piece.dgfl(1), ['d4'])
        self.assertEqual(piece.dgfr(1), ['b4'])
        self.assertEqual(piece.dgbl(1), ['d6'])
        self.assertEqual(piece.dgbr(1), ['b6'])

        self.assertEqual(piece.fwd(1, pos_idx=True), [34])
        self.assertEqual(piece.bkwd(1, pos_idx=True), [18])
        self.assertEqual(piece.left(1, pos_idx=True), [27])
        self.assertEqual(piece.right(1, pos_idx=True), [25])
        self.assertEqual(piece.dgfl(1, pos_idx=True), [35])
        self.assertEqual(piece.dgfr(1, pos_idx=True), [33])
        self.assertEqual(piece.dgbl(1, pos_idx=True), [19])
        self.assertEqual(piece.dgbr(1, pos_idx=True), [17])

        self.assertEqual(piece.fwd(), ['c4', 'c3', 'c2', 'c1'])
        self.assertEqual(piece.bkwd(), ['c6', 'c7', 'c8'])
        self.assertEqual(piece.left(), ['d5', 'e5', 'f5', 'g5', 'h5'])
        self.assertEqual(piece.right(), ['b5', 'a5'])
        self.assertEqual(piece.dgfl(), ['d4', 'e3', 'f2', 'g1'])
        self.assertEqual(piece.dgfr(), ['b4', 'a3'])
        self.assertEqual(piece.dgbl(), ['d6', 'e7', 'f8'])
        self.assertEqual(piece.dgbr(), ['b6', 'a7'])

        piece = chessboard.Piece()
        piece.pos_idx = 0
        piece.allegiance = 'black'

        self.assertEqual(piece.fwd(1), ['a7'])
        self.assertEqual(piece.bkwd(1), [])
        self.assertEqual(piece.left(1), ['b8'])
        self.assertEqual(piece.right(1), [])
        self.assertEqual(piece.dgfl(1), ['b7'])
        self.assertEqual(piece.dgfr(1), [])
        self.assertEqual(piece.dgbl(1), [])
        self.assertEqual(piece.dgbr(1), [])

        self.assertEqual(piece.fwd(1, pos_idx=True), [8])
        self.assertEqual(piece.bkwd(1, pos_idx=True), [])
        self.assertEqual(piece.left(1, pos_idx=True), [1])
        self.assertEqual(piece.right(1, pos_idx=True), [])
        self.assertEqual(piece.dgfl(1, pos_idx=True), [9])
        self.assertEqual(piece.dgfr(1, pos_idx=True), [])
        self.assertEqual(piece.dgbl(1, pos_idx=True), [])
        self.assertEqual(piece.dgbr(1, pos_idx=True), [])

        self.assertEqual(piece.fwd(), ['a7', 'a6', 'a5', 'a4', 'a3', 'a2', 'a1'])
        self.assertEqual(piece.bkwd(), [])
        self.assertEqual(piece.left(), ['b8', 'c8', 'd8', 'e8', 'f8', 'g8', 'h8'])
        self.assertEqual(piece.right(), [])
        self.assertEqual(piece.dgfl(), ['b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1'])
        self.assertEqual(piece.dgfr(), [])
        self.assertEqual(piece.dgbl(), [])
        self.assertEqual(piece.dgbr(), [])

    def test_king_move_pool(self):
        """
        Place a king in the middle of the board/corner and make sure the
        returned directional moves are correct
        Move pool should be symmetric for black and white king
        """
        white_piece = chessboard.King(init_position=26, allegiance='white')
        white_move_pool = flatten(white_piece.get_move_pool().values())
        self.assertCountEqual(white_move_pool, ['c6', 'c4', 'b5', 'd5', 'b6', 'd6', 'b4', 'd4'])

        black_piece = chessboard.King(init_position=26, allegiance='black')
        black_move_pool = flatten(black_piece.get_move_pool().values())
        self.assertCountEqual(white_move_pool, black_move_pool)

        piece = chessboard.King(init_position=0, allegiance='white')
        move_pool = flatten(piece.get_move_pool().values())
        self.assertCountEqual(move_pool, ['a7', 'b8', 'b7'])

    def test_bishop_move_pool(self):
        """
        Place a bishop in the middle of the board/corner and make sure the
        returned directional moves are correct
        Move pool should be symmetric for black and white bishop
        """
        white_piece = chessboard.Bishop(init_position=26, allegiance='white')
        white_move_pool = flatten(white_piece.get_move_pool().values())
        self.assertCountEqual(
            white_move_pool, ['b6', 'a7', 'd6', 'e7', 'f8', 'b4', 'a3', 'd4', 'e3', 'f2', 'g1'])

        black_piece = chessboard.Bishop(init_position=26, allegiance='black')
        black_move_pool = flatten(black_piece.get_move_pool().values())
        self.assertCountEqual(white_move_pool, black_move_pool)

        piece = chessboard.Bishop(init_position=0, allegiance='white')
        move_pool = flatten(piece.get_move_pool().values())
        self.assertCountEqual(move_pool, ['b7', 'c6', 'd5', 'e4', 'f3', 'g2', 'h1'])

    def test_rook_move_pool(self):
        """
        Place a rook in the middle of the board/corner and make sure the
        returned directional moves are correct
        Move pool should be symmetric for black and white rook
        """
        white_piece = chessboard.Rook(init_position=26, allegiance='white')
        white_move_pool = flatten(white_piece.get_move_pool().values())
        self.assertCountEqual(
            white_move_pool, ['c6', 'c7', 'c8', 'c4', 'c3', 'c2', 'c1', 'b5',
                              'a5', 'd5', 'e5', 'f5', 'g5', 'h5'])

        black_piece = chessboard.Rook(init_position=26, allegiance='black')
        black_move_pool = flatten(black_piece.get_move_pool().values())
        self.assertCountEqual(white_move_pool, black_move_pool)

        piece = chessboard.Rook(init_position=0, allegiance='white')
        move_pool = flatten(piece.get_move_pool().values())
        self.assertCountEqual(
            move_pool, ['a7', 'a6', 'a5', 'a4', 'a3', 'a2', 'a1', 'b8', 'c8',
                        'd8', 'e8', 'f8', 'g8', 'h8'])

    def test_queen_move_pool(self):
        """
        Place a queen in the middle of the board/corner and make sure the
        returned directional moves are correct
        Move pool should be symmetric for black and white queen
        """
        white_piece = chessboard.Queen(init_position=26, allegiance='white')
        white_move_pool = flatten(white_piece.get_move_pool().values())
        self.assertCountEqual(
            white_move_pool, ['c6', 'c7', 'c8', 'c4', 'c3', 'c2', 'c1', 'b5',
                              'a5', 'd5', 'e5', 'f5', 'g5', 'h5', 'b6', 'a7',
                              'd6', 'e7', 'f8', 'b4', 'a3', 'd4', 'e3', 'f2',
                              'g1'])

        black_piece = chessboard.Queen(init_position=26, allegiance='black')
        black_move_pool = flatten(black_piece.get_move_pool().values())
        self.assertCountEqual(white_move_pool, black_move_pool)

        piece = chessboard.Queen(init_position=0, allegiance='white')
        move_pool = flatten(piece.get_move_pool().values())
        self.assertCountEqual(
            move_pool, ['a7', 'a6', 'a5', 'a4', 'a3', 'a2', 'a1', 'b8', 'c8',
                        'd8', 'e8', 'f8', 'g8', 'h8', 'b7', 'c6', 'd5', 'e4',
                        'f3', 'g2', 'h1'])

    def test_knight_move_pool(self):
        """
        Place a knight in the middle of the board/corner and make sure the
        returned directional moves are correct
        Move pool should be symmetric for black and white knight
        """
        white_piece = chessboard.Knight(init_position=26, allegiance='white')
        white_move_pool = flatten(white_piece.get_move_pool().values())
        self.assertCountEqual(
            white_move_pool, ['b7', 'd7', 'a6', 'e6', 'e4', 'a4', 'd3', 'b3'])

        black_piece = chessboard.Knight(init_position=26, allegiance='black')
        black_move_pool = flatten(black_piece.get_move_pool().values())
        self.assertCountEqual(white_move_pool, black_move_pool)

        piece = chessboard.Knight(init_position=0, allegiance='white')
        move_pool = flatten(piece.get_move_pool().values())
        self.assertCountEqual(move_pool, ['c7', 'b6'])

    def test_pawn_move_pool(self):
        """
        Place a pawn in the middle of the board/corner and make sure the
        returned directional moves are correct
        Move pool is non symmetric for black and white pawn
        """
        white_piece = chessboard.Pawn(init_position=26, allegiance='white')
        white_move_pool = flatten(white_piece.get_move_pool().values())
        self.assertCountEqual(white_move_pool, ['c6', 'c7', 'b6', 'd6'])

        black_piece = chessboard.Pawn(init_position=26, allegiance='black')
        black_move_pool = flatten(black_piece.get_move_pool().values())
        self.assertCountEqual(black_move_pool, ['c4', 'c3', 'b4', 'd4'])

        white_piece = chessboard.Pawn(init_position=0, allegiance='white')
        white_move_pool = flatten(white_piece.get_move_pool().values())
        self.assertCountEqual(white_move_pool, [])

        black_piece = chessboard.Pawn(init_position=0, allegiance='black')
        black_move_pool = flatten(black_piece.get_move_pool().values())
        self.assertCountEqual(black_move_pool, ['a7', 'a6', 'b7'])

class TestLegalMoves(unittest.TestCase):
    """Test the legal moves for each piece type are correct in different setups"""

    FEN = [settings.FEN_START_STATE,
           '8/8/8/2k5/2pP4/8/B7/4K3 b - d3 5 3',
           'r4rk1/1pp1qppp/p1np1n2/2b1p1B1/2B1P1b1/P1NP1N2/1PP1QPPP/R4RK1 w - - 0 10',
           'r6r/1b2k1bq/8/8/7B/8/8/R3K2R b QK - 3 2']

    def test_get_legal_moves_output(self):
        """Test the pos_idx keyword argument works"""
        board = chessboard.Board(start_state=self.FEN[0])
        self.assertCountEqual(board.get_legal_moves('a7'), ['a6', 'a5'])
        self.assertCountEqual(board.get_legal_moves('a7', pos_idx=True), [16, 24])

    def test_pawn_legal_moves(self):
        """Make sure legal moves are correct for pawn in different setups"""
        board = chessboard.Board(start_state=self.FEN[0])
        self.assertCountEqual(board.get_legal_moves('a7'), ['a6', 'a5'])
        self.assertCountEqual(board.get_legal_moves('a2'), ['a3', 'a4'])
        board = chessboard.Board(start_state=self.FEN[1])
        self.assertCountEqual(board.get_legal_moves('d4'), ['c5', 'd5'])
        board = chessboard.Board(start_state=self.FEN[2])
        self.assertCountEqual(board.get_legal_moves('a6'), ['a5'])
        self.assertCountEqual(board.get_legal_moves('a3'), ['a4'])

    def test_bishop_legal_moves(self):
        """Make sure legal moves are correct for bishop in different setups"""
        board = chessboard.Board(start_state=self.FEN[0])
        self.assertCountEqual(board.get_legal_moves('c8'), [])
        self.assertCountEqual(board.get_legal_moves('c1'), [])
        board = chessboard.Board(start_state=self.FEN[1])
        self.assertCountEqual(board.get_legal_moves('a2'), ['b3', 'c4', 'b1'])
        board = chessboard.Board(start_state=self.FEN[2])
        self.assertCountEqual(board.get_legal_moves('c5'), ['d4', 'e3', 'f2', 'b4',
                                                            'a3', 'b6', 'a7'])
        self.assertCountEqual(board.get_legal_moves('c4'), ['b5', 'a6', 'd5', 'e6',
                                                            'f7', 'b3', 'a2'])

    def test_rook_legal_moves(self):
        """Make sure legal moves are correct for rook in different setups"""
        board = chessboard.Board(start_state=self.FEN[0])
        self.assertCountEqual(board.get_legal_moves('a8'), [])
        self.assertCountEqual(board.get_legal_moves('a1'), [])
        board = chessboard.Board(start_state=self.FEN[2])
        self.assertCountEqual(board.get_legal_moves('f8'), ['e8', 'd8', 'c8', 'b8'])
        self.assertCountEqual(board.get_legal_moves('f1'), ['e1', 'd1', 'c1', 'b1'])
        board = chessboard.Board(start_state=self.FEN[3])
        self.assertCountEqual(board.get_legal_moves('a8'), ['g8', 'f8', 'e8', 'd8',
                                                            'c8', 'b8', 'a7', 'a6',
                                                            'a5', 'a4', 'a3', 'a2',
                                                            'a1'])
        self.assertCountEqual(board.get_legal_moves('a1'), ['b1', 'c1', 'd1', 'a8',
                                                            'a7', 'a6', 'a5', 'a4',
                                                            'a3', 'a2'])

    def test_queen_legal_moves(self):
        """Make sure legal moves are correct for queen in different setups"""
        board = chessboard.Board(start_state=self.FEN[0])
        self.assertCountEqual(board.get_legal_moves('d8'), [])
        self.assertCountEqual(board.get_legal_moves('d1'), [])
        board = chessboard.Board(start_state=self.FEN[2])
        self.assertCountEqual(board.get_legal_moves('e7'), ['e6', 'e8', 'd7', 'd8'])
        self.assertCountEqual(board.get_legal_moves('e2'), ['e1', 'e3', 'd1', 'd2'])
        board = chessboard.Board(start_state=self.FEN[3])
        self.assertCountEqual(board.get_legal_moves('h7'), ['h6', 'h5', 'h4', 'g6',
                                                            'f5', 'e4', 'd3', 'c2',
                                                            'b1', 'g8'])

    def test_knight_legal_moves(self):
        """Make sure legal moves are correct for knight in different setups"""
        board = chessboard.Board(start_state=self.FEN[0])
        self.assertCountEqual(board.get_legal_moves('b8'), ['a6', 'c6'])
        self.assertCountEqual(board.get_legal_moves('b1'), ['a3', 'c3'])
        board = chessboard.Board(start_state=self.FEN[2])
        self.assertCountEqual(board.get_legal_moves('f6'), ['d7', 'd5', 'e8', 'h5',
                                                            'e4'])
        self.assertCountEqual(board.get_legal_moves('f3'), ['d4', 'd2', 'e1', 'h4',
                                                            'e5'])

    def test_king_legal_moves(self):
        """Make sure legal moves are correct for king in different setups"""
        board = chessboard.Board(start_state=self.FEN[0])
        self.assertCountEqual(board.get_legal_moves('e8'), [])
        self.assertCountEqual(board.get_legal_moves('e1'), [])
        board = chessboard.Board(start_state=self.FEN[1])
        self.assertCountEqual(board.get_legal_moves('c5'), ['b4', 'b5', 'b6', 'c6',
                                                            'd6', 'd5', 'd4'])
        self.assertCountEqual(board.get_legal_moves('e1'), ['d1', 'd2', 'e2', 'f2',
                                                            'f1'])
        board = chessboard.Board(start_state=self.FEN[2])
        self.assertCountEqual(board.get_legal_moves('g8'), ['h8'])
        self.assertCountEqual(board.get_legal_moves('g1'), ['h1'])
        board = chessboard.Board(start_state=self.FEN[3])
        self.assertCountEqual(board.get_legal_moves('e7'), ['d6', 'd7', 'd8', 'e8',
                                                            'f8', 'f7', 'e6'])


class TestCheck(unittest.TestCase):
    pass






class TestUtils(unittest.TestCase):
    """Test the common utilities in the Utils class"""

    def test_algebra_to_idx(self):
        """Check algebra to positional index conversion works"""
        self.assertEqual(utils.algebra_to_idx('a1'), 56)
        self.assertEqual(utils.algebra_to_idx('a8'), 0)
        self.assertEqual(utils.algebra_to_idx('h1'), 63)
        self.assertEqual(utils.algebra_to_idx('e5'), 28)
        with self.assertRaises(utils.InvalidAlgebraException):
            utils.algebra_to_idx('e')
        with self.assertRaises(utils.InvalidAlgebraException):
            utils.algebra_to_idx('5')
        with self.assertRaises(utils.InvalidAlgebraException):
            utils.algebra_to_idx(1)
        with self.assertRaises(utils.InvalidAlgebraException):
            utils.algebra_to_idx('k2')
        with self.assertRaises(utils.InvalidAlgebraException):
            utils.algebra_to_idx(utils)

    def test_idx_to_algebra(self):
        """Check positional index to algebra conversion works"""
        self.assertEqual(utils.idx_to_algebra(56), 'a1')
        self.assertEqual(utils.idx_to_algebra(0), 'a8')
        self.assertEqual(utils.idx_to_algebra(63), 'h1')
        self.assertEqual(utils.idx_to_algebra(28), 'e5')
        with self.assertRaises(utils.InvalidPosIdxException):
            utils.idx_to_algebra('e')
        with self.assertRaises(utils.InvalidPosIdxException):
            utils.idx_to_algebra('5')
        with self.assertRaises(utils.InvalidPosIdxException):
            utils.idx_to_algebra(67)
        with self.assertRaises(utils.InvalidPosIdxException):
            utils.idx_to_algebra('k2')
        with self.assertRaises(utils.InvalidPosIdxException):
            utils.idx_to_algebra(utils)

    def test_is_algebraic(self):
        """Check algebraic notation validation"""
        self.assertTrue(utils.is_algebraic('a4'))
        self.assertTrue(utils.is_algebraic('d2'))
        self.assertTrue(utils.is_algebraic('h1'))
        self.assertFalse(utils.is_algebraic('a'))
        self.assertFalse(utils.is_algebraic('a11'))
        self.assertFalse(utils.is_algebraic('k3'))
        self.assertFalse(utils.is_algebraic(utils))

    def test_is_pos_idx(self):
        """Check algebra notation validation"""
        self.assertTrue(utils.is_pos_idx(0))
        self.assertTrue(utils.is_pos_idx(34))
        self.assertTrue(utils.is_pos_idx(63))
        self.assertFalse(utils.is_pos_idx(64))
        self.assertFalse(utils.is_pos_idx(-1))
        self.assertFalse(utils.is_pos_idx(1.0))
        self.assertFalse(utils.is_pos_idx(utils))
        self.assertFalse(utils.is_pos_idx('63'))


class TestFENParser(unittest.TestCase):
    """Test the validity checking and parsing functions of the FENParser class"""

    def test_fen_validities(self):
        """FENParser should determine correclty whether a FEN string is valid/invalid"""

        for str_ in VALID_FEN_STRINGS:
            self.assertTrue(fen.FENParser(str_).is_valid())
        for str_ in INVALID_FEN_STRINGS:
            self.assertFalse(fen.FENParser(str_).is_valid())

    def test_fen_parsing_start_state(self):
        """FENParser should parse the Chess start state correctly"""
        p = fen.FENParser(settings.FEN_START_STATE)
        p.parse()

        self.assertEqual(len(p.record), 32) #32 Pieces
        self.assertEqual(len([x for x in p.record if x['piece_name'] == 'pawn']), 16) # 16 Pawns
        self.assertEqual(len([x for x in p.record if x['piece_name'] == 'king']), 2)  # 2 Kings

        kings = [x for x in p.record if x['piece_name'] == 'king']
        self.assertNotEqual(kings[0], kings[1])  # 2 Different Kings

        white_king = [x for x in kings if x['allegiance'] == 'white']
        self.assertEqual(white_king[0]['pos_idx'], 60)  # White King in right position

        self.assertEqual(p.active_allegiance, 'w') # White is first to move

        for king in kings:
            # Castling should be available
            self.assertTrue(king['queen_side_castle_allowed'])
            self.assertTrue(king['king_side_castle_allowed'])

    def test_fen_parsing_nonstart_state(self):
        """FENParser should parse the Chess start state correctly"""
        p = fen.FENParser('8/8/1k6/2b5/2pP4/8/5K2/8 b - d3 0 1')
        p.parse()

        self.assertEqual(len(p.record), 5)  # 5 Pieces
        self.assertEqual(
            len([x for x in p.record if x['piece_name'] == 'pawn']), 2)  # 2 Pawns
        self.assertEqual(
            len([x for x in p.record if x['piece_name'] == 'king']), 2)  # 2 Kings

        kings = [x for x in p.record if x['piece_name'] == 'king']
        self.assertNotEqual(kings[0], kings[1])  # 2 Different Kings

        white_king = [x for x in kings if x['allegiance'] == 'white']
        # White King in right position
        self.assertEqual(white_king[0]['pos_idx'], 53)

        self.assertEqual(p.active_allegiance, 'b')  # Black is first to move

        for king in kings:
            # Castling should not be available
            with self.assertRaises(KeyError):
                _ = king['queen_side_castle_allowed']
            with self.assertRaises(KeyError):
                _ = king['king_side_castle_allowed']

def flatten(list_):
    """Returns a flattened list"""
    return [item for sublist in list_ for item in sublist]

if __name__ == '__main__':
    unittest.main()
