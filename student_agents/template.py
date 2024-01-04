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

    def count_chess_pieces(self, board):
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

    def calculateScores(piece_counts, gs):
        material = 100 * (piece_counts['wP'] - piece_counts['bP']) + \
            320 * (piece_counts['wN'] - piece_counts['bN']) + \
            330 * (piece_counts['wB'] - piece_counts['bB']) + \
            900 * (piece_counts['wQ'] - piece_counts['bQ'])

        pawnsq = sum([pawntable[i]
                     for i in board.pieces(chess.PAWN, chess.WHITE)])


board = ['bN', 'bB', 'bQ', 'bK', 'bB', 'bN',
         'bp', 'bp', 'bp', 'bp', 'bp', 'bp',
         '--', '--', '--', '--', '--', '--',
         '--', '--', '--', '--', '--', '--',
         'wp', 'wp', 'wp', 'wp', 'wp', 'wp',
         'wN', 'wB', 'wQ', 'wK', 'wB', 'wN']

pawntable = [
        0, 0, 0, 0, 0, 0,
        5, 10, -20, -20, 10, 5,
        5, 10, 20, 20, 10, 5,
        0, 0, 10, 10, 0, 0,
        10, 20, 30, 30, 20, 10,
        50, 50, 50, 50, 50, 50
    ]

piece_values = Agent()

def calculate_piece_value(board, piece_name):

    piece_type = piece_name[1].lower()  # Extrahiere den Typ der Schachfigur ('n', 'b', usw.)
    piece_indices = [i for i, piece in enumerate(board) if piece == piece_name]

    piece_value = sum(piece_values.piece_tables[piece_type][i] for i in piece_indices)

    return piece_value

print(calculate_piece_value(board, 'bB'))

## teste calculate_piece_value und schaue ob es für beide seiten passt


## die funktion müsste theoretisch den index für die andere seite angeben
def square_mirror(index):
    row, col = divmod(index, 6)
    mirrored_index = col + (5 - row) * 6
    return mirrored_index