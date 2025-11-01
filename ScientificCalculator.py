import streamlit as st
import math

# --- Page Config ---
st.set_page_config(page_title="Scientific Calculator", page_icon="🧮", layout="centered")

# --- Custom CSS for Casio look ---
st.markdown("""
    <style>
    .stApp {
        background-color: #1a1a1a;
        color: white;
        text-align: center;
    }
    .main {
        background-color: #1a1a1a;
    }
    .stNumberInput, .stSelectbox, .stButton button {
        font-size: 18px !important;
    }
    .stButton button {
        background-color: #4b4b4b;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
    }
    .stButton button:hover {
        background-color: #2e2e2e;
    }
    .display {
        background-color: #e6e6e6;
        color: black;
        font-size: 24px;
        border-radius: 6px;
        padding: 10px;
        margin-bottom: 20px;
        font-family: 'Courier New', monospace;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧮 Scientific Calculator")
st.caption("Casio-style scientific calculator built using Streamlit")

# --- Input Section ---
expression = st.text_input("Enter expression", value="", placeholder="e.g. sin(30) + log(10) * 3")

# --- Compute ---
if st.button("Calculate"):
    try:
        # Allow math functions
        allowed_names = {k: v for k, v in math.__dict__.items()}
        allowed_names["pi"] = math.pi
        allowed_names["e"] = math.e

        # Convert degrees to radians for trig functions
        def deg_sin(x): return math.sin(math.radians(x))
        def deg_cos(x): return math.cos(math.radians(x))
        def deg_tan(x): return math.tan(math.radians(x))

        allowed_names.update({
            "sin": deg_sin,
            "cos": deg_cos,
            "tan": deg_tan,
            "sqrt": math.sqrt,
            "log": math.log10,
            "ln": math.log,
            "abs": abs,
            "pow": pow,
        })

        result = eval(expression, {"__builtins__": {}}, allowed_names)
        st.markdown(f"<div class='display'>= {result}</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")

# --- Function Help ---
with st.expander("📘 Supported Functions"):
    st.markdown("""
    - `sin(x)`, `cos(x)`, `tan(x)` → (angle in degrees)  
    - `log(x)` → log base 10  
    - `ln(x)` → natural log (base e)  
    - `sqrt(x)` → square root  
    - `pow(a,b)` → a raised to b  
    - Constants: `pi`, `e`  
    - You can use parentheses and basic operators `+ - * /`
    """)

st.caption("Made with ❤️ by Ojas | Powered by Streamlit")
