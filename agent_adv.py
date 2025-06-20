import random
import json
from pathlib import Path
import math # For math.prod in a potential future optimization, not strictly needed for this version

class TicTacToeAgent:
    def __init__(self, symbol, board_size=3, win_condition=3, q_value_file="agent_q_values.json", epsilon=0.1, learning_rate=0.1, discount_factor=0.9):
        self.symbol = symbol
        self.board_size = board_size
        self.win_condition = win_condition # Number of consecutive symbols needed to win
        self.q_value = {} # Stores Q(s, a) - value of taking action 'a' in state 's'
        self.epsilon = epsilon # For exploration during training
        self.learning_rate = learning_rate # Alpha
        self.discount_factor = discount_factor # Gamma
        self.q_value_file = Path(q_value_file)
        self.load_q_values()
        self.history = [] # To store (state, action) pairs during a game for learning

        # Memoization for minimax search (planning aspect)
        self.minimax_memo = {}

    def load_q_values(self):
        if self.q_value_file.exists():
            try:
                with open(self.q_value_file, "r") as f:
                    loaded_data = json.load(f)
                    self.q_value = {
                        state_str: {int(action_str): value for action_str, value in actions_dict.items()}
                        for state_str, actions_dict in loaded_data.items()
                    }
            except Exception as e:
                print(f"Error loading Q-values: {e}")
        else:
            print("No existing Q-value file found. Starting with an empty Q-table.")

    def save_q_values(self):
        try:
            with open(self.q_value_file, "w") as f:
                serializable_q_value = {
                    state_str: {str(action_idx): value for action_idx, value in actions_dict.items()}
                    for state_str, actions_dict in self.q_value.items()
                }
                json.dump(serializable_q_value, f)
        except Exception as e:
            print(f"Error saving Q-values: {e}")

    def select_move(self, board, training_mode=False):
        current_state_str = "".join(board)
        available_moves = self.available_moves(board)

        if not available_moves:
            return None

        # Minimax evaluation to guide Q-learning, especially early on
        best_minimax_score = -float('inf')
        minimax_best_moves = []

        for move in available_moves:
            next_board = self.make_move(board, move, self.symbol)
            score = self.minimax_evaluate(next_board, self.opponent(self.symbol)) # Minimax from opponent's perspective
            if score > best_minimax_score:
                best_minimax_score = score
                minimax_best_moves = [move]
            elif score == best_minimax_score:
                minimax_best_moves.append(move)

        # Prioritize immediate wins or blocking immediate losses if possible
        # This part of the logic might need tuning for larger boards.
        # For 3x3, a score of 1 means 'this move leads to my win'.
        # For larger boards, a score of 1 still means win, -1 means loss.
        if best_minimax_score == 1:
            # If a winning move exists, take it.
            chosen_move = random.choice(minimax_best_moves)
            if training_mode:
                self.history.append((current_state_str, chosen_move))
            return chosen_move
        elif best_minimax_score == -1 and not training_mode:
            # If the best move from minimax leads to a loss for the AI,
            # this means the opponent has a forced win. The agent will still
            # try to pick the 'least bad' move via Q-values or minimax_best_moves
            # if not training.
            pass # Continue to Q-value or epsilon-greedy choice

        # Epsilon-greedy exploration during training
        if training_mode and random.uniform(0, 1) < self.epsilon:
            chosen_move = random.choice(available_moves)
        else:
            if current_state_str not in self.q_value:
                self.q_value[current_state_str] = {move: 0 for move in available_moves}

            q_scores = self.q_value[current_state_str]
            max_q = -float('inf')
            q_best_moves = []

            for move in available_moves:
                if move not in q_scores:
                    q_scores[move] = 0.0 # Initialize Q-value for new state-action pair
                if q_scores[move] > max_q:
                    max_q = q_scores[move]
                    q_best_moves = [move]
                elif q_scores[move] == max_q:
                    q_best_moves.append(move)

            # Blending Q-values and Minimax:
            # If Q-values are all zero (i.e., unexplored states) and there's no immediate win,
            # fall back to a move suggested by Minimax to avoid purely random choices
            # in complex, unexplored scenarios.
            if max_q == 0.0 and best_minimax_score != 1: # If Q-values haven't been learned yet
                chosen_move = random.choice(minimax_best_moves)
            else:
                chosen_move = random.choice(q_best_moves)

        if training_mode:
            self.history.append((current_state_str, chosen_move))

        return chosen_move

    def minimax_evaluate(self, board, current_player_turn):
        state_str = "".join(board)
        if state_str in self.minimax_memo:
            return self.minimax_memo[state_str]

        winner_symbol = self.winner(board)
        if winner_symbol == self.symbol:
            return 1 # AI wins
        elif winner_symbol == self.opponent(self.symbol):
            return -1 # Opponent wins
        elif " " not in board: # Check for draw (full board)
            return 0

        best_score_for_current_player = -float('inf') if current_player_turn == self.symbol else float('inf')

        for move in self.available_moves(board):
            next_board = self.make_move(board, move, current_player_turn)
            score = self.minimax_evaluate(next_board, self.opponent(current_player_turn))

            if current_player_turn == self.symbol:
                best_score_for_current_player = max(best_score_for_current_player, score)
            else: # Opponent's turn (minimize opponent's score, so we maximize our negative score)
                best_score_for_current_player = min(best_score_for_current_player, score)

        self.minimax_memo[state_str] = best_score_for_current_player
        return best_score_for_current_player

    def update_q_values(self, final_reward):
        for i in reversed(range(len(self.history))):
            state, action = self.history[i]

            if i == len(self.history) - 1:
                # If this is the last state-action pair, there is no next state,
                # so the max Q-value of the next state is 0.
                next_q_max = 0
            else:
                next_state_str, _ = self.history[i+1]
                if next_state_str in self.q_value and self.q_value[next_state_str]:
                    # Get the maximum Q-value for the next state
                    next_q_max = max(self.q_value[next_state_str].values())
                else:
                    next_q_max = 0 # If next state is not in Q-table or has no actions, assume 0

            # Q-learning formula: Q(s,a) = Q(s,a) + alpha * [reward + gamma * max(Q(s',a')) - Q(s,a)]
            target = final_reward + self.discount_factor * next_q_max
            if state not in self.q_value:
                self.q_value[state] = {}
            if action not in self.q_value[state]:
                self.q_value[state][action] = 0.0

            self.q_value[state][action] += self.learning_rate * (target - self.q_value[state][action])

        self.history = [] # Clear history for the next game

    def available_moves(self, board):
        # Moves are indices from 0 to board_size*board_size - 1
        return [i for i in range(self.board_size * self.board_size) if board[i] == " "]

    def make_move(self, board, index, player):
        new_board = list(board)
        new_board[index] = player
        return new_board

    def game_over(self, board):
        return self.winner(board) is not None or " " not in board

    def winner(self, board):
        # Helper to convert 1D index to 2D (row, col)
        def get_coords(idx):
            return idx // self.board_size, idx % self.board_size

        # Check rows
        for r in range(self.board_size):
            for c in range(self.board_size - self.win_condition + 1):
                if all(board[r * self.board_size + c + i] == board[r * self.board_size + c] and board[r * self.board_size + c] != " " for i in range(self.win_condition)):
                    return board[r * self.board_size + c]

        # Check columns
        for c in range(self.board_size):
            for r in range(self.board_size - self.win_condition + 1):
                if all(board[(r + i) * self.board_size + c] == board[r * self.board_size + c] and board[r * self.board_size + c] != " " for i in range(self.win_condition)):
                    return board[r * self.board_size + c]

        # Check main diagonal (top-left to bottom-right)
        for r in range(self.board_size - self.win_condition + 1):
            for c in range(self.board_size - self.win_condition + 1):
                if all(board[(r + i) * self.board_size + (c + i)] == board[r * self.board_size + c] and board[r * self.board_size + c] != " " for i in range(self.win_condition)):
                    return board[r * self.board_size + c]

        # Check anti-diagonal (top-right to bottom-left)
        for r in range(self.board_size - self.win_condition + 1):
            for c in range(self.win_condition - 1, self.board_size): # Start from win_condition-1 column
                if all(board[(r + i) * self.board_size + (c - i)] == board[r * self.board_size + c] and board[r * self.board_size + c] != " " for i in range(self.win_condition)):
                    return board[r * self.board_size + c]
        return None

    def evaluate_result(self, board, player):
        w = self.winner(board)
        if w == player:
            return 1 # Player (AI) wins
        elif w is None:
            return 0 # Draw
        else:
            return -1 # Opponent wins (AI loses)

    def evaluate_result_for_opponent(self, board):
        # This function should give reward from opponent's perspective
        w = self.winner(board)
        opponent_symbol = self.opponent(self.symbol)
        if w == opponent_symbol:
            return 1 # Win for opponent
        elif w is None:
            return 0 # Draw
        else:
            return -1 # Loss for opponent (AI wins)

    def opponent(self, player):
        return "O" if player == "X" else "X"

# --- Training Function ---
def train(agent, n_games=100000, opponent_type="random"):
    print(f"Training agent for {n_games} games against a {opponent_type} opponent...")
    win_count = 0
    draw_count = 0
    loss_count = 0

    # For 5x5, Minimax opponent is extremely slow without significant pruning.
    # A random opponent is more practical for initial Q-learning.
    if opponent_type == "minimax" and agent.board_size > 3:
        print("WARNING: Minimax opponent for board size > 3 will be extremely slow.")
        print("Consider using 'random' opponent or a simplified minimax for training.")

    for i in range(n_games):
        # Board initialized based on board_size
        board = [" "] * (agent.board_size * agent.board_size)
        current_player_turn = "X"

        agent.history = []
        agent.minimax_memo = {} # Clear memoization for each new game

        while True:
            # Check for game end conditions before selecting a move
            if agent.winner(board) is not None or " " not in board:
                break # Game is over

            available_moves = agent.available_moves(board)
            if not available_moves: # Should be caught by " " not in board, but good to double check
                break

            if current_player_turn == agent.symbol:
                move = agent.select_move(board, training_mode=True)
            else:
                if opponent_type == "random":
                    move = random.choice(available_moves)
                elif opponent_type == "minimax":
                    # Create a temporary agent for the opponent's Minimax calculation
                    # Ensure it uses the correct board_size and win_condition
                    temp_opponent_agent = TicTacToeAgent(current_player_turn,
                                                         board_size=agent.board_size,
                                                         win_condition=agent.win_condition)
                    move = temp_opponent_agent.select_move(board, training_mode=False) # Opponent acts deterministically
                else:
                    # Fallback if opponent_type is unrecognized
                    move = random.choice(available_moves)

            if move is None:
                # This can happen if available_moves is empty right at the start of a loop iteration
                # and the previous checks didn't catch it, or if select_move logic fails.
                break

            board = agent.make_move(board, move, current_player_turn)
            current_player_turn = agent.opponent(current_player_turn)

        final_result = agent.evaluate_result(board, agent.symbol)
        agent.update_q_values(final_result)

        if final_result == 1:
            win_count += 1
        elif final_result == 0:
            draw_count += 1
        else: # final_result == -1
            loss_count += 1

        if (i + 1) % 10000 == 0:
            print(f"Game {i+1}/{n_games} - Wins: {win_count}, Draws: {draw_count}, Losses: {loss_count}")
            # Reset counts for the next block of games
            win_count = 0
            draw_count = 0
            loss_count = 0

    agent.save_q_values()
    print("Training complete and Q-values saved.")

if __name__ == "__main__":
    # Example for 3x3 Tic-Tac-Toe (original game)
    # agent_x = TicTacToeAgent("X", board_size=3, win_condition=3, q_value_file="agent_q_values_3x3_X.json", epsilon=0.3, learning_rate=0.2, discount_factor=0.95)
    # train(agent_x, n_games=500000, opponent_type="random") # Random opponent is good for initial Q-learning

    # Example for 5x5 Tic-Tac-Toe (4-in-a-row to win)
    # Note: Training a Q-learning agent for 5x5 is VERY computationally intensive
    # due to the massive state space and the Minimax evaluation within select_move.
    # You might need to reduce n_games for initial tests, or increase epsilon to favor exploration more.
    # Opponent type "random" is highly recommended for training 5x5.
    BOARD_SIZE = 5
    WIN_CONDITION = 4 # Common for 5x5, to make draws less frequent than 5-in-a-row
    AGENT_SYMBOL = "X"
    Q_VALUE_FILE = f"agent_q_values_{BOARD_SIZE}x{BOARD_SIZE}_{WIN_CONDITION}inrow_{AGENT_SYMBOL}.json"

    agent_x_5x5 = TicTacToeAgent(AGENT_SYMBOL, board_size=BOARD_SIZE, win_condition=WIN_CONDITION,
                                 q_value_file=Q_VALUE_FILE, epsilon=0.3, learning_rate=0.2, discount_factor=0.95)

    # For 5x5, start with a random opponent. Minimax opponent will be extremely slow.
    print(f"\n--- Starting training for {BOARD_SIZE}x{BOARD_SIZE} ({WIN_CONDITION}-in-a-row) ---")
    train(agent_x_5x5, n_games=100000, opponent_type="random") # Reduced games for testing 5x5
    # If you want to try training against minimax (be warned, it's slow for 5x5):
    # train(agent_x_5x5, n_games=1000, opponent_type="minimax")