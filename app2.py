import streamlit as st
import time
from agent import TicTacToeAgent

st.set_page_config(layout="centered", initial_sidebar_state="collapsed") # Good starting point for mobile

st.title("Tic Tac Toe with AI master 🤖")
st.markdown("""
You are <span style="color:blue;">**O**</span> and AI master is <span style="color:red;">**X**</span>.<br>
You always start first. Click once to place your O.<br>
AI will respond within 1 second.
""", unsafe_allow_html=True)

# Initialize session state for game statistics if not already present
if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    # Ensure the agent is initialized once. For a real deployed app, consider lazy loading or singleton pattern.
    if "agent" not in st.session_state:
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

def winner(board):
    wins = [(0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)]
    for a, b, c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

def play_move(pos):
    # Only allow a move if the square is empty, it's the user's turn, AND the game is NOT over
    if board[pos] == " " and st.session_state.turn == "O" and not game_over(board):
        board[pos] = "O"
        # After user's move, check if game is over before changing turn or running AI
        if not game_over(board):
            st.session_state.turn = "X" # Pass turn to AI
        st.rerun()

def print_board(board):
    is_game_finished = game_over(board)

    # Use a single column for the board on small screens, or adjust sizing
    # We'll use custom CSS to try and force a better square look
    st.markdown(
        """
        <style>
        .stButton button {
            width: 100%;
            height: 100%;
            padding: 0;
            font-size: 48px; /* Larger font for better tap target */
            font-weight: bold;
            display: flex;
            justify-content: center;
            align-items: center;
            aspect-ratio: 1 / 1; /* Keep buttons square */
        }
        .board-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr); /* 3 columns, equal width */
            gap: 5px; /* Small gap between cells */
            max-width: 300px; /* Max width for the board to prevent overstretching on large screens */
            margin: auto; /* Center the board */
        }
        .board-cell {
            width: 100%;
            aspect-ratio: 1 / 1; /* Keep cells square */
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 48px;
            font-weight: bold;
            user-select: none;
            background-color: #f0f2f6; /* A subtle background for empty cells */
            border-radius: 5px; /* Slightly rounded corners */
        }
        .symbol-O {
            color: #4B9CFF; /* Blue for O */
        }
        .symbol-X {
            color: #FF4B4B; /* Red for X */
        }
        </style>
        """, unsafe_allow_html=True
    )

    # Instead of st.columns, we'll render the board using pure HTML/CSS grid for better control
    st.markdown('<div class="board-grid">', unsafe_allow_html=True)
    for i in range(9):
        symbol = board[i]
        if symbol == " ":
            # Empty square: Use a button
            st.markdown(
                f"""
                <div class="board-cell">
                    <button id="button_{i}" style="width:100%; height:100%; font-size: 48px; font-weight: bold; {"opacity: 0.5; cursor: not-allowed;" if is_game_finished else ""}" onclick="
                        const el = document.getElementById('button_{i}');
                        if (el.innerText === ' ' && !{str(is_game_finished).lower()}) {{
                            Streamlit.setComponentValue('{i}');
                            // Temporarily disable the button to prevent double-clicks
                            el.disabled = true;
                            el.style.opacity = '0.5';
                            el.style.cursor = 'not-allowed';
                        }}
                    ">{symbol}</button>
                </div>
                """,
                unsafe_allow_html=True
            )
            # This is a trick: We use an invisible Streamlit button to capture clicks
            # and then use JavaScript to call `setComponentValue` which triggers a rerun.
            # We pass the index of the clicked cell.
            if st.button(" ", key=f"hidden_btn_{i}", help="Click to place O", disabled=is_game_finished):
                play_move(i)
        else:
            # Filled square: Display the symbol with color
            color_class = "symbol-X" if symbol == "X" else "symbol-O"
            st.markdown(
                f"""
                <div class="board-cell {color_class}">
                    {symbol}
                </div>
                """,
                unsafe_allow_html=True
            )
    st.markdown('</div>', unsafe_allow_html=True)


print_board(board)

# AI's turn
if not game_over(board) and st.session_state.turn == "X":
    with st.spinner("AI thinking..."): # Provide visual feedback while AI thinks
        time.sleep(1) # Reduced delay slightly for quicker testing, adjust as needed
        move = agent.select_move(board)
        if move is not None and board[move] == " ":
            board[move] = "X"
            if not game_over(board):
                st.session_state.turn = "O"
            st.rerun()
        else:
            st.error("AI could not make a valid move. This shouldn't happen.")
            st.session_state.turn = "O" # Pass turn back to user as fallback


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

    # Use a container for game over buttons to ensure they stack well
    st.markdown("---")
    st.subheader("Game Actions")
    col_restart, col_dummy = st.columns([0.6, 0.4]) # Give "Play Again" more space
    with col_restart:
        if st.button("Play Again", key="play_again_btn"):
            st.session_state.board = [" "] * 9
            st.session_state.turn = "O"
            st.session_state.game_outcome_recorded = False
            st.rerun()
    with col_dummy:
        pass # Empty column for spacing if needed

# --- Display Statistics ---
st.markdown("---")
st.subheader("Game Statistics")

total = st.session_state.total_games
user_win_rate = (st.session_state.user_wins / total * 100) if total > 0 else 0
ai_win_rate = (st.session_state.ai_wins / total * 100) if total > 0 else 0
draw_rate = (st.session_state.draws / total * 100) if total > 0 else 0

# Use columns for statistics, but they will naturally stack on small screens
stat_col1, stat_col2 = st.columns(2)
with stat_col1:
    st.metric("Games Played", st.session_state.total_games)
    st.metric("Your Wins (O)", f"{st.session_state.user_wins} ({user_win_rate:.1f}%)")
with stat_col2:
    st.metric("AI Wins (X)", f"{st.session_state.ai_wins} ({ai_win_rate:.1f}%)")
    st.metric("Draws", f"{st.session_state.draws} ({draw_rate:.1f}%)")

st.markdown("---")
if st.button("Reset Statistics", help="Clear all win/loss/draw counts", key="reset_stats_btn"):
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False
    st.rerun()
