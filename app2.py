import streamlit as st
import time
from agent import TicTacToeAgent

# Inject custom CSS for better responsiveness and centering
st.markdown("""
<style>
/* Center the main content */
.reportview-container .main {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 1rem; /* Adjust as needed */
}

/* Ensure columns within the board have some flex properties if needed */
.st-emotion-cache-nahz7x { /* This is a Streamlit class for columns, might change with versions */
    display: flex;
    justify-content: center; /* Center content within columns */
    align-items: center;
}

/* Specific styling for the game cells (buttons and markdown divs) */
.stButton>button, .tic-tac-toe-cell {
    width: 80px !important; /* Start with a larger fixed size */
    height: 80px !important;
    font-size: 40px !important; /* Adjust font size */
    line-height: 80px !important; /* Vertically center text */
    padding: 0 !important; /* Remove button padding */
    margin: 2px !important; /* Small margin between cells */
    display: flex; /* Use flexbox for centering content within cell */
    justify-content: center;
    align-items: center;
}

/* For smaller screens (e.g., iPhones in portrait) */
@media (max-width: 400px) { /* Adjust this breakpoint based on your testing */
    .stButton>button, .tic-tac-toe-cell {
        width: 60px !important; /* Reduce size for very small screens */
        height: 60px !important;
        font-size: 32px !important;
        line-height: 60px !important;
    }
}

/* Another breakpoint for even smaller phones */
@media (max-width: 320px) {
    .stButton>button, .tic-tac-toe-cell {
        width: 50px !important;
        height: 50px !important;
        font-size: 28px !important;
        line-height: 50px !important;
    }
}

/* Custom CSS to remove extra padding around the board itself if it's causing issues */
div[data-testid="stVerticalBlock"] div[data-testid="stHorizontalBlock"] {
    justify-content: center; /* Center the board itself if columns are centered */
}

</style>
""", unsafe_allow_html=True)


st.title("Tic Tac Toe with AI master 🤖")
st.markdown("""
You are <span style="color:blue;">**O**</span> and AI master is <span style="color:red;">**X**</span>.<br>
You always start first. Click once to place your O.<br>
AI will respond within 1 second.
""", unsafe_allow_html=True)

# Initialize session state for game statistics if not already present
if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    # Ensure TicTacToeAgent is defined or imported correctly
    st.session_state.agent = TicTacToeAgent("X", q_value_file="agent_q_values_X.json", epsilon=0.0)
    st.session_state.turn = "O"
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False

board = st.session_state.board
agent = st.session_state.agent

# Helper function to check if the game is over
def game_over(board):
    wins = [(0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)]
    for a, b, c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return True # There's a winner
    return " " not in board # It's a draw if no winner and no empty spaces

def play_move(pos):
    if board[pos] == " " and st.session_state.turn == "O" and not game_over(board):
        board[pos] = "O"
        if not game_over(board):
            st.session_state.turn = "X"
        st.rerun()

def winner(board):
    wins = [(0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)]
    for a, b, c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

def print_board(board):
    is_game_finished = game_over(board)

    # Use a container to center the entire board
    # This div will ensure the three columns stay grouped and centered
    st.markdown('<div class="tic-tac-toe-board-container">', unsafe_allow_html=True)
    for i in range(3):
        cols = st.columns(3, gap="small")
        for j in range(3):
            idx = 3*i + j
            with cols[j]:
                symbol = board[idx]
                if symbol == " ":
                    clicked = st.button(
                        " ",
                        key=f"btn_{idx}",
                        help=f"Click to place O",
                        disabled=is_game_finished
                    )
                    if clicked:
                        play_move(idx)
                else:
                    color = "#FF4B4B" if symbol == "X" else "#4B9CFF"
                    st.markdown(f"""
                        <div class="tic-tac-toe-cell" style="color: {color};">
                            {symbol}
                        </div>
                    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True) # Close the container div

print_board(board)

# AI's turn
if not game_over(board) and st.session_state.turn == "X":
    time.sleep(1)
    move = agent.select_move(board)
    if move is not None and board[move] == " ":
        board[move] = "X"
        if not game_over(board):
            st.session_state.turn = "O"
        st.rerun()
    else:
        st.error("AI could not make a valid move. This shouldn't happen.")
        st.session_state.turn = "O"


# --- Game Over Logic ---
if game_over(board):
    if st.session_state.get('game_outcome_recorded', False) == False:
        st.session_state.total_games += 1
        w = winner(board)
        if w == "O":
            st.session_state.user_wins += 1
        elif w == "X":
            st.session_state.ai_wins += 1
        else:
            st.session_state.draws += 1
        st.session_state.game_outcome_recorded = True

    w = winner(board)
    if w == "O":
        st.success("You win! 🎉")
    elif w == "X":
        st.error("AI Master wins! 😈")
    else:
        st.info("It's a draw! 🤝")

    if st.button("Play Again"):
        st.session_state.board = [" "] * 9
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
