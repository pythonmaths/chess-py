"""Base Piece class"""

import utils
from settings import LEFT_EDGE, RIGHT_EDGE

class Piece():
    """Class for a generic piece"""

    def __init__(self):
        self.allegiance = None
        self.pos_idx = None

        self.promoted_piece = False
        self.move_cnt = 0
        self.legal_moves = []
        self.allies_in_legal_moves = []
        self.illegal_enemy_king_moves = []

    def get_overview(self):
        """Return a string describing this piece"""
        dict_ = {'Name': str(self),
                 'Position': utils.idx_to_algebra(self.pos_idx),
                 'Allegiance': self.allegiance}
        return str(dict_)

    def get_direction(self):
        """Return the direction of play for this piece. 1 is down the board
           -1 is up the board"""
        return 1 if self.allegiance == 'black' else -1

    def get_rank(self):
        """Get the rank of the current piece"""
        alg = utils.idx_to_algebra(self.pos_idx)
        return alg[1]

    def get_file(self):
        """Get the file of the current piece"""
        alg = utils.idx_to_algebra(self.pos_idx)
        return alg[0]

    def is_on_rank(self, rank):
        """Return True if the piece is on the given rank"""
        return int(rank) == int(self.get_rank())

    def is_on_file(self, file):
        """Return True if the piece is on the given file"""
        return str(file) == str(self.get_file())

    def _clear_moves(self):
        """Empty move lists"""
        self.legal_moves = []
        self.allies_in_legal_moves = []
        self.illegal_enemy_king_moves = []

    def fwd(self, *args, pos_idx=False):
        """Return idx for forward moves"""
        direction = self.get_direction()
        indexes = []
        if not args:
            args = range(1, 8)
        for arg in args:
            idx = self.pos_idx + (8*arg*direction)
            if idx in range(64):
                indexes.append(idx)
        if pos_idx:
            return indexes
        algs = utils.idx_to_algebra(*indexes)
        return algs if isinstance(algs, list) else [algs]

    def bkwd(self, *args, pos_idx=False):
        """Return idx for backward moves"""
        direction = self.get_direction()
        indexes = []
        if not args:
            args = range(1, 8)
        for arg in args:
            idx = self.pos_idx - (8*arg*direction)
            if idx in range(64):
                indexes.append(idx)
        if pos_idx:
            return indexes
        algs = utils.idx_to_algebra(*indexes)
        return algs if isinstance(algs, list) else [algs]

    def left(self, *args, pos_idx=False):
        """Return idx for left moves"""
        direction = self.get_direction()
        indexes = []
        if not args:
            args = range(1, 8)
        for arg in args:
            idx = self.pos_idx + (arg*direction)
            if idx // 8 == self.pos_idx // 8:
                indexes.append(idx)
        if pos_idx:
            return indexes
        algs = utils.idx_to_algebra(*indexes)
        return algs if isinstance(algs, list) else [algs]

    def right(self, *args, pos_idx=False):
        """Return idx for right moves"""
        direction = self.get_direction()
        indexes = []
        if not args:
            args = range(1, 8)
        for arg in args:
            idx = self.pos_idx - (arg*direction)
            if idx // 8 == self.pos_idx // 8:
                indexes.append(idx)
        if pos_idx:
            return indexes
        algs = utils.idx_to_algebra(*indexes)
        return algs if isinstance(algs, list) else [algs]

    def dgfl(self, *args, pos_idx=False):
        """Return idx for forward diagonal left moves"""
        direction = self.get_direction()
        indexes = []
        if not args:
            args = range(1, 8)
        if self.pos_idx not in LEFT_EDGE[direction]:
            for arg in args:
                idx = self.pos_idx + (8*arg*direction + 1*arg*direction)
                if idx in range(64):
                    indexes.append(idx)
                if idx in LEFT_EDGE[direction]:
                    break
        if pos_idx:
            return indexes
        algs = utils.idx_to_algebra(*indexes)
        return algs if isinstance(algs, list) else [algs]

    def dgfr(self, *args, pos_idx=False):
        """Return idx for forward diagonal right moves"""
        direction = self.get_direction()
        indexes = []
        if not args:
            args = range(1, 8)
        if self.pos_idx not in RIGHT_EDGE[direction]:
            for arg in args:
                idx = self.pos_idx + (8*arg*direction + -1*arg*direction)
                if idx in range(64):
                    indexes.append(idx)
                if idx in RIGHT_EDGE[direction]:
                    break
        if pos_idx:
            return indexes
        algs = utils.idx_to_algebra(*indexes)
        return algs if isinstance(algs, list) else [algs]

    def dgbl(self, *args, pos_idx=False):
        """Return idx for backward diagonal left moves"""
        direction = self.get_direction()
        indexes = []
        if not args:
            args = range(1, 8)
        if self.pos_idx not in LEFT_EDGE[direction]:
            for arg in args:
                idx = self.pos_idx - (8*arg*direction + -1*arg*direction)
                if idx in range(64):
                    indexes.append(idx)
                if idx in LEFT_EDGE[direction]:
                    break
        if pos_idx:
            return indexes
        algs = utils.idx_to_algebra(*indexes)
        return algs if isinstance(algs, list) else [algs]

    def dgbr(self, *args, pos_idx=False):
        """Return idx for backward diagonal right moves"""
        direction = self.get_direction()
        indexes = []
        if not args:
            args = range(1, 8)
        if self.pos_idx not in RIGHT_EDGE[direction]:
            for arg in args:
                idx = self.pos_idx - (8*arg*direction + 1*arg*direction)
                if idx in range(64):
                    indexes.append(idx)
                if idx in RIGHT_EDGE[direction]:
                    break
        if pos_idx:
            return indexes
        algs = utils.idx_to_algebra(*indexes)
        return algs if isinstance(algs, list) else [algs]
