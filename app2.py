import streamlit as st
import time
# Assuming TicTacToeAgent is defined in 'agent.py' and 'agent_q_values_X.json' exists.
# You'll need to have these files alongside your Streamlit app script.
from agent import TicTacToeAgent 

# Inject custom CSS for a robust 3x3 grid using CSS Grid, optimized for small screens
# This CSS aims to make the Tic-Tac-Toe board as compact as possible
# while maintaining a 3x3 layout even on the smallest iPhone screens.
st.markdown("""
<style>
/* 1. Global App Centering */
/* This ensures the entire Streamlit app content is horizontally centered. */
.stApp {
    display: flex;
    flex-direction: column;
    align-items: center; /* Center content horizontally */
    padding-top: 0.5rem;    /* Reduced top padding for more screen space */
    padding-bottom: 0.5rem; /* Reduced bottom padding */
}

/* 2. Style for the Tic-Tac-Toe board container using CSS Grid */
/* This is the main container that holds all 9 individual game cells. */
.tic-tac-toe-grid-container {
    display: grid;
    /* Define 3 columns. '1fr' means each column takes an equal fraction of the available space. */
    /* This is critical for ensuring the 3x3 layout does not stack vertically. */
    grid-template-columns: repeat(3, 1fr);
    /* Set a small gap between grid items (the individual cells). */
    gap: 3px; 
    /* Set a maximum width for the entire board. This prevents it from becoming too large on desktops. */
    max-width: 250px; /* Adjusted for maximum compactness */
    /* Make the board take up a high percentage of the viewport width on mobile. */
    width: 95vw; /* 95% of viewport width, leaving minimal side margins */
    /* Center the grid container horizontally and reduce vertical margins. */
    margin: 10px auto; 
    /* Optional: Add a border around the entire board for visual separation. */
    border: 2px solid #555; 
    border-radius: 8px; /* Apply rounded corners to the board border. */
    /* Optional: Add slight padding inside the board border. */
    padding: 3px; 
    /* Ensure padding and border are included in the element's total size calculation. */
    box-sizing: border-box; 
}

/* 3. Styling for individual game cells */
/* These styles apply to each of the 9 squares on the Tic-Tac-Toe board. */
.tic-tac-toe-cell {
    /* Make cells square based on their width within the grid. */
    /* 'width: 100%' makes it fill its grid column, 'padding-bottom: 100%' sets height equal to width. */
    width: 100%; 
    padding-bottom: 100%; 
    /* Required for absolutely positioning the X/O content inside. */
    position: relative; 

    /* Basic visual styles for the cell background and border. */
    background-color: #f0f2f6; 
    border: 1px solid #aaa; 
    border-radius: 5px; /* Rounded corners for individual cells. */
    
    /* Use flexbox to center the content (X, O, or clickable area) within the cell. */
    display: flex; 
    justify-content: center;
    align-items: center;
    
    cursor: pointer;    /* Indicate that the cell is clickable. */
    user-select: none;  /* Prevent text selection on X/O symbols. */
    font-weight: bold;
}

/* Style for the actual content (X or O) inside the cell */
/* This element is positioned absolutely to fill its parent cell and center the symbol. */
.tic-tac-toe-cell-content {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    /* Use flexbox again to perfectly center the symbol within its content container. */
    display: flex; 
    justify-content: center;
    align-items: center;
    /* Set font size relative to the parent, making it scale with cell size. */
    font-size: 2.5em; /* Adjusted for compactness */
}

/* Colors for X and O symbols */
.tic-tac-toe-cell-content.O {
    color: #4B9CFF; /* Blue for user's 'O' */
}
.tic-tac-toe-cell-content.X {
    color: #FF4B4B; /* Red for AI's 'X' */
}

/* Style for disabled cells (when game is over or cell is already filled) */
.tic-tac-toe-cell.disabled {
    cursor: not-allowed; /* Change cursor to indicate non-interactiveness. */
    opacity: 0.7;        /* Make disabled cells slightly faded. */
}

/* Specific media query for extremely small screens (e.g., iPhone SE 1st Gen) */
/* This ensures the layout remains usable on the absolute smallest mobile viewports. */
@media (max-width: 320px) {
    .tic-tac-toe-grid-container {
        /* Further reduce max width for the entire board. */
        max-width: 220px; 
        /* Take up an even higher percentage of viewport width on these tiny screens. */
        width: 98vw; 
        /* Minimize gap and padding to reclaim every possible pixel. */
        gap: 2px; 
        padding: 2px; 
    }
    .tic-tac-toe-cell-content {
        /* Ensure font fits even if cells become very small. */
        font-size: 2em; 
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

# Initialize session state for game statistics and board state if not already present.
# Session state is crucial in Streamlit for maintaining variables across reruns.
if "board" not in st.session_state:
    st.session_state.board = [" "] * 9 # The Tic-Tac-Toe board, initialized empty
    try:
        # Initialize the AI agent. This requires 'agent.py' and 'agent_q_values_X.json' to be present.
        st.session_state.agent = TicTacToeAgent("X", q_value_file="agent_q_values_X.json", epsilon=0.0)
    except FileNotFoundError:
        # Graceful error handling if the necessary AI files are missing.
        st.error("Error: 'agent_q_values_X.json' not found. Please ensure the AI Q-value file is in the same directory.")
        st.stop() # Stop the app execution if a critical file is missing.
    except Exception as e:
        st.error(f"Error initializing AI agent: {e}. Make sure agent.py is correctly defined.")
        st.stop()

    st.session_state.turn = "O" # 'O' (user) starts first.
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False # Flag to ensure game outcome is recorded only once per game.

board = st.session_state.board
agent = st.session_state.agent

# Helper function to check if the game has ended.
def game_over(board_state):
    """Checks if the game has ended (either a win or a draw)."""
    wins = [(0,1,2), (3,4,5), (6,7,8), # Horizontal wins
            (0,3,6), (1,4,7), (2,5,8), # Vertical wins
            (0,4,8), (2,4,6)]          # Diagonal wins
    
    # Check for a winner
    for a, b, c in wins:
        if board_state[a] == board_state[b] == board_state[c] and board_state[a] != " ":
            return True # A player has won

    # Check for a draw (no winner and no empty spaces left)
    return " " not in board_state 

# Function to handle a user's move.
def play_move(pos):
    """Processes a user's move if valid."""
    # Ensure the move is valid: empty square, user's turn, and game not over.
    if st.session_state.board[pos] == " " and st.session_state.turn == "O" and not game_over(st.session_state.board):
        st.session_state.board[pos] = "O" # Place 'O' on the board.
        # After user's move, check if game is over before changing turn or triggering AI.
        if not game_over(st.session_state.board): 
            st.session_state.turn = "X" # Pass turn to AI.
        # Set a flag to indicate a rerun is needed after processing this move.
        st.session_state._trigger_rerun_after_move = True 

# Helper function to determine the winner of the game.
def winner(board_state):
    """Returns the winning symbol ('X' or 'O') or None if no winner."""
    wins = [(0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)]
    for a, b, c in wins:
        if board_state[a] == board_state[b] == board_state[c] and board_state[a] != " ":
            return board_state[a] # Return the symbol of the winner.
    return None # No winner yet.

# Function to display the Tic-Tac-Toe board using custom HTML and CSS Grid.
def display_board(board_state):
    """Renders the Tic-Tac-Toe board as a 3x3 grid."""
    is_game_finished = game_over(board_state)
    board_html = "" # Initialize an empty string to build the board HTML.

    # Loop through all 9 positions on the board.
    for i in range(9):
        symbol = board_state[i]
        # Determine if the cell should be disabled (game over or already filled).
        disabled_class = "disabled" if is_game_finished or symbol != " " else ""
        # Determine the class for coloring the symbol (O or X).
        content_class = "O" if symbol == "O" else ("X" if symbol == "X" else "")
        
        # If the cell is empty and the game is ongoing, make it clickable using a hidden form/button.
        if symbol == " " and not is_game_finished:
             board_html += f"""
            <div class="tic-tac-toe-cell {disabled_class}">
                <form action="" method="get" class="tic-tac-toe-cell-content" style="cursor:pointer;">
                    <input type="hidden" name="action" value="play_move">
                    <input type="hidden" name="pos" value="{i}">
                    <button type="submit" style="all: unset; cursor: pointer; width: 100%; height: 100%; border: none; background: transparent;"></button>
                </form>
            </div>
            """
        # If the cell is filled or the game is over, just display the symbol (non-clickable).
        else:
            board_html += f"""
            <div class="tic-tac-toe-cell {disabled_class}">
                <div class="tic-tac-toe-cell-content {content_class}">
                    {symbol if symbol != " " else ""} {/* Display X/O, or empty string if cell is empty but disabled */}
                </div>
            </div>
            """
    
    # Render the entire board HTML within the Streamlit app.
    st.markdown(f'<div class="tic-tac-toe-grid-container">{board_html}</div>', unsafe_allow_html=True)

# --- Process Clicks from Custom HTML Buttons ---
# Streamlit reruns the script on every interaction. We check if a custom HTML button
# (via its form submission) has added 'action' and 'pos' to the URL query parameters.
if 'action' in st.query_params and st.query_params['action'] == 'play_move':
    try:
        pos = int(st.query_params['pos'])
        play_move(pos) # Call the Python function to process the move.
        
        # Clear query parameters to prevent the move from being re-executed on subsequent reruns.
        # This is crucial to avoid unintended actions or infinite loops.
        st.query_params.clear()
        
        # Force a rerun to update the board state and allow the AI to play its turn.
        st.rerun() 
    except ValueError:
        pass # Ignore if 'pos' parameter is not a valid integer.


# --- Display the Board ---
display_board(board) 

# --- AI's Turn Logic ---
# The AI makes a move only if the game is not over and it's currently the AI's turn ('X').
if not game_over(board) and st.session_state.turn == "X":
    time.sleep(1) # Introduce a small delay to simulate AI "thinking".
    move = agent.select_move(board) # AI selects its best move.
    
    # Ensure the AI's selected move is valid (within board boundaries and on an empty square).
    if move is not None and board[move] == " ":
        board[move] = "X" # Place AI's 'X' on the board.
        # After AI's move, check game state before passing turn back to user.
        if not game_over(board): 
            st.session_state.turn = "O" # Pass turn back to user ('O').
        st.rerun() # Force a rerun to display AI's move and potentially check for game end.
    else:
        # This is a fallback error message if AI fails to make a valid move (should rarely happen).
        st.error("AI could not make a valid move. This shouldn't happen.")
        st.session_state.turn = "O" # Pass turn back to user as a fallback.


# --- Game Over Logic ---
# This block executes when the game reaches a terminal state (win or draw).
if game_over(board):
    # Record game outcome statistics only once per game.
    if st.session_state.get('game_outcome_recorded', False) == False:
        st.session_state.total_games += 1
        current_winner = winner(board)
        if current_winner == "O":
            st.session_state.user_wins += 1
        elif current_winner == "X":
            st.session_state.ai_wins += 1
        else:
            st.session_state.draws += 1
        st.session_state.game_outcome_recorded = True # Set flag to prevent re-recording.

    # Display game outcome message to the user.
    current_winner = winner(board)
    if current_winner == "O":
        st.success("You win! 🎉")
    elif current_winner == "X":
        st.error("AI Master wins! 😈")
    else:
        st.info("It's a draw! 🤝")

    # 'Play Again' button to reset the game.
    if st.button("Play Again"):
        st.session_state.board = [" "] * 9 # Reset board to empty.
        st.session_state.turn = "O"        # Reset turn to user.
        st.session_state.game_outcome_recorded = False # Reset flag.
        st.rerun() # Force rerun to restart the game.

# --- Display Game Statistics ---
st.markdown("---") # Visual separator.
st.subheader("Game Statistics")

total = st.session_state.total_games
# Calculate win/draw rates, handle division by zero if no games played yet.
user_win_rate = (st.session_state.user_wins / total * 100) if total > 0 else 0
ai_win_rate = (st.session_state.ai_wins / total * 100) if total > 0 else 0
draw_rate = (st.session_state.draws / total * 100) if total > 0 else 0

# Display statistics using Streamlit metrics in a 3-column layout.
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Games Played", st.session_state.total_games)
with col2:
    st.metric("Your Wins (O)", f"{st.session_state.user_wins} ({user_win_rate:.1f}%)")
with col3:
    st.metric("AI Wins (X)", f"{st.session_state.ai_wins} ({ai_win_rate:.1f}%)")

# Display draw count separately.
st.metric("Draws", f"{st.session_state.draws} ({draw_rate:.1f}%)")

# 'Reset Statistics' button.
if st.button("Reset Statistics", help="Clear all win/loss/draw counts"):
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False
    st.rerun() # Force rerun to update displayed statistics.
