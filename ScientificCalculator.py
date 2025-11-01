import streamlit as st
import math

# --- Page setup ---
st.set_page_config(page_title="Retro Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom Retro CSS ---
st.markdown("""
    <style>
        body {
            background-color: #1e1e1e;
            color: #00FFCC;
            font-family: 'Courier New', monospace;
        }

        .calculator {
            width: 320px;
            margin: 50px auto;
            background-color: #2c2c2c;
            border: 3px solid #00FFCC;
            border-radius: 15px;
            padding: 15px;
            box-shadow: 0 0 30px #00FFCC66;
        }

        .display {
            background-color: #0d0d0d;
            color: #00FF66;
            border: 2px solid #00FFCC;
            border-radius: 5px;
            font-size: 28px;
            text-align: right;
            padding: 10px;
            margin-bottom: 20px;
            font-weight: bold;
            letter-spacing: 2px;
        }

        .stButton>button {
            background-color: #111;
            color: #00FFCC;
            border: 1px solid #00FFCC;
            border-radius: 8px;
            font-size: 18px;
            height: 55px;
            width: 70px;
            margin: 4px;
            font-weight: bold;
            transition: all 0.2s ease-in-out;
        }

        .stButton>button:hover {
            background-color: #00FFCC;
            color: #111;
            transform: scale(1.05);
        }

        .title {
            text-align: center;
            color: #00FFCC;
            font-size: 28px;
            font-weight: bold;
            margin-bottom: 10px;
            text-shadow: 0px 0px 10px #00FFCC;
        }
    </style>
""", unsafe_allow_html=True)

# --- Calculator UI ---
st.markdown("<div class='calculator'>", unsafe_allow_html=True)
st.markdown("<div class='title'>🧮 RETRO CALCULATOR</div>", unsafe_allow_html=True)

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
st.caption("👾 Inspired by retro Casio fx-911 | Built with ❤️ using Streamlit")
