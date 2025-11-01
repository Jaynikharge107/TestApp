import streamlit as st
import math

# --- Page Config ---
st.set_page_config(page_title="Casio 911EX - Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom CSS ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 20% 20%, #0e0e0e, #1a1a1a);
        color: #fff;
        font-family: 'Poppins', sans-serif;
    }
    .calc-container {
        max-width: 400px;
        background: linear-gradient(145deg, #2d2d2d, #1f1f1f);
        border-radius: 25px;
        margin: 40px auto;
        padding: 20px;
        box-shadow: 10px 10px 20px #0a0a0a, -5px -5px 15px #3a3a3a;
    }
    .display {
        background: #e0f0dc;
        color: #000;
        font-size: 30px;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 25px;
        text-align: right;
        font-family: 'Courier New', monospace;
        box-shadow: inset 2px 2px 8px #9fa9a3;
    }
    .stButton > button {
        height: 60px;
        width: 100%;
        border: none;
        border-radius: 12px;
        font-size: 20px;
        font-weight: 600;
        transition: 0.1s ease-in-out;
        color: white;
    }
    /* Different button colors */
    .number-btn > button {
        background-color: #404040;
    }
    .number-btn > button:hover {
        background-color: #555;
    }
    .func-btn > button {
        background-color: #0052cc;
    }
    .func-btn > button:hover {
        background-color: #0066ff;
    }
    .op-btn > button {
        background-color: #ff9500;
    }
    .op-btn > button:hover {
        background-color: #ffaa33;
    }
    .clear-btn > button {
        background-color: #e53935;
    }
    .clear-btn > button:hover {
        background-color: #ff5c5c;
    }
    .equal-btn > button {
        background-color: #0096FF;
    }
    .equal-btn > button:hover {
        background-color: #33adff;
    }
    h1 {
        text-align: center;
        color: #00BFFF;
        margin-bottom: 0;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title ---
st.markdown("<h1>🧮 Casio 911EX</h1>", unsafe_allow_html=True)
st.caption("A premium Casio-style scientific calculator built with Streamlit")

# --- Session State ---
if "exp" not in st.session_state:
    st.session_state.exp = ""

# --- Logic ---
def press(key):
    if key == "C":
        st.session_state.exp = ""
    elif key == "=":
        try:
            allowed = {k: v for k, v in math.__dict__.items()}
            allowed.update({
                "pi": math.pi,
                "e": math.e,
                "sin": lambda x: math.sin(math.radians(x)),
                "cos": lambda x: math.cos(math.radians(x)),
                "tan": lambda x: math.tan(math.radians(x)),
                "log": math.log10,
                "ln": math.log,
                "sqrt": math.sqrt,
                "pow": pow,
                "abs": abs
            })
            st.session_state.exp = str(eval(st.session_state.exp, {"__builtins__": {}}, allowed))
        except Exception:
            st.session_state.exp = "Error"
    else:
        st.session_state.exp += str(key)

# --- UI ---
st.markdown('<div class="calc-container">', unsafe_allow_html=True)
st.markdown(f'<div class="display">{st.session_state.exp}</div>', unsafe_allow_html=True)

layout = [
    ["sin(", "cos(", "tan(", "log(", "ln("],
    ["7", "8", "9", "/", "sqrt("],
    ["4", "5", "6", "*", "pow("],
    ["1", "2", "3", "-", "pi"],
    ["0", ".", "(", ")", "+"],
    ["C", "e", "abs(", "=", ""]
]

for row in layout:
    cols = st.columns(5, gap="small")
    for i, key in enumerate(row):
        if key:
            # Color-code buttons
            if key in ["0","1","2","3","4","5","6","7","8","9",".","(",")","pi","e"]:
                btn_class = "number-btn"
            elif key in ["sin(","cos(","tan(","log(","ln(","sqrt(","pow(","abs("]:
                btn_class = "func-btn"
            elif key in ["+","-","*","/"]:
                btn_class = "op-btn"
            elif key == "=":
                btn_class = "equal-btn"
            elif key == "C":
                btn_class = "clear-btn"
            else:
                btn_class = "number-btn"

            with cols[i]:
                st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
                st.button(key, on_click=press, args=(key,))
                st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
st.caption("✨ Designed by Ojas | Looks like Casio | Built with ❤️ in Streamlit")
