import streamlit as st
import time
from agent import TicTacToeAgent

st.set_page_config(layout="centered") # Use centered layout for better presentation of larger board

st.title("Tic Tac Toe with AI master 🤖")
st.markdown("""
You are <span style="color:blue;">**O**</span> and AI master is <span style="color:red;">**X**</span>.<br>
You always start first. Click once to place your O.<br>
AI will respond within 1 second.
""", unsafe_allow_html=True)

# --- Game Configuration ---
# Define BOARD_SIZE and WIN_CONDITION for the 5x5 game
BOARD_SIZE = 5
WIN_CONDITION = 4 # 4-in-a-row for a 5x5 board is common and more dynamic
AGENT_SYMBOL = "X"
# The Q-value file name should match what the agent is configured to use for 5x5
AGENT_Q_VALUE_FILE = f"agent_q_values_{BOARD_SIZE}x{BOARD_SIZE}_{WIN_CONDITION}inrow_{AGENT_SYMBOL}.json"
# --------------------------

# Initialize session state for game statistics if not already present
if "board" not in st.session_state:
    # Initialize board for 5x5
    st.session_state.board = [" "] * (BOARD_SIZE * BOARD_SIZE)
    # Initialize TicTacToeAgent with the correct board_size and win_condition
    st.session_state.agent = TicTacToeAgent(
        AGENT_SYMBOL,
        board_size=BOARD_SIZE,
        win_condition=WIN_CONDITION,
        q_value_file=AGENT_Q_VALUE_FILE,
        epsilon=0.0 # Set epsilon to 0.0 for play mode (no exploration)
    )
    st.session_state.turn = "O"
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False # Add this flag if not already there

board = st.session_state.board
agent = st.session_state.agent # Reference to the agent from session state

# Helper function to play a user move
def play_move(pos):
    # Use the agent's game_over method
    if board[pos] == " " and st.session_state.turn == "O" and not agent.game_over(board):
        board[pos] = "O"
        # After user's move, check if game is over before changing turn or running AI
        if not agent.game_over(board): # Use agent's game_over
            st.session_state.turn = "X" # Pass turn to AI
        st.rerun()

# The game_over and winner functions previously in app.py are now handled by the agent.

def print_board(board):
    # Use the agent's game_over method
    is_game_finished = agent.game_over(board)

    # Dynamically create columns based on BOARD_SIZE
    for i in range(BOARD_SIZE):
        cols = st.columns(BOARD_SIZE, gap="small") # Create BOARD_SIZE columns
        for j in range(BOARD_SIZE):
            idx = i * BOARD_SIZE + j # Calculate 1D index for current cell
            with cols[j]:
                symbol = board[idx]
                if symbol == " ":
                    # Empty square - disable the button if the game is over
                    clicked = st.button(
                        " ",
                        key=f"btn_{idx}",
                        help=f"Click to place O",
                        disabled=is_game_finished # Disable if game is over
                    )
                    if clicked:
                        play_move(idx)
                else:
                    # Filled square
                    color = "#FF4B4B" if symbol == "X" else "#4B9CFF"
                    st.markdown(f"""
                        <div style="
                            width: 60px; /* Adjust button size as needed for visual appeal */
                            height: 60px;
                            font-size: 32px;
                            font-weight: bold;
                            color: {color};
                            text-align: center;
                            line-height: 60px;
                            user-select: none;
                            display: flex; /* Use flexbox for centering */
                            justify-content: center;
                            align-items: center;
                        ">
                            {symbol}
                        </div>
                    """, unsafe_allow_html=True)

# Display the board
print_board(board)

# AI's turn
# Ensure AI only moves if game is NOT over and it's its turn
if not agent.game_over(board) and st.session_state.turn == AGENT_SYMBOL:
    with st.spinner("AI thinking..."):
        time.sleep(1) # Delay for human readability
        move = agent.select_move(board)
    if move is not None and board[move] == " ": # Ensure the selected move is valid and empty
        board[move] = AGENT_SYMBOL
        # After AI's move, check if game is over before changing turn
        if not agent.game_over(board):
            st.session_state.turn = agent.opponent(AGENT_SYMBOL) # Switch turn back to human player
        st.rerun()
    else:
        st.error("AI could not make a valid move. This shouldn't happen under normal circumstances.")
        st.session_state.turn = agent.opponent(AGENT_SYMBOL) # Pass turn back to user as fallback


# --- Game Over Logic ---
# Use agent's game_over and winner functions for final checks
if agent.game_over(board):
    if st.session_state.get('game_outcome_recorded', False) == False:
        st.session_state.total_games += 1
        w = agent.winner(board) # Use agent's winner
        if w == agent.opponent(AGENT_SYMBOL): # Check if human player ('O') won
            st.session_state.user_wins += 1
        elif w == AGENT_SYMBOL: # Check if AI player ('X') won
            st.session_state.ai_wins += 1
        else: # It's a draw
            st.session_state.draws += 1
        st.session_state.game_outcome_recorded = True

    w = agent.winner(board) # Use agent's winner again for displaying the message
    if w == agent.opponent(AGENT_SYMBOL):
        st.success("You win! 🎉")
    elif w == AGENT_SYMBOL:
        st.error("AI Master wins! 😈")
    else:
        st.info("It's a draw! 🤝")

    if st.button("Play Again"):
        # Reset board based on BOARD_SIZE
        st.session_state.board = [" "] * (BOARD_SIZE * BOARD_SIZE)
        st.session_state.turn = agent.opponent(AGENT_SYMBOL) # User ('O') always starts
        st.session_state.game_outcome_recorded = False
        st.rerun()

# --- Display Statistics ---
st.markdown("---")
st.subheader("Game Statistics")

total = st.session_state.total_games
# Calculate percentages carefully to avoid division by zero
user_win_rate = (st.session_state.user_wins / total * 100) if total > 0 else 0
ai_win_rate = (st.session_state.ai_wins / total * 100) if total > 0 else 0
draw_rate = (st.session_state.draws / total * 100) if total > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Games Played", st.session_state.total_games)
with col2:
    st.metric("Your Wins (O)", f"{st.session_state.user_wins} ({user_win_rate:.1f}%)")
with col3:
    st.metric("AI Wins (X)", f"{st.session_state.ai_wins} ({ai_win_rate:.1f}%)")

st.metric("Draws", f"{st.session_state.draws} ({draw_rate:.1f}%)")

if st.button("Reset Statistics", help="Clear all win/loss/draw counts"):
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False
    st.rerun()
