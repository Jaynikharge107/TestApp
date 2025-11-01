import streamlit as st
import math

# --- Page Setup ---
st.set_page_config(page_title="Retro Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom CSS for Retro Look ---
st.markdown("""
    <style>
    body {
        background-color: #f5f2e7;
        color: #2b2b2b;
        font-family: 'Courier New', monospace;
    }
    .stApp {
        background-color: #f5f2e7;
    }
    .calculator {
        background-color: #fefcf5;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.2);
        width: 380px;
        margin: auto;
        border: 2px solid #dcd2b4;
    }
    .title {
        text-align: center;
        color: #004d4d;
        font-size: 26px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .display {
        background-color: #e3dfc8;
        border-radius: 8px;
        text-align: right;
        font-size: 28px;
        padding: 10px 15px;
        margin-bottom: 10px;
        color: #1a1a1a;
        height: 55px;
        overflow-x: auto;
    }
    .stButton>button {
        background-color: #c7f0db;
        color: #2b2b2b;
        border: 1px solid #a7d7c5;
        border-radius: 8px;
        height: 50px;
        font-size: 18px;
        font-weight: 600;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #b6e3cd;
        border: 1px solid #88c6a3;
    }
    .equals-btn>button {
        background-color: #f7c59f !important;
        color: black !important;
        font-weight: bold;
    }
    .clear-btn>button {
        background-color: #f28b82 !important;
        color: white !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown('<div class="title">🧮 Retro Scientific Calculator</div>', unsafe_allow_html=True)

# --- State ---
if "expression" not in st.session_state:
    st.session_state.expression = ""
if "answer" not in st.session_state:
    st.session_state.answer = ""

# --- Display Area ---
st.markdown(f'<div class="calculator">', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.expression or "0"}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="display" style="background-color:#d8efd3; color:#004d4d;">Ans: {st.session_state.answer or ""}</div>', unsafe_allow_html=True)

# --- Buttons Layout ---
cols = st.columns(4)
buttons = [
    ("7", "8", "9", "/"),
    ("4", "5", "6", "*"),
    ("1", "2", "3", "-"),
    ("0", ".", "=", "+"),
    ("sin", "cos", "tan", "sqrt"),
    ("(", ")", "π", "C")
]

def press(key):
    if key == "C":
        st.session_state.expression = ""
        st.session_state.answer = ""
    elif key == "=":
        try:
            expr = st.session_state.expression.replace("π", str(math.pi))
            result = eval(expr, {"__builtins__": None}, math.__dict__)
            st.session_state.answer = round(result, 6)
        except Exception:
            st.session_state.answer = "Error"
    else:
        st.session_state.expression += key

# --- Create Buttons ---
for row in buttons:
    cols = st.columns(4)
    for i, key in enumerate(row):
        btn_class = ""
        if key == "=":
            btn_class = "equals-btn"
        elif key == "C":
            btn_class = "clear-btn"
        with cols[i]:
            st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
            if st.button(key):
                press(key)
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# --- Keyboard Input ---
keyboard_input = st.text_input("Use Keyboard (numpad supported):", value="", key="input", label_visibility="collapsed")

if keyboard_input:
    if keyboard_input.lower() == "c":
        st.session_state.expression = ""
        st.session_state.answer = ""
    elif keyboard_input == "=":
        try:
            expr = st.session_state.expression.replace("π", str(math.pi))
            st.session_state.answer = round(eval(expr, {"__builtins__": None}, math.__dict__), 6)
        except Exception:
            st.session_state.answer = "Error"
    else:
        st.session_state.expression += keyboard_input
    st.session_state.input = ""
    st.rerun()
