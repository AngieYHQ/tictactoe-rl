# import streamlit as st
# import time # Import the time module
# from agent import TicTacToeAgent

# st.title("Tic Tac Toe with AI master 🤖")
# st.markdown("""
# You are **O** (circle, blue), AI is **X** (cross, red).
# You always start first. Click once to place your O.
# AI will respond immediately.
# """)

# if "board" not in st.session_state:
#     st.session_state.board = [" "] * 9
#     st.session_state.agent = TicTacToeAgent("X")
#     st.session_state.turn = "O"  # User always starts as O

# board = st.session_state.board
# agent = st.session_state.agent

# def play_move(pos):
#     if board[pos] == " " and st.session_state.turn == "O":
#         board[pos] = "O"
#         st.session_state.turn = "X"
#         st.rerun()

# def winner(board):
#     wins = [(0,1,2), (3,4,5), (6,7,8),
#             (0,3,6), (1,4,7), (2,5,8),
#             (0,4,8), (2,4,6)]
#     for a, b, c in wins:
#         if board[a] == board[b] == board[c] and board[a] != " ":
#             return board[a]
#     return None

# def game_over(board):
#     return winner(board) is not None or " " not in board

# def print_board(board):
#     for i in range(3):
#         cols = st.columns(3, gap="small")
#         for j in range(3):
#             idx = 3*i + j
#             with cols[j]:
#                 symbol = board[idx]
#                 if symbol == " ":
#                     # empty square with border
#                     clicked = st.button(" ", key=f"btn_{idx}", help=f"Click to place O")
#                     if clicked:
#                         play_move(idx)
#                 else:
#                     # filled square: no border, colored X or O, fixed size
#                     color = "#FF4B4B" if symbol == "X" else "#4B9CFF"
#                     st.markdown(f"""
#                         <div style="
#                             width: 60px;
#                             height: 60px;
#                             font-size: 32px;
#                             font-weight: bold;
#                             color: {color};
#                             text-align: center;
#                             line-height: 60px;
#                             user-select: none;
#                         ">
#                             {symbol}
#                         </div>
#                     """, unsafe_allow_html=True)

# print_board(board)

# # AI's turn
# if not game_over(board) and st.session_state.turn == "X":
#     # Add a 2-second delay here
#     time.sleep(1) # <--- ADDED THIS LINE
#     move = agent.select_move(board)
#     board[move] = "X"
#     st.session_state.turn = "O"
#     st.rerun()

# if game_over(board):
#     w = winner(board)
#     if w:
#         st.success(f"{w} wins!")
#     else:
#         st.info("It's a draw!")
#     if st.button("Play Again"):
#         st.session_state.board = [" "] * 9
#         st.session_state.turn = "O"
#         st.rerun()


import streamlit as st
import time
from agent import TicTacToeAgent

st.title("Tic Tac Toe with AI master 🤖")
st.markdown("""
You are **O** (circle, blue), AI is **X** (cross, red).
You always start first. Click once to place your O.
AI will respond immediately.
""")

# Initialize session state for game statistics if not already present
if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    # Initialize the AI agent, pointing to the saved Q-values
    # Set epsilon to 0.0 when playing against a human to ensure optimal play (no exploration)
    st.session_state.agent = TicTacToeAgent("X", q_value_file="agent_q_values_X.json", epsilon=0.0)
    st.session_state.turn = "O"  # User always starts as O
    
    # Initialize game statistics
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0

board = st.session_state.board
agent = st.session_state.agent

def play_move(pos):
    if board[pos] == " " and st.session_state.turn == "O":
        board[pos] = "O"
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

def game_over(board):
    return winner(board) is not None or " " not in board

def print_board(board):
    for i in range(3):
        cols = st.columns(3, gap="small")
        for j in range(3):
            idx = 3*i + j
            with cols[j]:
                symbol = board[idx]
                if symbol == " ":
                    # empty square with border
                    clicked = st.button(" ", key=f"btn_{idx}", help=f"Click to place O")
                    if clicked:
                        play_move(idx)
                else:
                    # filled square: no border, colored X or O, fixed size
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

print_board(board)

# AI's turn
if not game_over(board) and st.session_state.turn == "X":
    time.sleep(2) # 2-second delay for AI move
    move = agent.select_move(board)
    # Ensure AI selects a valid move (should always happen with your agent logic)
    if move is not None and board[move] == " ":
        board[move] = "X"
        st.session_state.turn = "O"
        st.rerun()
    else:
        # Fallback if AI somehow fails to make a valid move (e.g., board full or error)
        st.error("AI could not make a valid move. This shouldn't happen.")
        st.session_state.turn = "O" # Pass turn back to user

if game_over(board):
    # Only update statistics once per game when it's over
    if st.session_state.get('game_outcome_recorded', False) == False: # Prevents double counting on rerun
        st.session_state.total_games += 1
        w = winner(board)
        if w == "O":
            st.session_state.user_wins += 1
            st.success("You win! 🎉")
        elif w == "X":
            st.session_state.ai_wins += 1
            st.error("AI Master wins! 😈")
        else:
            st.session_state.draws += 1
            st.info("It's a draw! 🤝")
        st.session_state.game_outcome_recorded = True # Mark outcome as recorded

    # Display game outcome message after recording
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
        st.session_state.game_outcome_recorded = False # Reset for new game
        st.rerun()

# --- Display Statistics ---
st.markdown("---")
st.subheader("Game Statistics")

# Calculate rates
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

# Add a reset statistics button
if st.button("Reset Statistics", help="Clear all win/loss/draw counts"):
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False # Ensure this is also reset
    st.rerun()
