"""This module implements the universal chess engine interface"""

import os
import re
from subprocess import Popen, PIPE
from configparser import ConfigParser
from fen import FENParser
import utils
from settings import ENGINE_CONFIGURATION_FILE, DEFAULT_ENGINE

class UCI():
    """Universal chess interafce"""

    def __init__(self, engine=DEFAULT_ENGINE, depth=2, params=None):
        self.engine_name = engine
        self.depth = str(depth)
        self.info = ""
        self.available_params = {}

        self.engine_path, self.engine_params = self._get_config(self.engine_name)
        self.engine = Popen(
            self.engine_path, universal_newlines=True, stdin=PIPE, stdout=PIPE)

        self._initialise()

        if params is not None:
            self.engine_params.update(params)

        self.set_params(self.engine_params)

    def get_param(self, param=None):
        """Return the specified parameter, default is return all the parameters"""
        if param is None:
            return self.engine_params
        try:
            return self.engine_params[param]
        except KeyError:
            raise UCIException('The parameter "%s" has not been set for engine: %s' %
                               (param, self.engine_name))

    def set_params(self, engine_params):
        """Use a dictionary of engine params to set the engine options"""
        for key, value in engine_params.items():
            self.set_param(key, value)

    def set_param(self, name, value):
        """Send the option to the engine and wait for ok back"""
        if name not in self.available_params:
            raise UCIException('Engine has not signified that "%s" is an availbale '
                               'parameter to be set. Available parameters are %s' %
                               (name, self.available_params.keys()))
        self._write('setoption name %s value %s' % (name, value))
        self._wait_for_ok()

    def set_position(self, fen=None, moves=None):
        """Send a board position to the gui"""
        if fen is None:
            fen = 'startpos'
        else:
            parser = FENParser(fen)
            if not parser.is_valid():
                raise UCIException('Invalid FEN string: %s' % fen)
            fen = 'fen %s' % fen
        if moves is not None:
            for move in moves:
                if not utils.is_long_algebraic(move):
                    raise UCIException('Invalid long algebraic move: %s' % move)
            moves = 'moves %s' % ' '.join(moves)
        else:
            moves = ''
        self._reset()
        self._write('position %s %s' % (fen, moves))

    def get_best_move(self):
        """Ask engine for best move"""
        self._write('go depth %s' % self.depth)
        while True:
            output = self._read()
            info = re.match(r'^info (.*)', output)
            match = re.match(r'^bestmove ([a-z0-9]*)', output)
            if info:
                self.info += info.group(1) + '\n'
            if match:
                return match.group(1)

    def _initialise(self):
        """Initialise the engine with uci and get setable options"""
        self._write("uci")
        while True:
            output = self._read()
            if output == 'uciok':
                return
            option = re.match(r'^option name (.*) (type.*)', output)
            if option:
                self.available_params[option.group(1)] = option.group(2)

    def _reset(self):
        """Reset between each position, go command"""
        self._write("ucinewgame")
        self._wait_for_ok()
        self.info = ""

    def _write(self, command):
        """Give the engine a uci command"""
        self.engine.stdin.write("%s\n" % command)
        self.engine.stdin.flush()

    def _read(self):
        """Return whatever is currently in the stdout pipe"""
        return self.engine.stdout.readline().strip()

    def _wait_for_ok(self):
        """Ping the engine and wait for the ok back"""
        self._write('isready')
        while True:
            if self._read() == 'readyok':
                return

    @staticmethod
    def _get_config(engine_name):
        """Retrieve the engine configuration from the yaml engine configuration file"""
        if os.path.isfile(ENGINE_CONFIGURATION_FILE):
            config = ConfigParser()
            config.optionxform = str
            config.read(ENGINE_CONFIGURATION_FILE)
        else:
            raise UCIException('Engine configuration file not found: %s' %
                               os.path.abspath(ENGINE_CONFIGURATION_FILE))
        try:
            config = config[engine_name]
        except KeyError:
            raise UCIException('Configuration for "%s" could not be found in %s' %
                               (engine_name, os.path.abspath(ENGINE_CONFIGURATION_FILE)))
        if 'path' in config:
            path = config['path']
        else:
            raise UCIException('Engine configuration for "%s" must contain a "path" '
                               'parameter pointing to the engine executable' % engine_name)
        del config['path']
        return path, dict(config)


class UCIException(BaseException):
    """Exception to catch uci errors"""

    def __init__(self, msg):
        super(UCIException, self).__init__()
        self.message = msg

    def __str__(self):
        return self.message
