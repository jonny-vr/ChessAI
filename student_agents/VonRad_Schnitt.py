# from queue import Queue
# import sys
# sys.path.append(
#     '/Users/jonathanvonrad/Desktop/Artificial_Intelligence/Assignment08/Chess/')
# from ChessEngine import GameState

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
        self.color = None  # color of agent
        self.transpositionTable = {}  # hashtable containing
        self.piece_tables = {  # dictionary for each piece to evaluate position
            'p': [  # pawns need to go forward
                0, 0, 0, 0, 0, 0,
                5, 10, -20, -20, 10, 5,
                5, 10, 20, 20, 10, 5,
                0, 10, 20, 20, 10, 0,
                10, 20, 30, 30, 20, 10,
                50, 50, 50, 50, 50, 50
            ],
            'n': [  # knights are the most effective in center
                -20, -30, -30, -30, -30, -20,
                -30, 10, 15, 15, 10, -30,
                -30, 10, 30, 30, 10, -30,
                -30, 15, 30, 30, 15, -30,
                -30, 10, 15, 15, 10, -30,
                -50, -30, -30, -30, -30, -50
            ],
            'b': [  # bishops are more effective in center
                -20, -10, -10, -10, -10, -20,
                -10, 10, 10, 10, 10, -10,
                -10, 10, 10, 10, 10, -10,
                -10, 5, 10, 10, 5, -10,
                -10, 5, 10, 10, 5, -10,
                -20, -10, -10, -10, -10, -20
            ],
            'q': [  # queens are more effective in center (apart from check)
                -20, -10, -5, -5, -10, -20,
                -10, 5, 5, 5, 5, -10,
                0, 5, 5, 5, 5, -5,
                -5, 5, 5, 5, 5, -5,
                -10, 5, 5, 5, 5, -10,
                -20, -10, -5, -5, -10, -20
            ],
            'k': [  # king should be safe in opening/middlegame
                20, 10, 0, 0, 10, 20,
                -10, -20, -20, -20, -20, -10,
                -20, -30, -40, -40, -30, -20,
                -30, -40, -50, -50, -40, -30,
                -30, -40, -50, -50, -40, -30,
                -30, -40, -50, -50, -40, -30
            ],
            'k-endgame': [  # king should help pawns in endgame
                0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0,
                0, 10, 10, 10, 10, 0,
                0, 10, 10, 10, 10, 0,
                0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0
            ]
        }

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                    given functions
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

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

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                    move calculation
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------
#                              iterative deepening search
# ---------------------------------------------------------------------------------------------------------


    def findBestMove(self, gs):
        """
        Finds the best chess move for the current game state using an iterative deepening alpha-beta search.

        Parameters:
        - gs (GameState): The current state of the chess game.

        Returns:
        Move: The best move to be played according to the implemented search algorithm.
        """
        # initialize values
        self.color = 'White' if gs.whiteToMove else 'Black'
        validMoves = gs.getValidMoves()
        optimizedMoves = self.optimizeForCaptures(validMoves)
        bestMove = optimizedMoves[0]
        initial_queue = self.move_queue
        bestValue = -99999
        alpha = -100000
        beta = 100000
        depth = 1

        # start of iterative deepening search
        while True:
            for move in optimizedMoves:

                # start with bestMove after every iteration
                best_move_index = optimizedMoves.index(bestMove)
                optimizedMoves = [optimizedMoves[best_move_index]] + \
                    optimizedMoves[:best_move_index] + \
                    optimizedMoves[best_move_index + 1:]

                # make move and update gs.stalemate
                gs.makeMove(move)
                gs.getValidMoves()

                # we don't want draws
                if gs.staleMate or gs.draw or gs.threefold or self.threeSameMovesInRow(gs, move):
                    gs.undoMove()
                    continue

                # calculate
                boardValue = - \
                    self.alphabeta(gs, -beta, -alpha, depth - 1)

                # update values accordingly
                if boardValue > bestValue:
                    bestValue = boardValue
                    bestMove = move
                if boardValue > alpha:
                    alpha = boardValue

                # undo move
                gs.undoMove()

            # increase calculation depth and clear queue
            depth += 1
            self.clear_queue(initial_queue)
            self.update_move(bestMove,
                             self.evaluatePosition(gs), depth)

# ---------------------------------------------------------------------------------------------------------
#                              Negamax with alpha-beta pruning
# ---------------------------------------------------------------------------------------------------------

    def alphabeta(self, board, alpha, beta, depthleft):
        """
        Applies the alpha-beta pruning algorithm to search for the best move in a given chess position.

        Parameters:
        - board (ChessBoard): The current state of the chess board.
        - alpha (int): The lower bound of the score window.
        - beta (int): The upper bound of the score window.
        - depthleft (int): The remaining depth of the search tree.

        Returns:
        int: The best score for the current board position within the specified score window.
        """
        # Initialize the best score with a low value.
        bestscore = -9999

        # Perform a quiesce search when the recursion depth reaches zero.
        if (depthleft == 0):
            return self.quiesce(board, alpha, beta)

        # Optimize the order of moves, prioritizing captures.
        validMoves = board.getValidMoves()
        optimizedMoves = self.optimizeForCaptures(validMoves)

        for move in optimizedMoves:
            # make move and update board.stalemate
            board.makeMove(move)
            board.getValidMoves()

            # We don't want draws
            if board.staleMate or board.draw or board.threefold:
                board.undoMove()
                continue

            # calculating score using negamax approach (negating value)
            score = -self.alphabeta(board, -beta, -alpha, depthleft - 1)

            # undo move
            board.undoMove()

            # prune, if possible
            if (score >= beta):
                return score
            if (score > bestscore):
                bestscore = score
            if (score > alpha):
                alpha = score

        return bestscore


# ---------------------------------------------------------------------------------------------------------
#                              Quiescence Search
# ---------------------------------------------------------------------------------------------------------

    def quiesce(self, board, alpha, beta):
        """
        Applies quiescence search to evaluate the chess board position within a narrow score window.

        Parameters:
        - board (ChessBoard): The current state of the chess board.
        - alpha (int): The lower bound of the score window.
        - beta (int): The upper bound of the score window.

        Returns:
        int: The evaluated score of the current board position within the specified score window.
        """
        # Evaluate the current board position.
        stand_pat = self.evaluatePosition(board)

        # prune, if possible
        if (stand_pat >= beta):
            return beta

        # update alpha
        if (alpha < stand_pat):
            alpha = stand_pat

        # Optimize the order of moves, prioritizing captures.
        validMoves = board.getValidMoves()
        optimizedMoves = self.optimizeForCaptures(validMoves)

        for move in optimizedMoves:
            # Recursive call for captures with negamax approach. (negating score)
            if move.isCapture:
                board.makeMove(move)
                score = -self.quiesce(board, -beta, -alpha)
                board.undoMove()

                # prune, if possible
                if (score >= beta):
                    return beta

                # update alpha
                if (score > alpha):
                    alpha = score

        # Return the final alpha score after considering all capturing moves.
        return alpha

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                    position evaluation
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------


# ---------------------------------------------------------------------------------------------------------
#                                     Final evaluation
# ---------------------------------------------------------------------------------------------------------


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
        board_hash = self.customHash(gs)
        if board_hash in self.transpositionTable:
            return self.transpositionTable[board_hash]
        # check for checkmate / stalemate / draw
        myTurn = gs.whiteToMove and self.color == 'White' or not gs.whiteToMove and self.color == 'Black'

        if gs.checkMate:
            if myTurn:
                return -9999
            else:
                return 9999

        if gs.staleMate:
            return 0
        if gs.draw:
            return 0

        # number of pieces
        piece_counts = self.countPieces(gs.board)

        # material and piece_scores
        scores = self.calculateScores(piece_counts, gs)

        # sum of all scores
        eval = scores['material'] + scores['pawn'] + scores['knight'] + \
            scores['bishop'] + scores['queen'] + scores['king']

        # favorable position for white = unfavorable position for black
        if gs.whiteToMove:
            self.transpositionTable[board_hash] = eval
            return eval
        else:
            self.transpositionTable[board_hash] = -eval
            return -eval

# ---------------------------------------------------------------------------------------------------------
#                                     count pieces
# ---------------------------------------------------------------------------------------------------------

    def countPieces(self, board):
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

# ---------------------------------------------------------------------------------------------------------
#                              score calculation (material + individual pieces)
# ---------------------------------------------------------------------------------------------------------

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
        pawn_value = 100 if not self.isEndgame(gs) else 200

        material = 100 * (piece_counts['wp'] - piece_counts['bp']) + \
            320 * (piece_counts['wN'] - piece_counts['bN']) + \
            330 * (piece_counts['wB'] - piece_counts['bB']) + \
            900 * (piece_counts['wQ'] - piece_counts['bQ'])

        # individual pieces score
        pawn_score = self.calculatePieceValue(
            gs, 'wp') - self.calculatePieceValue(gs, 'bp')
        knight_score = self.calculatePieceValue(
            gs, 'wN') - self.calculatePieceValue(gs, 'bN')
        bishop_score = self.calculatePieceValue(
            gs, 'wB') - self.calculatePieceValue(gs, 'bB')
        queen_score = self.calculatePieceValue(
            gs, 'wQ') - self.calculatePieceValue(gs, 'bQ')
        king_score = self.calculatePieceValue(
            gs, 'wK') - self.calculatePieceValue(gs, 'bK')

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

# ---------------------------------------------------------------------------------------------------------
#                                    piece scores
# ---------------------------------------------------------------------------------------------------------

    def calculatePieceValue(self, gs, piece_name):
        """
        Sums up individual piece scores of a chess piece.

        Args:
            gs (GameState()): State of Game
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
            piece_indices = [self.squareMirror(i) for i, piece in enumerate(
                gs.board) if piece == piece_name]

        # könig im endgame hat andere tabelle!
        if self.isEndgame(gs) and piece_type == 'k':
            piece_value = sum(
                self.piece_tables['k-endgame'][i] for i in piece_indices)
        else:
            piece_value = sum(
                self.piece_tables[piece_type][i] for i in piece_indices)

        return piece_value

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                    Helpers
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    # determines if endgame (approximation 15 or less pieces) --> used in calculatePieceValue()
    def isEndgame(self, gs):
        """
        Determines whether the current chess game state is in the endgame phase.

        Parameters:
        - gs (ChessGameState): The current state of the chess game.

        Returns:
        bool: True if the game is in the endgame phase (when the total number of pieces on the board is less than 15),
              False otherwise.
        """
        piece_counts = self.countPieces(gs.board)
        if sum(piece_counts.values()) < 15:
            return True
        else:
            return False

    # mirros index for piece score --> used in calculatePieceValue()
    def squareMirror(self, index):
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

    def customHash(self, board):
        """
        Generates a custom hash value for the given chess board state.

        Parameters:
        - board (ChessBoard): The chess board object representing the current state.

        Returns:
        str: A custom hash value based on the concatenated string representation of the board
             and the indicator of which player (white or black) is to move next.
        """
        board_str = ''.join(board.board)
        final_hash = board_str + "#" + str(board.whiteToMove)
        return final_hash

    # heuristic for sorting validMoves to improve prunign --> used in findBestMove()/alphabeta()/quiesce()
    def optimizeForCaptures(self, validMoves):
        """
        Optimizes a list of chess moves by separating capture moves from non-capture moves.

        Parameters:
        - validMoves (list): A list of chess moves.

        Returns:
        list: A new list of moves with capture moves placed before non-capture moves.
        """
        capture_moves = [move for move in validMoves if move.isCapture]
        other_moves = [
            move for move in validMoves if move not in capture_moves]
        return capture_moves + other_moves

    def threeSameMovesInRow(self, gs, move):
        if len(gs.moveLog) > 4:
            last_own_move = gs.moveLog[-2].getChessNotation()
            second_last_own_move = gs.moveLog[-4].getChessNotation()
            return move.getChessNotation() == last_own_move == second_last_own_move
        else:
            return False

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                    debugging
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

# agent = Agent()

# state = GameState()

# state.board = ['--', 'bB', 'bQ', 'bK', 'bB', 'bN',
#                'bp', 'bp', 'bN', '--', 'bp', 'bp',
#                '--', '--', '--', '--', '--', '--',
#                'wp', '--', 'bp', 'wB', '--', '--',
#                '--', 'wp', 'wN', '--', 'wp', 'wp',
#                '--', '--', 'wQ', 'wK', 'wB', 'wN']


# agent.findBestMove(state)
