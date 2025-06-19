import streamlit as st
import time
from agent import TicTacToeAgent

# Inject custom CSS for robust 3x3 grid on all screen sizes
st.markdown("""
<style>
/* 1. Global App Centering (optional but good for aesthetics) */
.stApp {
    display: flex;
    flex-direction: column;
    align-items: center; /* Center content horizontally */
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* 2. CRITICAL: Force Streamlit's column container to NEVER wrap */
/* This targets the div that wraps the entire row of st.columns for each board row. */
/* The data-testid can sometimes change with Streamlit versions, but this is common. */
div[data-testid="stVerticalBlock"] > div[data-testid="stHorizontalBlock"] {
    display: flex;
    flex-direction: row; /* Ensure they stay in a row */
    flex-wrap: nowrap !important; /* THIS IS THE KEY TO PREVENT STACKING */
    justify-content: center; /* Center the whole row of cells */
    align-items: center;
    width: 100%; /* Take full available width of its parent */
    max-width: 300px; /* Limit overall board width for very large screens */
    margin: 0 auto; /* Center the board block itself */
    gap: 0; /* Let cell margins handle spacing, not column gap */
    box-sizing: border-box; /* Include padding/border in total size calculation */
}

/* 3. Style for individual column containers */
/* These are the specific divs that hold each button/symbol (created by st.columns) */
div[data-testid^="stColumn"] { /* Targets divs whose testid starts with stColumn */
    flex-shrink: 0; /* Prevent columns from shrinking too much */
    flex-grow: 0;  /* Prevent columns from growing too much */
    flex-basis: calc(33.33% - 4px); /* Distribute space evenly, accounting for cell margins */
    max-width: calc(33.33% - 4px); /* Ensure max width doesn't exceed 1/3 */

    display: flex; /* Make column itself a flex container */
    justify-content: center; /* Center content within each column */
    align-items: center;
    padding: 0 !important; /* Remove any default padding from columns */
    box-sizing: border-box;
}

/* 4. Styling for the actual game cells (buttons and markdown divs) */
.stButton > button, .tic-tac-toe-cell {
    /* Use viewport width (vw) for highly responsive sizing */
    /* 30vw is roughly 1/3 of the viewport width. Adjust if too big/small. */
    width: 28vw !important; /* Example: 28% of viewport width */
    height: 28vw !important; /* Keep it square relative to width */

    /* Ensure minimum and maximum sizes for better control */
    min-width: 50px !important;
    min-height: 50px !important;
    max-width: 80px !important;
    max-height: 80px !important;

    font-size: 8vw !important; /* Scale font size with viewport */
    min-font-size: 28px !important;
    max-font-size: 40px !important;

    font-weight: bold;
    color: inherit; /* Inherit color from the Python 'style' attribute */
    text-align: center;
    line-height: 1; /* Reset line-height, flexbox handles vertical centering */
    padding: 0 !important;
    margin: 2px !important; /* Small margin between cells */
    border-radius: 5px;
    box-sizing: border-box;

    display: flex; /* Use flexbox to perfectly center X/O */
    justify-content: center;
    align-items: center;
    background-color: #f0f2f6; /* Streamlit's default button background */
    border: 1px solid #ccc; /* Uniform border for grid lines */
    cursor: pointer;
}

/* Ensure the filled cells also have the correct border and background */
.tic-tac-toe-cell {
    background-color: transparent; /* No background fill for symbol cells */
    user-select: none; /* Prevent text selection */
}

/* Specific color overrides for symbols (ensures !important works) */
.tic-tac-toe-cell[style*="color: rgb(255, 75, 75)"], /* Red for X (Streamlit's internal RGB) */
.tic-tac-toe-cell[style*="color: #FF4B4B"] { /* Red for X (direct hex) */
    color: #FF4B4B !important;
}

.tic-tac-toe-cell[style*="color: rgb(75, 156, 255)"], /* Blue for O (Streamlit's internal RGB) */
.tic-tac-toe-cell[style*="color: #4B9CFF"] { /* Blue for O (direct hex) */
    color: #4B9CFF !important;
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
    try:
        # Ensure TicTacToeAgent is defined or imported correctly
        st.session_state.agent = TicTacToeAgent("X", q_value_file="agent_q_values_X.json", epsilon=0.0)
    except FileNotFoundError:
        st.error("Error: 'agent_q_values_X.json' not found. Please ensure the AI Q-value file is in the same directory.")
        st.stop()
    except Exception as e:
        st.error(f"Error initializing AI agent: {e}. Make sure agent.py is correctly defined.")
        st.stop()

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

    for i in range(3):
        # Using st.columns(3, gap="small") as before.
        # The CSS above will ensure these columns stay in a row.
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

print_board(board) # Call this to display the board

# AI's turn
if not game_over(board) and st.session_state.turn == "X":
    time.sleep(1) # Reduced delay slightly for quicker testing, adjust as needed
    move = agent.select_move(board)
    if move is not None and board[move] == " ":
        board[move] = "X"
        if not game_over(board): # <--- CHECK GAME OVER AFTER AI MOVE
            st.session_state.turn = "O"
        st.rerun()
    else:
        st.error("AI could not make a valid move. This shouldn't happen.")
        st.session_state.turn = "O" # Pass turn back to user as fallback


# --- Game Over Logic (as previously discussed) ---
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
