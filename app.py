import streamlit as st
from agent import TicTacToeAgent

st.set_page_config(page_title="Tic Tac Toe AI", page_icon="🎮")

st.title("Tic Tac Toe with AI master 🤖")
st.markdown("""
<style>
/* Make buttons bigger with consistent size */
div.stButton > button {
    width: 80px !important;
    height: 80px !important;
    font-size: 24px !important;
    border: 1px solid #555 !important;
    background-color: white !important;
}

/* Remove border for disabled buttons */
div.stButton > button[disabled] {
    border: none !important;
    background-color: transparent !important;
    cursor: default !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
You are **O** (circle, blue), AI is **X** (cross, red).  
You always start first. Click a square to place your O.  
AI will respond immediately.
""")

if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    st.session_state.agent = TicTacToeAgent("X")
    st.session_state.turn = "O"  # User starts as O

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
        cols = st.columns(3, gap="small")
        for j in range(3):
            idx = 3*i + j
            with cols[j]:
                symbol = board[idx]
                if symbol == " ":
                    clicked = st.button(" ", key=f"btn_{idx}", help=f"Click to place O")
                    if clicked:
                        play_move(idx)
                else:
                    color = "#FF4B4B" if symbol == "X" else "#4B9CFF"
                    st.markdown(f"""
                        <div style="
                            width: 80px;
                            height: 80px;
                            font-size: 32px;
                            font-weight: bold;
                            color: {color};
                            text-align: center;
                            line-height: 80px;
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
