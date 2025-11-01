import streamlit as st
import math
import base64

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# --- Sound Effect (embedded base64 beep) ---
beep_sound = """
data:audio/wav;base64,UklGRigAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=
"""

# --- Custom Styling ---
st.markdown("""
    <style>
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(160deg, #f2f8f8 0%, #d7f0f0 100%);
        }
        [data-testid="stHeader"], [data-testid="stToolbar"] {display: none;}
        
        .calculator {
            width: 380px;
            margin: 50px auto;
            background-color: #ffffff;
            border: 2px solid #00a6a6;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 0 25px #00a6a655;
        }
        .title {
            text-align: center;
            color: #006d77;
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 10px;
            font-family: 'Orbitron', sans-serif;
        }
        .display-box {
            background: #e9f7f7;
            color: #004d40;
            border: 2px solid #00a6a6;
            border-radius: 8px;
            font-size: 26px;
            text-align: right;
            padding: 14px;
            margin-bottom: 20px;
            font-weight: bold;
            letter-spacing: 1.2px;
            box-shadow: inset 0 0 8px #00a6a655;
            height: 50px;
        }
        input[type="text"] {
            background-color: transparent;
            border: none;
            color: #004d40;
            width: 100%;
            height: 100%;
            font-size: 26px;
            outline: none;
            text-align: right;
            font-family: 'Courier New', monospace;
        }
        .stButton>button {
            background-color: #f4ffff;
            color: #007f7f;
            border: 1.5px solid #00a6a6;
            border-radius: 8px;
            font-size: 18px;
            height: 58px;
            width: 75px;
            margin: 5px;
            font-weight: bold;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #00a6a6;
            color: #ffffff;
            transform: scale(1.07);
            box-shadow: 0 0 10px #00a6a655;
        }
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #008b8b;
            font-size: 13px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Calculator Container ---
st.markdown("<div class='calculator'>", unsafe_allow_html=True)
st.markdown("<div class='title'>🧮 STREAMLIT SCIENTIFIC CALCULATOR</div>", unsafe_allow_html=True)

# --- Session State ---
if "expression" not in st.session_state:
    st.session_state.expression = ""

# --- Input Display (Keyboard Support) ---
expression = st.text_input(
    label="",
    value=st.session_state.expression,
    key="input_box",
    placeholder="Type here or use buttons...",
)

st.session_state.expression = expression

# --- Beep function ---
def play_beep():
    sound_html = f'<audio autoplay><source src="{beep_sound}" type="audio/wav"></audio>'
    st.markdown(sound_html, unsafe_allow_html=True)

# --- Button Layout ---
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
    ["sin", "cos", "tan", "sqrt"],
    ["log", "ln", "(", ")"],
    ["π", "x²", "C", "DEL"]
]

for row in buttons:
    cols = st.columns(4)
    for i, key in enumerate(row):
        if cols[i].button(key):
            play_beep()  # play click sound
            if key == "C":
                st.session_state.expression = ""
            elif key == "DEL":
                st.session_state.expression = st.session_state.expression[:-1]
            elif key == "=":
                try:
                    expr = st.session_state.expression.replace("π", str(math.pi))
                    expr = expr.replace("^", "**")
                    expr = expr.replace("x²", "**2")
                    expr = expr.replace("sin", "math.sin")
                    expr = expr.replace("cos", "math.cos")
                    expr = expr.replace("tan", "math.tan")
                    expr = expr.replace("sqrt", "math.sqrt")
                    expr = expr.replace("log", "math.log10")
                    expr = expr.replace("ln", "math.log")

                    result = eval(expr)
                    st.session_state.expression = str(round(result, 6))
                except Exception:
                    st.session_state.expression = "Error"
            elif key == "x²":
                st.session_state.expression += "**2"
            else:
                st.session_state.expression += key

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("<div class='footer'>✨ Built with ❤️ using Streamlit | Ideal for LinkedIn & GitHub Showcase</div>", unsafe_allow_html=True)
