import streamlit as st
import time
from agent import TicTacToeAgent

# Inject custom CSS for a robust 3x3 grid using CSS Grid
st.markdown("""
<style>
/* 1. Global App Centering */
.stApp {
    display: flex;
    flex-direction: column;
    align-items: center; /* Center content horizontally */
    padding-top: 1rem;
    padding-bottom: 1rem;
}

/* 2. Style for the Tic-Tac-Toe board container using CSS Grid */
.tic-tac-toe-grid-container {
    display: grid;
    /* Define 3 columns, each taking an equal fraction of available space */
    grid-template-columns: repeat(3, 1fr);
    /* Add a gap between grid items (cells) */
    gap: 5px; /* Adjust gap as needed */
    /* Set a max width for the entire board to keep it from being too big on large screens */
    max-width: 300px; /* Adjust this max width as desired for desktop */
    width: 100%; /* Take full width on smaller screens */
    margin: 20px auto; /* Center the grid container and add some vertical margin */
    border: 2px solid #555; /* Optional: Add a border around the entire board */
    border-radius: 8px; /* Optional: Rounded corners for the board */
    padding: 5px; /* Optional: Padding inside the board border */
    box-sizing: border-box; /* Include padding/border in total size */
}

/* 3. Styling for individual game cells */
.tic-tac-toe-cell {
    /* Make cells square based on their width within the grid */
    width: 100%; /* Take full width of its grid column */
    padding-bottom: 100%; /* Create a square aspect ratio */
    position: relative; /* For absolute positioning of content */

    /* Basic visual styles */
    background-color: #f0f2f6; /* Light background for cells */
    border: 1px solid #aaa; /* Cell borders */
    border-radius: 5px;
    display: flex; /* Use flexbox for centering content inside */
    justify-content: center;
    align-items: center;
    cursor: pointer;
    user-select: none; /* Prevent text selection */
    font-weight: bold;
}

/* Style for the actual content (X or O) inside the cell */
.tic-tac-toe-cell-content {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 3em; /* Larger font size for X/O */
}

/* Colors for X and O */
.tic-tac-toe-cell-content.O {
    color: #4B9CFF; /* Blue */
}
.tic-tac-toe-cell-content.X {
    color: #FF4B4B; /* Red */
}

/* Style for disabled cells (when game is over or cell is filled) */
.tic-tac-toe-cell.disabled {
    cursor: not-allowed;
    opacity: 0.7;
}

/* Adjust font size for very small screens if needed */
@media (max-width: 360px) {
    .tic-tac-toe-cell-content {
        font-size: 2.5em; /* Smaller font for very small screens */
    }
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
    # This function needs to be a callback for the HTML buttons
    # Streamlit buttons automatically trigger reruns, but custom HTML buttons need a trick.
    # We will use st.session_state to pass the move, then process it on rerun.
    if st.session_state.turn == "O" and not game_over(st.session_state.board) and st.session_state.board[pos] == " ":
        st.session_state.board[pos] = "O"
        if not game_over(st.session_state.board):
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

def display_board(board):
    is_game_finished = game_over(board)
    board_html = ""
    for i in range(9):
        symbol = board[i]
        disabled_class = "disabled" if is_game_finished or symbol != " " else ""
        content_class = "O" if symbol == "O" else ("X" if symbol == "X" else "")
        
        # Use a hidden Streamlit button or st.form to capture clicks from custom HTML divs
        # Streamlit doesn't directly support callbacks from custom HTML elements.
        # The best workaround for now is to use hidden buttons or an input field.
        # A simpler approach is to only use a hidden button if the cell is clickable.

        if symbol == " " and not is_game_finished:
             # This creates a form for each clickable cell. When the button is clicked,
             # the form is submitted, and we can retrieve the 'idx' from it.
             # This is a common pattern for custom HTML interactions.
            board_html += f"""
            <div class="tic-tac-toe-cell {disabled_class}">
                <form action="" method="get" class="tic-tac-toe-cell-content" style="cursor:pointer;">
                    <input type="hidden" name="action" value="play_move">
                    <input type="hidden" name="pos" value="{i}">
                    <button type="submit" style="all: unset; cursor: pointer; width: 100%; height: 100%; border: none; background: transparent;"></button>
                </form>
            </div>
            """
        else:
            board_html += f"""
            <div class="tic-tac-toe-cell {disabled_class}">
                <div class="tic-tac-toe-cell-content {content_class}">
                    {symbol if symbol != " " else ""}
                </div>
            </div>
            """
    
    st.markdown(f'<div class="tic-tac-toe-grid-container">{board_html}</div>', unsafe_allow_html=True)

# Check for a move from custom HTML button
if 'action' in st.query_params and st.query_params['action'] == 'play_move':
    try:
        pos = int(st.query_params['pos'])
        play_move(pos) # Process the move immediately
        # Clear query params to prevent re-triggering on subsequent reruns
        st.query_params.clear() 
        st.rerun() # Rerun to update board and potentially trigger AI
    except ValueError:
        pass # Ignore if 'pos' is not an integer


display_board(board) # Call this to display the board

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

col1, col2, col3 = st.columns(3) # These statistics columns should be fine as Streamlit handles them well
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
