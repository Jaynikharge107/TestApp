import streamlit as st
import pandas as pd

st.set_page_config(page_title="Loan Eligibility App", page_icon="💰")

st.title("💰 Loan Eligibility & Savings Analyzer")
st.write("Enter your monthly income and expenses to check eligibility and get savings advice.")

# RESET
if st.button("🔄 Reset Data"):
    st.session_state.expenses = []
    st.success("Data reset!")
    st.experimental_rerun()

Income = st.number_input("💵 Monthly Income (In-Hand)", min_value=0, step=1000)

if "expenses" not in st.session_state:
    st.session_state.expenses = []

expense = st.text_input("💸 Enter an expense and press Enter")

if expense:
    if expense.isdigit():
        st.session_state.expenses.append(int(expense))
        st.success(f"✅ Added ₹{expense}")
    else:
        st.error("❗ Expense must be a number")

if st.session_state.expenses:
    st.subheader("📌 Expense Summary")
    Total_exp = sum(st.session_state.expenses)
    Savings = Income - Total_exp
    remaining_percent = (Savings / Income) * 100 if Income > 0 else 0

    st.write("✅ All Expenses:", st.session_state.expenses)
    st.write("💸 Total Expense: ₹", Total_exp)
    st.write("📊 Savings: ₹", Savings)
    st.write(f"✅ % Saved: {remaining_percent:.2f}%")

    # ✅ Streamlit Chart Instead of Matplotlib
    data = pd.DataFrame({
        "Category": ["Expenses", "Savings"],
        "Amount": [Total_exp, Savings]
    })
    
    st.subheader("📊 Savings vs Expenses")
    st.bar_chart(data.set_index("Category"))

    # ✅ Motivational Messages
    st.subheader("💡 Savings Advice")
    if remaining_percent > 80:
        st.success("🔥 Amazing! You're saving more than 80%. Excellent financial control! 🚀")
    elif 60 <= remaining_percent <= 80:
        st.success("✅ Good savings! You're on a strong path! 💪")
    elif 40 <= remaining_percent < 60:
        st.warning("🙂 Doing okay. Reduce small unnecessary spending for better savings.")
    else:
        st.error("⚠️ Savings are low. Tips:")
        st.write("""
        ✅ Track daily expenses  
        ✅ Cut luxury spending  
        ✅ Purchase only needs  
        ✅ Set saving targets  
        """)

    # ✅ Loan Eligibility
    st.subheader("📌 Loan Eligibility Result")
    if remaining_percent <= 40:
        st.error("❌ Loan Status: Not Eligible")
    else:
        st.success("✅ Loan Status: Eligible")

        if 40 < remaining_percent <= 60:
            loan_amount = 40000
            interest = 12
        elif 60 < remaining_percent <= 80:
            loan_amount = 80000
            interest = 11
        else:
            loan_amount = 150000
            interest = 10

        tenure = st.slider("⏳ Choose Loan Tenure (Months)", 6, 36, value=12)

        monthly_int_rate = interest / 100 / 12
        Emi = loan_amount * monthly_int_rate * ((1 + monthly_int_rate) ** tenure) / \
              ((1 + monthly_int_rate) ** tenure - 1)

        st.write("💵 Approved Loan Amount: ₹", loan_amount)
        st.write("📈 Interest Rate:", interest, "%")
        st.write("⏳ Tenure:", tenure, "Months")
        st.write(f"🧾 EMI Per Month: ₹{round(Emi)}")

else:
    st.info("Add expenses above. Type a number and press Enter.")
