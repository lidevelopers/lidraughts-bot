"""
Some example strategies for people who want to create a custom, homemade bot.
And some handy classes to extend
"""

import random
from engine_wrapper import EngineWrapper
import draughts


class FillerEngine:
    """
    Not meant to be an actual engine.

    This is only used to provide the property "self.engine"
    in "MinimalEngine" which extends "EngineWrapper"
    """
    def __init__(self, main_engine, name=None):
        self.id = {
            "name": name
        }
        self.name = name
        self.main_engine = main_engine

    def __getattr__(self, method_name):
        main_engine = self.main_engine

        def method(*args, **kwargs):
            nonlocal main_engine
            nonlocal method_name
            return main_engine.notify(method_name, *args, **kwargs)

        return method


class MinimalEngine(EngineWrapper):
    """
    Subclass this to prevent a few random errors

    Even though MinimalEngine extends EngineWrapper,
    you don't have to actually wrap an engine.

    At minimum, just implement `search`,
    however you can also change other methods like
    `notify`, `first_search`, `get_time_control`, etc.
    """
    def __init__(self, *args, name=None):
        super().__init__(*args)

        self.engine_name = self.__class__.__name__ if name is None else name

        self.last_move_info = []
        self.engine = FillerEngine(self, name=self.name)
        self.engine.id = {
            "name": self.engine_name
        }

    def search_with_ponder(self, board, wtime, btime, winc, binc, ponder):
        timeleft = 0
        if board.whose_turn() == draughts.WHITE:
            timeleft = wtime
        else:
            timeleft = btime
        return self.search(board, timeleft, ponder)

    def search(self, board, timeleft, ponder):
        raise NotImplementedError("The search method is not implemented")

    def notify(self, method_name, *args, **kwargs):
        """
        The EngineWrapper class sometimes calls methods on "self.engine".
        "self.engine" is a filler property that notifies <self> 
        whenever an attribute is called.

        Nothing happens unless the main engine does something.

        Simply put, the following code is equivalent
        self.engine.<method_name>(<*args>, <**kwargs>)
        self.notify(<method_name>, <*args>, <**kwargs>)
        """
        pass


class ExampleEngine(MinimalEngine):
    pass


# Strategy names and ideas from tom7's excellent eloWorld video

class RandomMove(ExampleEngine):
    def search(self, board, *args):
        move = random.choice(board.legal_moves()[0])
        return board.board_to_li_api(move), None


class FirstMoveLidraughts(ExampleEngine):
    """Gets the first move when sorted by lidraughts representation (e.g. 011223)"""
    def search(self, board, *args):
        moves = board.legal_moves()[0]
        moves = list(map(board.board_to_li_api, moves))
        moves.sort()
        return moves[0], None


class FirstMoveHub(ExampleEngine):
    """Gets the first move when sorted by hub representation (e.g. 01x23x7x18)"""
    def search(self, board, *args):
        moves = board.legal_moves()[0]
        hub_moves = list(map(board.board_to_hub, moves))
        hub_to_moves = {}
        for hub_move, li_move in zip(hub_moves, moves):
            hub_to_moves[hub_move] = li_move
        hub_moves.sort()
        return hub_to_moves[hub_moves[0]], None


class FirstMovePDN(ExampleEngine):
    """Gets the first move when sorted by PDN representation (e.g. 01x23)"""
    def search(self, board, *args):
        moves = board.legal_moves()[0]
        pdn_moves = list(map(board.board_to_pdn, moves))
        pdn_to_moves = {}
        for pdn_move, li_move in zip(pdn_moves, moves):
            pdn_to_moves[pdn_move] = li_move
        pdn_moves.sort()
        return pdn_to_moves[pdn_moves[0]], None
