import streamlit as st
from agent import TicTacToeAgent, train
import threading

st.set_page_config(page_title="Tic Tac Toe AI", page_icon="🎮")
st.title("Tic Tac Toe with AI Master 🤖")
st.markdown("""
You are **O** (circle, blue), AI is **X** (cross, red).  
You start first. Click a square to place your O.  
AI will respond immediately.
""")

# Initialize agent and train if needed
if "agent" not in st.session_state:
    st.session_state.agent = TicTacToeAgent("X")
    if len(st.session_state.agent.value) < 1000:
        def train_agent():
            train(st.session_state.agent, n_games=10000)
        threading.Thread(target=train_agent).start()

# Initialize game state
if "board" not in st.session_state:
    st.session_state.board = [" "] * 9
    st.session_state.turn = "O"
    st.session_state.game_over = False

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

def game_over(board):
    return winner(board) is not None or " " not in board

def play_move(pos):
    if st.session_state.turn == "O" and board[pos] == " " and not st.session_state.game_over:
        board[pos] = "O"
        if game_over(board):
            st.session_state.game_over = True
        else:
            st.session_state.turn = "X"
            ai_move()

def ai_move():
    if st.session_state.turn == "X" and not st.session_state.game_over:
        move = agent.select_move(board)
        board[move] = "X"
        if game_over(board):
            st.session_state.game_over = True
        else:
            st.session_state.turn = "O"

def print_board(board):
    for i in range(3):
        cols = st.columns(3, gap="small")
        for j in range(3):
            index = 3 * i + j
            with cols[j]:
                symbol = board[index]
                if not st.session_state.game_over and symbol == " ":
                    if st.button(" ", key=f"btn_{index}", help=f"Click to place O"):
                        play_move(index)
                else:
                    color = "#FF4B4B" if symbol == "X" else "#4B9CFF"
                    st.markdown(f"""
                        <button disabled
                            style="
                                width: 60px;
                                height: 60px;
                                font-size: 32px;
                                font-weight: bold;
                                background-color: transparent;
                                border: none;
                                color: {color};
                                cursor: default;
                                padding: 0;
                                margin: 0;
                            "
                        >{symbol}</button>
                    """, unsafe_allow_html=True)

print_board(board)

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
