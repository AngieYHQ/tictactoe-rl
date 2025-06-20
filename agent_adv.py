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
BOARD_SIZE = 5
WIN_CONDITION = 4 # 4-in-a-row for a 5x5 board is common and more dynamic
AGENT_Q_VALUE_FILE = f"agent_q_values_{BOARD_SIZE}x{BOARD_SIZE}_{WIN_CONDITION}inrow_X.json"
# --------------------------

# Initialize session state for game statistics if not already present
if "board" not in st.session_state:
    st.session_state.board = [" "] * (BOARD_SIZE * BOARD_SIZE) # Initialize 5x5 board
    # Initialize agent with correct board_size and win_condition
    st.session_state.agent = TicTacToeAgent(
        "X",
        board_size=BOARD_SIZE,
        win_condition=WIN_CONDITION,
        q_value_file=AGENT_Q_VALUE_FILE,
        epsilon=0.0 # Agent should be deterministic in play mode
    )
    st.session_state.turn = "O"
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False

board = st.session_state.board
agent = st.session_state.agent # Reference to the agent from session state

# Helper function to play a user move
def play_move(pos):
    # Use agent's game_over check
    if board[pos] == " " and st.session_state.turn == "O" and not agent.game_over(board):
        board[pos] = "O"
        # After user's move, check if game is over before changing turn or running AI
        if not agent.game_over(board):
            st.session_state.turn = "X" # Pass turn to AI
        st.rerun()

def print_board(board):
    # Use agent's game_over check
    is_game_finished = agent.game_over(board)

    # Create BOARD_SIZE x BOARD_SIZE grid
    for i in range(BOARD_SIZE):
        cols = st.columns(BOARD_SIZE, gap="small") # Create BOARD_SIZE columns
        for j in range(BOARD_SIZE):
            idx = i * BOARD_SIZE + j # Calculate 1D index
            with cols[j]:
                symbol = board[idx]
                if symbol == " ":
                    # Empty square - disable button if game is over
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
                            width: 60px; /* Adjust button size as needed */
                            height: 60px;
                            font-size: 32px;
                            font-weight: bold;
                            color: {color};
                            text-align: center;
                            line-height: 60px;
                            user-select: none;
                        ">
                            {symbol}
                        </div>
                    """, unsafe_allow_html=True)

# Display the board
print_board(board)

# AI's turn
# Ensure AI only moves if game is NOT over and it's its turn
if not agent.game_over(board) and st.session_state.turn == "X":
    with st.spinner("AI thinking..."):
        time.sleep(1) # Reduced delay slightly for quicker testing, adjust as needed
        move = agent.select_move(board)
    if move is not None and board[move] == " ":
        board[move] = "X"
        if not agent.game_over(board):
            st.session_state.turn = "O"
        st.rerun()
    else:
        st.error("AI could not make a valid move. This shouldn't happen.")
        st.session_state.turn = "O" # Pass turn back to user as fallback


# --- Game Over Logic ---
# Use agent's game_over and winner functions
if agent.game_over(board):
    if st.session_state.get('game_outcome_recorded', False) == False:
        st.session_state.total_games += 1
        w = agent.winner(board) # Use agent's winner
        if w == "O":
            st.session_state.user_wins += 1
        elif w == "X":
            st.session_state.ai_wins += 1
        else:
            st.session_state.draws += 1
        st.session_state.game_outcome_recorded = True

    w = agent.winner(board) # Use agent's winner again for display
    if w == "O":
        st.success("You win! 🎉")
    elif w == "X":
        st.error("AI Master wins! 😈")
    else:
        st.info("It's a draw! 🤝")

    if st.button("Play Again"):
        st.session_state.board = [" "] * (BOARD_SIZE * BOARD_SIZE) # Reset board to 5x5
        st.session_state.turn = "O"
        st.session_state.game_outcome_recorded = False
        st.rerun()

# --- Display Statistics ---
st.markdown("---")
st.subheader("Game Statistics")

total = st.session_state.total_games
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
