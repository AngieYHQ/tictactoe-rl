import streamlit as st
import time
from agent import TicTacToeAgent

st.title("Tic Tac Toe with AI master 🤖")
st.markdown("""
You are <span style="color:blue;">**O**</span> and AI master is <span style="color:red;">**X**</span>.<br>
You always start first. Click once to place your O.<br>
AI will respond within 1 second.
""", unsafe_allow_html=True)

# Initialize session state for game statistics if not already present
if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    st.session_state.agent = TicTacToeAgent("X", q_value_file="agent_q_values_X.json", epsilon=0.0)
    st.session_state.turn = "O"
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False # Add this flag if not already there

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
    # Only allow a move if the square is empty, it's the user's turn, AND the game is NOT over
    if board[pos] == " " and st.session_state.turn == "O" and not game_over(board): # <--- IMPORTANT CHANGE HERE
        board[pos] = "O"
        # After user's move, check if game is over before changing turn or running AI
        if not game_over(board): # <--- CHECK GAME OVER AFTER USER MOVE
            st.session_state.turn = "X" # Pass turn to AI
        st.rerun()

def winner(board):
    # ... (same winner function as before)
    wins = [(0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)]
    for a, b, c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None


def print_board(board):
    is_game_finished = game_over(board) # Check game state once

    for i in range(3):
        cols = st.columns(3, gap="small")
        for j in range(3):
            idx = 3*i + j
            with cols[j]:
                symbol = board[idx]
                if symbol == " ":
                    # Empty square
                    # Disable the button if the game is over
                    clicked = st.button(
                        " ",
                        key=f"btn_{idx}",
                        help=f"Click to place O",
                        disabled=is_game_finished # <--- IMPORTANT CHANGE HERE
                    )
                    if clicked:
                        play_move(idx) # This will now also check game_over internally
                else:
                    # Filled square
                    color = "#FF4B4B" if symbol == "X" else "#4B9CFF"
                    st.markdown(f"""
                        <div style="
                            width: 60px;
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

print_board(board) # Call this to display the board

# AI's turn
# Ensure AI only moves if game is NOT over and it's its turn
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
