import streamlit as st
from agent import TicTacToeAgent

st.title("Tic Tac Toe with RL Agent 🤖")
st.markdown("You are **O**, the AI is **X**.")

if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    st.session_state.agent = TicTacToeAgent("X")
    st.session_state.turn = "X"

board = st.session_state.board
agent = st.session_state.agent

def print_board(board):
    for i in range(3):
        cols = st.columns(3)
        for j in range(3):
            index = 3*i + j
            with cols[j]:
                if board[index] == " ":
                    if st.button(" ", key=index):
                        if st.session_state.turn == "O":
                            board[index] = "O"
                            st.session_state.turn = "X"
                else:
                    st.markdown(f"## {board[index]}")

print_board(board)

def winner(board):
    wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
    for a, b, c in wins:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None

def game_over(board):
    return winner(board) is not None or " " not in board

if not game_over(board) and st.session_state.turn == "X":
    move = agent.select_move(board)
    board[move] = "X"
    st.session_state.turn = "O"

if game_over(board):
    w = winner(board)
    if w:
        st.success(f"{w} wins!")
    else:
        st.info("It's a draw!")
    if st.button("Play Again"):
        st.session_state.board = [" "] * 9
        st.session_state.turn = "X"