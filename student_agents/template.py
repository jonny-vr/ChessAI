import random


class Agent:
    def __init__(self):
        self.move_queue = None
        self.nextMove = None
        self.counter = None
        self.currentDepth = None
        self.start = None
        self.timeout = None
        self.globalBestMove = None
        self.globalBestScore = None
        self.nextMoveScore = None
        self.is_turn = False

    pawntable = [
        0, 0, 0, 0, 0, 0,
        5, 10, -20, -20, 10, 5,
        5, 10, 20, 20, 10, 5,
        0, 0, 10, 10, 0, 0,
        10, 20, 30, 30, 20, 10, 50, 50, 50, 50, 50, 50]

    knightstable = [
        -50, -30, -30, -30, -30, -50,
        -30, 10, 15, 15, 10, -30,
        -30, 15, 30, 30, 15, -30,
        -30, 15, 30, 30, 15, -30,
        -30, 10, 15, 15, 10, -30,
        -50, -30, -30, -30, -30, -50]

    bishopstable = [
        -20, -10, -10, -10, -10, -20,
        -10, 10, 10, 10, 10, -10,
        -10, 10, 10, 10, 10, -10,
        -10, 5, 10, 10, 5, -10,
        -10, 5, 10, 10, 5, -10,
        -20, -10, -10, -10, -10, -20]

    queenstable = [
        -20, -10, -5, -5, -10,  -20,
        -10, 5, 5, 5, 5, -10,
        0, 5, 5, 5, 5, -5,
        -5, 5, 5, 5, 5, -5,
        -10, 5, 5, 5, 5, -10,
        -20, -10, -5, -5, -10,  -20]

    kingstable = [
        20, 10, 0, 0, 10, 20,
        -10, -20, -20, -20, -20,  -10,
        -20, -30, -40, -40, -30,  -20,
        -30, -40, -50, -50, -40,  -30,
        -30, -40, -50, -50, -40,  -30,
        -30, -40, -50, -50, -40,  -30]

    def get_move(self):
        move = None
        while not self.move_queue.empty():
            move = self.move_queue.get()
        return move

    def update_move(self, move, score, depth):
        """
        :param move: Object of class Move, like a list element of gamestate.getValidMoves()
        :param score: Integer; not really necessary, just for informative printing
        :param depth: Integer; not really necessary, just for informative printing
        :return:
        """
        self.move_queue.put([move, score, depth])

    def clear_queue(self, outer_queue):
        self.move_queue = outer_queue

    def findBestMove(self, gs):
        self.is_turn = True
        """
        Parameters
        ----------
        gs : Gamestate
            current state of the game
        Returns
        -------
        none

        """
        validMoves = gs.getValidMoves()
        pass

    def evaluatePosition(self, gs):
        """
        Parameters
        ----------
        gs: Gamestate
            current state of the game
        Returns
        -------
        Score: Integer

        """
        if gs.checkMate:
            if self.turn:
                return -9999
            else:
                return 9999

        if gs.staleMate:
            return 0
        if gs.draw:
            return 0
