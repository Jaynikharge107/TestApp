import streamlit as st
import math

# --- Streamlit Page Config ---
st.set_page_config(page_title="Scientific Calculator | Streamlit", page_icon="🧮", layout="centered")

# --- Custom Styling ---
st.markdown("""
    <style>
        /* Background */
        [data-testid="stAppViewContainer"] {
            background: radial-gradient(circle at top, #101820 0%, #0a0a0a 100%);
        }
        [data-testid="stHeader"], [data-testid="stToolbar"] {
            display: none;
        }

        /* Calculator Box */
        .calculator {
            width: 380px;
            margin: 60px auto;
            background-color: #1c1c1c;
            border: 2px solid #00FFF0;
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 0 25px #00FFF055;
        }

        /* Title */
        .title {
            text-align: center;
            color: #00FFF0;
            font-size: 26px;
            font-weight: 700;
            margin-bottom: 15px;
            text-shadow: 0px 0px 8px #00FFF0AA;
            font-family: 'Orbitron', sans-serif;
        }

        /* Display */
        .display-box {
            background: linear-gradient(180deg, #0f1e13, #1c2a20);
            color: #9CFF9C;
            border: 2px solid #00FFCC;
            border-radius: 8px;
            font-size: 26px;
            text-align: right;
            padding: 14px;
            margin-bottom: 20px;
            font-weight: bold;
            letter-spacing: 1.5px;
            box-shadow: inset 0 0 8px #00FFCC55;
            height: 50px;
        }

        /* Input box */
        input[type="text"] {
            background-color: transparent;
            border: none;
            color: #9CFF9C;
            width: 100%;
            height: 100%;
            font-size: 26px;
            outline: none;
            text-align: right;
            font-family: 'Courier New', monospace;
        }

        /* Buttons */
        .stButton>button {
            background-color: #111;
            color: #00FFD5;
            border: 1px solid #00FFD5;
            border-radius: 8px;
            font-size: 18px;
            height: 58px;
            width: 75px;
            margin: 5px;
            font-weight: bold;
            transition: all 0.15s ease-in-out;
        }

        .stButton>button:hover {
            background-color: #00FFD5;
            color: #111;
            transform: scale(1.05);
            box-shadow: 0 0 15px #00FFD5AA;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #00FFD599;
            font-size: 13px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Calculator UI Container ---
st.markdown("<div class='calculator'>", unsafe_allow_html=True)
st.markdown("<div class='title'>🧮 STREAMLIT SCIENTIFIC CALCULATOR</div>", unsafe_allow_html=True)

# --- Initialize Session State ---
if "expression" not in st.session_state:
    st.session_state.expression = ""

# --- Input Display ---
expression = st.text_input(
    label="",
    value=st.session_state.expression,
    key="input_box",
    placeholder="Enter expression (use keyboard or buttons)...",
)

# --- Update Expression ---
st.session_state.expression = expression

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
st.markdown("<div class='footer'>✨ Built with ❤️ in Streamlit | Perfect for LinkedIn showcase</div>", unsafe_allow_html=True)
