import streamlit as st
import math

# --- Page Setup ---
st.set_page_config(page_title="Casio 911EX - Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom CSS ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 20% 20%, #1f1f1f, #000000);
        color: #fff;
        font-family: 'Poppins', sans-serif;
    }
    .calc-container {
        max-width: 420px;
        background: linear-gradient(145deg, #2c2c2c, #1b1b1b);
        border-radius: 25px;
        margin: 40px auto;
        padding: 20px 25px 30px;
        box-shadow: 10px 10px 20px #0a0a0a, -5px -5px 15px #2a2a2a;
    }
    .display {
        background: #cde0cc;
        color: #000;
        font-size: 28px;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 20px;
        text-align: right;
        font-family: 'Courier New', monospace;
        box-shadow: inset 2px 2px 8px #9fa9a3;
        overflow-x: auto;
    }
    button[data-baseweb="button"] {
        border-radius: 10px !important;
        height: 60px !important;
        font-size: 18px !important;
        font-weight: 600 !important;
        background-color: #292929 !important;
        color: white !important;
        border: 1px solid #3a3a3a !important;
        transition: 0.1s ease-in-out;
    }
    button[data-baseweb="button"]:hover {
        background-color: #3a3a3a !important;
        border: 1px solid #5c5c5c !important;
    }
    .equal-btn button[data-baseweb="button"] {
        background-color: #0078FF !important;
        color: white !important;
    }
    .clear-btn button[data-baseweb="button"] {
        background-color: #E53935 !important;
    }
    h1 {
        text-align: center;
        color: #00BFFF;
        margin-bottom: 0px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>🧮 Casio 911EX</h1>", unsafe_allow_html=True)
st.caption("A modern, fully interactive Casio-style scientific calculator built with Streamlit")

# --- Session State ---
if "exp" not in st.session_state:
    st.session_state.exp = ""

# --- Button Press Logic ---
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

# --- Calculator UI ---
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
            btn_class = "equal-btn" if key == "=" else "clear-btn" if key == "C" else ""
            with cols[i]:
                st.markdown(f'<div class="{btn_class}">', unsafe_allow_html=True)
                st.button(key, on_click=press, args=(key,))
                st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.caption("✨ Designed by Ojas | Built with ❤️ in Streamlit")
