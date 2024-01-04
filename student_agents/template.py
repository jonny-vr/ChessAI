import random

from ..ChessEngine import GameState


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
        self.color = None

        self.piece_tables = {
            'p': [
                0, 0, 0, 0, 0, 0,
                5, 10, -20, -20, 10, 5,
                5, 10, 20, 20, 10, 5,
                0, 0, 10, 10, 0, 0,
                10, 20, 30, 30, 20, 10,
                50, 50, 50, 50, 50, 50
            ],
            'n': [
                -50, -30, -30, -30, -30, -50,
                -30, 10, 15, 15, 10, -30,
                -30, 15, 30, 30, 15, -30,
                -30, 15, 30, 30, 15, -30,
                -30, 10, 15, 15, 10, -30,
                -50, -30, -30, -30, -30, -50
            ],
            'b': [
                -20, -10, -10, -10, -10, -20,
                -10, 10, 10, 10, 10, -10,
                -10, 10, 10, 10, 10, -10,
                -10, 5, 10, 10, 5, -10,
                -10, 5, 10, 10, 5, -10,
                -20, -10, -10, -10, -10, -20
            ],
            'q': [
                -20, -10, -5, -5, -10, -20,
                -10, 5, 5, 5, 5, -10,
                0, 5, 5, 5, 5, -5,
                -5, 5, 5, 5, 5, -5,
                -10, 5, 5, 5, 5, -10,
                -20, -10, -5, -5, -10, -20
            ],
            'k': [
                20, 10, 0, 0, 10, 20,
                -10, -20, -20, -20, -20, -10,
                -20, -30, -40, -40, -30, -20,
                -30, -40, -50, -50, -40, -30,
                -30, -40, -50, -50, -40, -30,
                -30, -40, -50, -50, -40, -30
            ]
        }

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
        # Now it's our turn
        self.turn = True
        # Set Color initially
        if self.color == None:
            if gs.whiteToMove == True:
                self.color = 'White'
            else:
                self.color = 'Black'

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
        # check for checkmate / stalemate / draw
        if gs.checkMate:
            if self.turn:
                return -9999
            else:
                return 9999

        if gs.staleMate:
            return 0
        if gs.draw:
            return 0

        # number of pieces
        piece_counts = self.count_chess_pieces(gs.board)

        # material and piece_scores
        scores = self.calculateScores(piece_counts, gs)

        # sum of all scores
        eval = scores['material'] + scores['pawn'] + scores['knight'] + \
            scores['bishop'] + scores['queen'] + scores['king']

        # favorable position for white = unfavorable position for black
        if gs.whiteToMove:
            return eval
        else:
            return -eval

    def count_chess_pieces(self, board):
        """
        Counts the number of each chess piece on the board.

        Args:
            board (list of str): List representing the current state of the chess board.

        Returns:
            dict: A dictionary containing counts for each chess piece, categorized by color and type.
                  Keys are strings representing piece names, and values are the respective counts.
        """
        piece_counts = {
            'wK': 0, 'wQ': 0, 'wB': 0, 'wN': 0, 'wp': 0,
            'bK': 0, 'bQ': 0, 'bB': 0, 'bN': 0, 'bp': 0,
        }
        for square in board:
            match square:
                case '--':
                    continue
                case 'wK':
                    piece_counts['wK'] += 1
                case 'wQ':
                    piece_counts['wQ'] += 1
                case 'wB':
                    piece_counts['wB'] += 1
                case 'wN':
                    piece_counts['wN'] += 1
                case 'wp':
                    piece_counts['wp'] += 1
                case 'bK':
                    piece_counts['bK'] += 1
                case 'bQ':
                    piece_counts['bQ'] += 1
                case 'bB':
                    piece_counts['bB'] += 1
                case 'bN':
                    piece_counts['bN'] += 1
                case 'bp':
                    piece_counts['bp'] += 1

        return piece_counts

    def calculateScores(self, piece_counts, gs):
        """
        Calculates scores based on the counts of chess pieces.

        Args:
            piece_counts (dict): A dictionary containing counts for each chess piece,
                                 categorized by color and type.
                                 Keys are strings representing piece names, and values are the respective counts.
            gs (GameState): The current state of the chess game.
        Returns:
            dict: A dictionary containing various scores, including material and individual piece scores.
                  Keys are strings representing score types, and values are the respective scores.
        """

        # material score
        material = 100 * (piece_counts['wP'] - piece_counts['bP']) + \
            320 * (piece_counts['wN'] - piece_counts['bN']) + \
            330 * (piece_counts['wB'] - piece_counts['bB']) + \
            900 * (piece_counts['wQ'] - piece_counts['bQ'])

        # individual pieces score
        pawn_score = self.calculate_piece_value(
            gs.board, 'wp') - self.calculate_piece_value(gs.board, 'bp')
        knight_score = self.calculate_piece_value(
            gs.board, 'wN') - self.calculate_piece_value(gs.board, 'bN')
        bishop_score = self.calculate_piece_value(
            gs.board, 'wB') - self.calculate_piece_value(gs.board, 'bB')
        queen_score = self.calculate_piece_value(
            gs.board, 'wQ') - self.calculate_piece_value(gs.board, 'bQ')
        king_score = self.calculate_piece_value(
            gs.board, 'wK') - self.calculate_piece_value(gs.board, 'bK')

        # Return a dictionary containing the scores
        scores = {
            'material': material,
            'pawn': pawn_score,
            'knight': knight_score,
            'bishop': bishop_score,
            'queen': queen_score,
            'king': king_score
        }

        return scores

    def square_mirror(self, index):
        """
        Mirrors the given index on a 6x6 chess board for calculating piece scores of white chess pieces.

        Args:
            index (int): The index of the chess piece in the gs.board array.

        Returns:
            int: The mirrored index of the chess piece, effectively switching from black to white or vice versa.
        """
        row, col = divmod(index, 6)
        mirrored_index = col + (5 - row) * 6
        return mirrored_index

    def calculate_piece_value(self, board, piece_name):
        """
        Sums up individual piece scores of a chess piece.

        Args:
            board (List of str): String Array representing Chess Board
            piece_name (str): Name of chess piece eg. 'bp', 'bB', ...

        Returns:
            int: Summed up score values for chess piece.
        """

        # extract type of chesspiece ('n', 'b', etc.)
        piece_type = piece_name[1].lower()
        piece_color = piece_name[0]
        if piece_color == 'b':
            piece_indices = [i for i, piece in enumerate(
                board) if piece == piece_name]
        else:
            piece_indices = [self.square_mirror(i) for i, piece in enumerate(
                board) if piece == piece_name]

        piece_value = sum(
            self.piece_tables[piece_type][i] for i in piece_indices)

        return piece_value


agent = Agent()

board = GameState()

eval = agent.evaluatePosition(board)

print(eval)
