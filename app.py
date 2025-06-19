import streamlit as st
from agent import TicTacToeAgent
import threading

st.title("Tic Tac Toe with RL Agent 🤖")
st.markdown("""
You are **O** (circles), AI is **X** (crosses).  
You always start first. Click to place your O.  
AI will respond immediately.
""")

# Initialize agent and train if needed
if "agent" not in st.session_state:
    st.session_state.agent = TicTacToeAgent("X")
    # Run training in a thread to avoid blocking (optional)
    if len(st.session_state.agent.value) < 1000:
        def train_agent():
            st.session_state.agent.value = {}
            st.session_state.agent.history = []
            train(st.session_state.agent, n_games=10000)
        threading.Thread(target=train_agent).start()

# Initialize board and states
if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    st.session_state.turn = "O"
    st.session_state.game_over = False

board = st.session_state.board
agent = st.session_state.agent

def winner(board):
    wins = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    for a,b,c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

def game_over(board):
    return winner(board) is not None or " " not in board

def ai_move():
    if not st.session_state.game_over and st.session_state.turn == "X":
        move = agent.select_move(board)
        board[move] = "X"
        st.session_state.turn = "O"
        if game_over(board):
            st.session_state.game_over = True

cols = st.columns(3)
for i in range(3):
    for j in range(3):
        idx = 3*i + j
        with cols[j]:
            if board[idx] == " ":
                if st.button(" ", key=idx):
                    if not st.session_state.game_over and st.session_state.turn == "O":
                        board[idx] = "O"
                        st.session_state.turn = "X"
                        if game_over(board):
                            st.session_state.game_over = True
                        else:
                            ai_move()
            else:
                st.markdown(f"## {board[idx]}")

if st.session_state.game_over:
    w = winner(board)
    if w:
        st.success(f"{w} wins!")
    else:
        st.info("It's a draw!")
    if st.button("Play Again"):
        st.session_state.board = [" "] * 9
        st.session_state.turn = "O"
        st.session_state.game_over = False
        st.experimental_rerun()
