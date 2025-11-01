import streamlit as st
import math

# --- Page Config ---
st.set_page_config(page_title="Casio 911 - Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom CSS for Casio-like style ---
st.markdown("""
    <style>
    .stApp {
        background-color: #1c1c1c;
        color: white;
        text-align: center;
    }
    .calculator {
        background-color: #2b2b2b;
        border-radius: 15px;
        width: 340px;
        margin: 0 auto;
        padding: 15px;
        box-shadow: 0px 0px 15px rgba(255,255,255,0.1);
    }
    .display {
        background-color: #d4e0d7;
        color: black;
        text-align: right;
        font-size: 28px;
        border-radius: 8px;
        padding: 10px;
        margin-bottom: 10px;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
    }
    .button {
        width: 70px;
        height: 50px;
        margin: 4px;
        border: none;
        border-radius: 8px;
        font-size: 18px;
        background-color: #3b3b3b;
        color: white;
        transition: all 0.1s ease-in-out;
    }
    .button:hover {
        background-color: #5a5a5a;
    }
    .equal {
        background-color: #0096FF !important;
    }
    .clear {
        background-color: #FF4C4C !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧮 Casio 911EX - Scientific Calculator")
st.caption("Interactive Casio-style scientific calculator built with Streamlit")

# --- Session State to hold input ---
if "expression" not in st.session_state:
    st.session_state.expression = ""

# --- Button Handler ---
def press(btn):
    if btn == "=":
        try:
            # Allow math functions
            allowed_names = {k: v for k, v in math.__dict__.items()}
            allowed_names.update({
                "pi": math.pi,
                "e": math.e,
                "sin": lambda x: math.sin(math.radians(x)),
                "cos": lambda x: math.cos(math.radians(x)),
                "tan": lambda x: math.tan(math.radians(x)),
                "sqrt": math.sqrt,
                "log": math.log10,
                "ln": math.log,
                "abs": abs,
                "pow": pow,
            })
            result = eval(st.session_state.expression, {"__builtins__": {}}, allowed_names)
            st.session_state.expression = str(result)
        except Exception:
            st.session_state.expression = "Error"
    elif btn == "C":
        st.session_state.expression = ""
    else:
        st.session_state.expression += str(btn)

# --- Calculator Layout ---
st.markdown('<div class="calculator">', unsafe_allow_html=True)
st.markdown(f"<div class='display'>{st.session_state.expression}</div>", unsafe_allow_html=True)

# --- Buttons Layout ---
cols = st.columns(5)
buttons = [
    ["7", "8", "9", "/", "C"],
    ["4", "5", "6", "*", "sqrt("],
    ["1", "2", "3", "-", "pow("],
    ["0", ".", "(", ")", "+"],
    ["sin(", "cos(", "tan(", "log(", "ln("],
    ["pi", "e", "abs(", "=", ""],
]

for row in buttons:
    cols = st.columns(5)
    for i, btn in enumerate(row):
        if btn:
            if btn == "=":
                cols[i].button(btn, key=btn, on_click=press, args=(btn,), help="Evaluate", use_container_width=True)
            elif btn == "C":
                cols[i].button(btn, key=btn, on_click=press, args=(btn,), help="Clear", use_container_width=True)
            else:
                cols[i].button(btn, key=btn, on_click=press, args=(btn,), use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

st.caption("Made with ❤️ by Ojas | Casio-style Calculator | Streamlit")
