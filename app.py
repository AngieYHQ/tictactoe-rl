import streamlit as st
from agent import TicTacToeAgent

st.title("Tic Tac Toe with AI master 🤖")
st.markdown("""
You are **O** (circle, blue), AI is **X** (cross, red).  
You always start first. Click once to place your O.  
AI will respond immediately.
""")

if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    st.session_state.agent = TicTacToeAgent("X")
    st.session_state.turn = "O"  # User always starts as O

board = st.session_state.board
agent = st.session_state.agent

def play_move(pos):
    if board[pos] == " " and st.session_state.turn == "O":
        board[pos] = "O"
        st.session_state.turn = "X"

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
        cols = st.columns(3, gap="big")
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
        st.session_state.turn = "O"
