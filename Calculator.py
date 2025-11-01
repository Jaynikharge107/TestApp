
import streamlit as st

# --- App Title ---
st.set_page_config(page_title="Normal Calculator", page_icon="🧮", layout="centered")
st.title("🧮 Normal Calculator")
st.write("A simple and interactive calculator built using Streamlit!")

# --- User Inputs ---
st.subheader("Enter Numbers")

num1 = st.number_input("Enter first number", value=0.0, step=1.0)
num2 = st.number_input("Enter second number", value=0.0, step=1.0)

# --- Operation Selection ---
operation = st.selectbox(
    "Select an operation",
    ("Addition (+)", "Subtraction (-)", "Multiplication (×)", "Division (÷)")
)

# --- Calculate Button ---
if st.button("Calculate"):
    if operation == "Addition (+)":
        result = num1 + num2
        st.success(f"✅ Result: {num1} + {num2} = {result}")

    elif operation == "Subtraction (-)":
        result = num1 - num2
        st.success(f"✅ Result: {num1} - {num2} = {result}")

    elif operation == "Multiplication (×)":
        result = num1 * num2
        st.success(f"✅ Result: {num1} × {num2} = {result}")

    elif operation == "Division (÷)":
        if num2 == 0:
            st.error("❌ Cannot divide by zero!")
        else:
            result = num1 / num2
            st.success(f"✅ Result: {num1} ÷ {num2} = {result}")

# --- Footer ---
st.caption("Created with ❤️ using Streamlit")
