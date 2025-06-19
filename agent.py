import random
import json
from pathlib import Path

class TicTacToeAgent:
    def __init__(self, symbol, q_value_file="agent_q_values.json", epsilon=0.1, learning_rate=0.1, discount_factor=0.9):
        self.symbol = symbol
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

        best_minimax_score = -float('inf')
        minimax_best_moves = []

        for move in available_moves:
            next_board = self.make_move(board, move, self.symbol)
            score = self.minimax_evaluate(next_board, self.opponent(self.symbol))
            if score > best_minimax_score:
                best_minimax_score = score
                minimax_best_moves = [move]
            elif score == best_minimax_score:
                minimax_best_moves.append(move)

        if best_minimax_score == 1:
            return random.choice(minimax_best_moves)
        elif best_minimax_score == -1 and not training_mode:
            pass

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
                    q_scores[move] = 0.0
                if q_scores[move] > max_q:
                    max_q = q_scores[move]
                    q_best_moves = [move]
                elif q_scores[move] == max_q:
                    q_best_moves.append(move)

            if max_q == 0.0 and best_minimax_score != 1:
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
            return 1
        elif winner_symbol == self.opponent(self.symbol):
            return -1
        elif " " not in board:
            return 0

        best_score_for_current_player = -float('inf') if current_player_turn == self.symbol else float('inf')

        for move in self.available_moves(board):
            next_board = self.make_move(board, move, current_player_turn)
            score = self.minimax_evaluate(next_board, self.opponent(current_player_turn))

            if current_player_turn == self.symbol:
                best_score_for_current_player = max(best_score_for_current_player, score)
            else:
                best_score_for_current_player = min(best_score_for_current_player, score)

        self.minimax_memo[state_str] = best_score_for_current_player
        return best_score_for_current_player

    def update_q_values(self, final_reward):
        for i in reversed(range(len(self.history))):
            state, action = self.history[i]

            if i == len(self.history) - 1:
                next_q_max = 0
            else:
                next_state_str, _ = self.history[i+1]
                if next_state_str in self.q_value and self.q_value[next_state_str]:
                    next_q_max = max(self.q_value[next_state_str].values())
                else:
                    next_q_max = 0

            target = final_reward + self.discount_factor * next_q_max
            if state not in self.q_value:
                self.q_value[state] = {}
            if action not in self.q_value[state]:
                self.q_value[state][action] = 0.0

            self.q_value[state][action] += self.learning_rate * (target - self.q_value[state][action])

        self.history = []

    def available_moves(self, board):
        return [i for i in range(9) if board[i] == " "]

    def make_move(self, board, index, player):
        new_board = list(board)
        new_board[index] = player
        return new_board

    def game_over(self, board):
        return self.winner(board) is not None or " " not in board

    def winner(self, board):
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6),
                (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
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

    # >>> This is where the indentation needs to be corrected <<<
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

    for i in range(n_games):
        board = [" "] * 9
        current_player_turn = "X"

        agent.history = []

        while True:
            available_moves = agent.available_moves(board)
            if not available_moves or agent.winner(board) is not None:
                break

            if current_player_turn == agent.symbol:
                move = agent.select_move(board, training_mode=True)
            else:
                if opponent_type == "random":
                    move = random.choice(available_moves)
                elif opponent_type == "minimax":
                    temp_opponent_agent = TicTacToeAgent(current_player_turn)
                    move = temp_opponent_agent.select_move(board, training_mode=False)
                else:
                    move = random.choice(available_moves)

            if move is None:
                break

            board = agent.make_move(board, move, current_player_turn)
            current_player_turn = agent.opponent(current_player_turn)

        final_result = agent.evaluate_result(board, agent.symbol)
        agent.update_q_values(final_result)

        if final_result == 1:
            win_count += 1
        elif final_result == 0:
            draw_count += 1
        else:
            loss_count += 1

        if (i + 1) % 10000 == 0:
            print(f"Game {i+1}/{n_games} - Wins: {win_count}, Draws: {draw_count}, Losses: {loss_count}")
            win_count = 0
            draw_count = 0
            loss_count = 0

    agent.save_q_values()
    print("Training complete and Q-values saved.")

if __name__ == "__main__":
    agent_x = TicTacToeAgent("X", q_value_file="agent_q_values_X.json", epsilon=0.3, learning_rate=0.2, discount_factor=0.95)
    train(agent_x, n_games=500000, opponent_type="random")
