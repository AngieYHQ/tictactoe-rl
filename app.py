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
    st.session_state.agent = TicTacToeAgent("X", q_value_file="agent_q_values_X.json", epsilon=0.0)
    st.session_state.turn = "O"
    st.session_state.total_games = 0
    st.session_state.user_wins = 0
    st.session_state.ai_wins = 0
    st.session_state.draws = 0
    st.session_state.game_outcome_recorded = False
    st.session_state.explicit_draw_declared = False # New flag for early draw declaration

board = st.session_state.board
agent = st.session_state.agent

def winner(board):
    wins = [(0,1,2), (3,4,5), (6,7,8),
            (0,3,6), (1,4,7), (2,5,8),
            (0,4,8), (2,4,6)]
    for a, b, c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

# Modified game_over to also consider explicit_draw_declared
def game_over(board):
    return winner(board) is not None or " " not in board or st.session_state.explicit_draw_declared

def play_move(pos):
    if board[pos] == " " and st.session_state.turn == "O" and not game_over(board):
        board[pos] = "O"
        # Check if user's move resulted in a win or draw
        if winner(board):
            st.session_state.turn = "DONE" # End turn processing
            st.rerun()
            return
        elif " " not in board: # Board is full, it's a draw
            st.session_state.turn = "DONE" # End turn processing
            st.rerun()
            return

        # Check if a draw is inevitable for the AI's next move from this board state
        # Simulate AI's optimal play to see if it leads to a draw
        # Temporarily clear AI's minimax memo to ensure fresh calculation for this check
        agent.minimax_memo = {} # Clear memoization for a fresh evaluation
        ai_optimal_score = agent.minimax_evaluate(board, agent.symbol) # Evaluate from AI's perspective (X)
        if ai_optimal_score == 0: # If AI evaluates the current state as a forced draw
            st.session_state.explicit_draw_declared = True
            st.session_state.turn = "DONE" # End turn processing
        else:
            st.session_state.turn = "X" # Pass turn to AI

        st.rerun()

def print_board(board):
    is_game_finished = game_over(board)

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
    time.sleep(1.5)
    agent.minimax_memo = {} # Clear memoization for AI's actual move selection
    move = agent.select_move(board)

    if move is not None and board[move] == " ":
        board[move] = "X"
        # After AI's move, check if it won or resulted in a draw
        if winner(board):
            st.session_state.turn = "DONE" # Game ended with AI win
        elif " " not in board: # Board is full, it's a draw
            st.session_state.turn = "DONE"
        else:
            # Check if AI's move led to a state where a draw is now inevitable
            # Evaluate from user's perspective (O) for their next turn
            agent.minimax_memo = {} # Clear memo for evaluation from opponent's perspective
            user_optimal_score = agent.minimax_evaluate(board, agent.opponent(agent.symbol)) # Evaluate for 'O'
            if user_optimal_score == 0: # If user can only force a draw
                st.session_state.explicit_draw_declared = True
                st.session_state.turn = "DONE" # Game ended as a draw
            else:
                st.session_state.turn = "O" # Pass turn back to user

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
        elif st.session_state.explicit_draw_declared: # Prioritize explicit draw declaration
            st.session_state.draws += 1
            w = None # Set winner to None to force draw message
        else: # Standard draw (board full)
            st.session_state.draws += 1
        st.session_state.game_outcome_recorded = True

    # Display game outcome message
    w = winner(board) # Re-evaluate winner for message display
    if w == "O":
        st.success("You win! 🎉")
    elif w == "X":
        st.error("AI Master wins! 😈")
    else: # If no winner, it's a draw (either explicit or board full)
        st.info("It's a draw! 🤝")

    if st.button("Play Again"):
        st.session_state.board = [" "] * 9
        st.session_state.turn = "O"
        st.session_state.game_outcome_recorded = False
        st.session_state.explicit_draw_declared = False # Reset explicit draw flag
        agent.minimax_memo = {} # Clear AI's memoization for a fresh game
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
    st.session_state.explicit_draw_declared = False # Reset
    agent.minimax_memo = {} # Clear
    st.rerun()
