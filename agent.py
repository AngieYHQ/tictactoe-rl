# import random
# import json
# from pathlib import Path

# class TicTacToeAgent:
#     def __init__(self, symbol, value_file="agent_values.json"):
#         self.symbol = symbol
#         self.value = {}
#         self.learning_rate = 0.1
#         self.history = []
#         self.value_file = Path(value_file)
#         self.load_values()

#     def select_move(self, board):
#         best_score = -float("inf")
#         best_moves = []
#         for move in self.available_moves(board):
#             next_board = self.make_move(board, move, self.symbol)
#             score = self.simulate(next_board, self.opponent(self.symbol))
#             if score > best_score:
#                 best_score = score
#                 best_moves = [move]
#             elif score == best_score:
#                 best_moves.append(move)
#         return random.choice(best_moves)  # Random among best moves

#     def simulate(self, board, current_player):
#         state = "".join(board)
#         if self.game_over(board):
#             result = self.evaluate_result(board, self.symbol)
#             self.value[state] = result
#             return result

#         if state in self.value:
#             return self.value[state]

#         scores = []
#         for move in self.available_moves(board):
#             next_board = self.make_move(board, move, current_player)
#             score = -self.simulate(next_board, self.opponent(current_player))
#             scores.append(score)

#         best_score = max(scores)
#         self.value[state] = best_score
#         return best_score

#     def save_values(self):
#         try:
#             with open(self.value_file, "w") as f:
#                 json.dump(self.value, f)
#         except Exception as e:
#             print("Error saving values:", e)

#     def load_values(self):
#         if self.value_file.exists():
#             try:
#                 with open(self.value_file, "r") as f:
#                     self.value = json.load(f)
#             except Exception as e:
#                 print("Error loading values:", e)

#     def available_moves(self, board):
#         return [i for i in range(9) if board[i] == " "]

#     def make_move(self, board, index, player):
#         new_board = board.copy()
#         new_board[index] = player
#         return new_board

#     def game_over(self, board):
#         return self.winner(board) is not None or " " not in board

#     def winner(self, board):
#         wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6),
#                 (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
#         for a, b, c in wins:
#             if board[a] == board[b] == board[c] and board[a] != " ":
#                 return board[a]
#         return None

#     def evaluate_result(self, board, player):
#         w = self.winner(board)
#         if w == player:
#             return 1
#         elif w is None:
#             return 0
#         else:
#             return -1

#     def opponent(self, player):
#         return "O" if player == "X" else "X"

# # Training function
# def train(agent, n_games=10000):
#     def play_game():
#         board = [" "] * 9
#         current_player = "X"
#         history = {"X": [], "O": []}

#         while True:
#             moves = [i for i, v in enumerate(board) if v == " "]
#             if not moves or agent.winner(board) is not None:
#                 break

#             if current_player == agent.symbol:
#                 move = agent.select_move(board)
#             else:
#                 move = random.choice(moves)  # opponent plays randomly

#             board = agent.make_move(board, move, current_player)
#             history[current_player].append("".join(board))

#             if agent.winner(board) or not any(v == " " for v in board):
#                 break
#             current_player = agent.opponent(current_player)

#         result = agent.evaluate_result(board, agent.symbol)
#         for state in history[agent.symbol]:
#             if state not in agent.value:
#                 agent.value[state] = result
#             else:
#                 agent.value[state] += agent.learning_rate * (result - agent.value[state])
#             result = -result

#     for _ in range(n_games):
#         play_game()

#     agent.save_values()


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
                    # Q-values are typically stored as {state_str: {action_idx: value}}
                    # JSON keys must be strings, so action_idx will be stringified
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
                # Convert action_idx (int) to string for JSON keys
                serializable_q_value = {
                    state_str: {str(action_idx): value for action_idx, value in actions_dict.items()}
                    for state_str, actions_dict in self.q_value.items()
                }
                json.dump(serializable_q_value, f)
        except Exception as e:
            print(f"Error saving Q-values: {e}")

    def select_move(self, board, training_mode=False):
        # When playing against the user, always exploit learned knowledge
        # During training, use epsilon-greedy for exploration
        current_state_str = "".join(board)
        available_moves = self.available_moves(board)

        if not available_moves:
            return None # No moves possible

        # Prioritize winning/losing moves immediately through minimax lookahead
        # This is the "Planning & Reasoning" part
        best_minimax_score = -float('inf')
        minimax_best_moves = []

        for move in available_moves:
            next_board = self.make_move(board, move, self.symbol)
            score = self.minimax_evaluate(next_board, self.opponent(self.symbol)) # Simulate opponent's turn
            if score > best_minimax_score:
                best_minimax_score = score
                minimax_best_moves = [move]
            elif score == best_minimax_score:
                minimax_best_moves.append(move)

        # If a guaranteed win or loss is found, prioritize it.
        # A score of 1 means winning, -1 means losing, 0 means draw
        if best_minimax_score == 1: # Agent can win in the next move
            return random.choice(minimax_best_moves)
        elif best_minimax_score == -1 and not training_mode: # Agent will lose if opponent plays optimally (during play, try to avoid this)
             # If AI is about to lose, it will pick the move that delays defeat or leads to a draw if possible
             # This is implicitly handled by picking the highest minimax score (even if it's -1, it's better than worse)
             pass # Continue to Q-learning logic, which might pick a better "worst" move

        # Reinforcement Learning (Q-learning based decision)
        if training_mode and random.uniform(0, 1) < self.epsilon:
            # Exploration: choose a random move
            chosen_move = random.choice(available_moves)
        else:
            # Exploitation: choose the move with the highest Q-value
            # If state not seen, initialize Q-values for available moves to 0
            if current_state_str not in self.q_value:
                self.q_value[current_state_str] = {move: 0 for move in available_moves}

            q_scores = self.q_value[current_state_str]
            max_q = -float('inf')
            q_best_moves = []

            for move in available_moves:
                if move not in q_scores: # Initialize Q-value for unseen action
                    q_scores[move] = 0.0
                if q_scores[move] > max_q:
                    max_q = q_scores[move]
                    q_best_moves = [move]
                elif q_scores[move] == max_q:
                    q_best_moves.append(move)

            # Combine Minimax and Q-learning for a robust strategy
            # If minimax indicates a clear win, take it. Otherwise, use Q-values.
            # If Q-values are all 0 (unexplored state), pick randomly or based on minimax's draw/lose avoidance.
            if max_q == 0.0 and best_minimax_score != 1: # If Q-values are uninitialized for this state, or for the draw/lose case
                 chosen_move = random.choice(minimax_best_moves) # Prefer moves that lead to best theoretical outcome
            else:
                 chosen_move = random.choice(q_best_moves) # Otherwise, rely on learned Q-values

        if training_mode:
            # Record the state and chosen action for learning after the game
            self.history.append((current_state_str, chosen_move))

        return chosen_move

    def minimax_evaluate(self, board, current_player_turn):
        state_str = "".join(board)
        if state_str in self.minimax_memo:
            return self.minimax_memo[state_str]

        # Base cases
        winner_symbol = self.winner(board)
        if winner_symbol == self.symbol: # AI wins
            return 1
        elif winner_symbol == self.opponent(self.symbol): # Opponent wins
            return -1
        elif " " not in board: # Draw
            return 0

        # Recursive case
        best_score_for_current_player = -float('inf') if current_player_turn == self.symbol else float('inf')

        for move in self.available_moves(board):
            next_board = self.make_move(board, move, current_player_turn)
            score = self.minimax_evaluate(next_board, self.opponent(current_player_turn))

            if current_player_turn == self.symbol:
                best_score_for_current_player = max(best_score_for_current_player, score)
            else: # Opponent's turn, they will try to minimize our score (maximize their own)
                best_score_for_current_player = min(best_score_for_current_player, score)

        self.minimax_memo[state_str] = best_score_for_current_player
        return best_score_for_current_player

    def update_q_values(self, final_reward):
        # Go through the history in reverse to update Q-values
        # This is a basic form of TD(0) update
        for i in reversed(range(len(self.history))):
            state, action = self.history[i]
            
            # The next state's maximum Q-value for future reward
            # If it's the last step, future_q_max is 0 (terminal state)
            if i == len(self.history) - 1:
                next_q_max = 0
            else:
                next_state_str, _ = self.history[i+1] # Get the next state from history
                if next_state_str in self.q_value and self.q_value[next_state_str]:
                    next_q_max = max(self.q_value[next_state_str].values())
                else:
                    next_q_max = 0 # No Q-values for next state yet

            # Q-learning formula: Q(s,a) = Q(s,a) + alpha * (reward + gamma * max(Q(s',a')) - Q(s,a))
            # The reward is the final reward received at the end of the game
            # This is simplified; typically, rewards are associated with transitions.
            # Here, we propagate the final reward back.
            
            # For simplicity, we use the final_reward here directly.
            # A more robust Q-learning would calculate immediate reward for each step,
            # but in Tic-Tac-Toe, reward is usually only at the end.
            
            # The state and action being updated are from the *agent's* perspective.
            # The `final_reward` should be from the agent's perspective.
            target = final_reward + self.discount_factor * next_q_max
            if state not in self.q_value:
                self.q_value[state] = {}
            if action not in self.q_value[state]:
                self.q_value[state][action] = 0.0
            
            self.q_value[state][action] += self.learning_rate * (target - self.q_value[state][action])
        
        self.history = [] # Clear history after updating

    # Helper functions (mostly copied from your original code)
    def available_moves(self, board):
        return [i for i in range(9) if board[i] == " "]

    def make_move(self, board, index, player):
        new_board = list(board) # Ensure it's a mutable list
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
        # This function should give reward from 'player's' perspective
        w = self.winner(board)
        if w == player:
            return 1 # Win for 'player'
        elif w is None:
            return 0 # Draw
        else:
            return -1 # Loss for 'player' (opponent wins)

    def opponent(self, player):
        return "O" if player == "X" else "X"

# --- Training Function ---
def train(agent, n_games=100000, opponent_type="random"): # Increased games for better learning
    print(f"Training agent for {n_games} games against a {opponent_type} opponent...")
    win_count = 0
    draw_count = 0
    loss_count = 0

    for i in range(n_games):
        board = [" "] * 9
        current_player_turn = "X" # Agent always starts as X in this training loop
        
        # Reset agent's history for the new game
        agent.history = [] 

        while True:
            available_moves = agent.available_moves(board)
            if not available_moves or agent.winner(board) is not None:
                break # Game over

            if current_player_turn == agent.symbol:
                # Agent makes a move using its select_move (which includes exploration during training)
                move = agent.select_move(board, training_mode=True)
            else:
                # Opponent's move
                if opponent_type == "random":
                    move = random.choice(available_moves)
                elif opponent_type == "minimax":
                    # For a tougher opponent, we can temporarily create another agent or use minimax directly
                    # Note: This makes training very slow as minimax is computed every time.
                    # A pre-trained minimax opponent is better if you want a truly smart one.
                    temp_opponent_agent = TicTacToeAgent(current_player_turn)
                    move = temp_opponent_agent.select_move(board, training_mode=False) # Opponent plays optimally
                else: # Default to random
                    move = random.choice(available_moves)

            if move is None: # Should not happen if available_moves is checked, but for safety
                break

            board = agent.make_move(board, move, current_player_turn)

            # Switch turns
            current_player_turn = agent.opponent(current_player_turn)

        # Game ended, now update Q-values
        final_result = agent.evaluate_result(board, agent.symbol) # Reward from agent's perspective
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
            loss_count = 0 # Reset for next batch

    agent.save_q_values()
    print("Training complete and Q-values saved.")


# --- How to use the agent for training and playing ---
if __name__ == "__main__":
    # Example of training
    # It's recommended to train first, then use the trained agent in your Streamlit app.
    
    # Train agent 'X' (our AI)
    agent_x = TicTacToeAgent("X", q_value_file="agent_q_values_X.json", epsilon=0.3, learning_rate=0.2, discount_factor=0.95)
    train(agent_x, n_games=500000, opponent_type="random") # Train against a random opponent
    # train(agent_x, n_games=10000, opponent_type="minimax") # Train against a minimax opponent (much slower)

    # You could also train an agent 'O' if you wanted to make the AI play against itself
    # agent_o = TicTacToeAgent("O", q_value_file="agent_q_values_O.json", epsilon=0.3, learning_rate=0.2, discount_factor=0.95)
    # train(agent_o, n_games=500000, opponent_type="random")

    # After training, you would use this saved `agent_q_values_X.json` in your Streamlit app.
    # In your app.py:
    # st.session_state.agent = TicTacToeAgent("X", q_value_file="agent_q_values_X.json", epsilon=0.0) # epsilon=0.0 means no exploration, always exploit
