import random

class TicTacToeAgent:
    def __init__(self, symbol):
        self.symbol = symbol
        self.value = {}
        self.learning_rate = 0.1
        self.history = []

    def select_move(self, board):
        best_score = -float("inf")
        best_move = None
        for move in self.available_moves(board):
            next_board = self.make_move(board, move, self.symbol)
            score = self.simulate(next_board, self.opponent(self.symbol))
            if score > best_score:
                best_score = score
                best_move = move
        return best_move

    def simulate(self, board, current_player):
        state = "".join(board)
        if self.game_over(board):
            result = self.evaluate_result(board, self.symbol)
            self.value[state] = result
            return result

        if state in self.value:
            return self.value[state]

        scores = []
        for move in self.available_moves(board):
            next_board = self.make_move(board, move, current_player)
            score = -self.simulate(next_board, self.opponent(current_player))
            scores.append(score)

        best_score = max(scores)
        self.value[state] = best_score
        return best_score

    def remember(self, board):
        self.history.append("".join(board))

    def learn(self, result):
        for state in reversed(self.history):
            if state not in self.value:
                self.value[state] = result
            else:
                self.value[state] += self.learning_rate * (result - self.value[state])
            result = -result
        self.history.clear()

    def available_moves(self, board):
        return [i for i in range(9) if board[i] == " "]

    def make_move(self, board, index, player):
        new_board = board.copy()
        new_board[index] = player
        return new_board

    def game_over(self, board):
        return self.winner(board) is not None or " " not in board

    def winner(self, board):
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in wins:
            if board[a] == board[b] == board[c] and board[a] != " ":
                return board[a]
        return None

    def evaluate_result(self, board, player):
        w = self.winner(board)
        if w == player:
            return 1
        elif w is None:
            return 0
        else:
            return -1

    def opponent(self, player):
        return "O" if player == "X" else "X"
        
