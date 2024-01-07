import random


class Agent:
    def __init__(self):
        self.move_queue = None

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
        """
        Parameters
        ----------
        gs : Gamestate
            current state of the game
        Returns
        -------
        none

        """
        # TODO

    def isEndgame(self, gs):
        piece_counts = self.count_chess_pieces(gs.board)
        if sum(piece_counts.values()) < 15:
            return True
        else:
            return False

    def calculate_piece_value(self, gs, piece_name):
        """
        Sums up individual piece scores of a chess piece.

        Args:
            gs (GameState()): state of Game
            piece_name (str): Name of chess piece eg. 'bp', 'bB', ...

        Returns:
            int: Summed up score values for chess piece.
        """

        # extract type of chesspiece ('n', 'b', etc.)
        piece_type = piece_name[1].lower()
        piece_color = piece_name[0]

        if piece_color == 'b':
            piece_indices = [i for i, piece in enumerate(
                gs.board) if piece == piece_name]
        else:
            piece_indices = [self.square_mirror(i) for i, piece in enumerate(
                gs.board) if piece == piece_name]

        # könig im endgame hat andere tabelle!
        if self.isEndgame(gs) and piece_type == 'k':
            piece_value = sum(
                self.piece_tables['k-endgame'][i] for i in piece_indices)
        else:
            piece_value = sum(
                self.piece_tables[piece_type][i] for i in piece_indices)

        return piece_value
