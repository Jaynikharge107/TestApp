import streamlit as st
import math

# --- Page setup ---
st.set_page_config(page_title="Retro Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom Retro CSS ---
st.markdown("""
    <style>
        /* Background */
        [data-testid="stAppViewContainer"] {
            background-color: #121212;
        }
        [data-testid="stHeader"] {
            background: none;
        }
        [data-testid="stToolbar"] {
            display: none;
        }

        /* Main calculator box */
        .calculator {
            width: 340px;
            margin: 40px auto;
            background-color: #1a1a1a;
            border: 3px solid #00FFF0;
            border-radius: 18px;
            padding: 15px;
            box-shadow: 0 0 25px #00FFF033;
        }

        /* Title */
        .title {
            text-align: center;
            color: #00FFF0;
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 15px;
            letter-spacing: 1px;
            text-shadow: 0px 0px 12px #00FFFF, 0px 0px 20px #00FFFF66;
            font-family: 'Courier New', monospace;
        }

        /* Display */
        .display {
            background: linear-gradient(180deg, #0f1e13, #1c2a20);
            color: #9CFF9C;
            border: 2px solid #00FFCC;
            border-radius: 6px;
            font-size: 28px;
            text-align: right;
            padding: 12px;
            margin-bottom: 20px;
            font-weight: bold;
            letter-spacing: 1.5px;
            box-shadow: inset 0 0 8px #00FFCC55;
        }

        /* Buttons */
        .stButton>button {
            background-color: #111;
            color: #00FFD5;
            border: 1px solid #00FFD5;
            border-radius: 10px;
            font-size: 18px;
            height: 58px;
            width: 75px;
            margin: 5px;
            font-weight: bold;
            font-family: 'Courier New', monospace;
            transition: all 0.15s ease-in-out;
        }

        .stButton>button:hover {
            background-color: #00FFD5;
            color: #111;
            transform: scale(1.07);
            box-shadow: 0 0 15px #00FFD5AA;
        }

        /* Footer */
        .footer {
            text-align: center;
            margin-top: 20px;
            color: #00FFD5AA;
            font-size: 13px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Calculator UI ---
st.markdown("<div class='calculator'>", unsafe_allow_html=True)
st.markdown("<div class='title'>🧮 RETRO CASIO CALCULATOR</div>", unsafe_allow_html=True)

# --- Display Area ---
if "expression" not in st.session_state:
    st.session_state.expression = ""

display = st.session_state.expression if st.session_state.expression else "0"
st.markdown(f"<div class='display'>{display}</div>", unsafe_allow_html=True)

# --- Button Layout ---
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
    ["sin", "cos", "tan", "sqrt"],
    ["log", "ln", "(", ")"],
    ["C", "DEL", "π", "x²"]
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
st.markdown("<div class='footer'>👾 Inspired by Casio fx-911 | Built with ❤️ using Streamlit</div>", unsafe_allow_html=True)
