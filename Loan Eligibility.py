import streamlit as st
import pandas as pd

st.set_page_config(page_title="Loan Eligibility App", page_icon="💰", layout="centered")

st.title("💰 Loan Eligibility & Savings Analyzer")
st.write("Check your monthly savings, loan eligibility & EMI based on your financial details.")

# Reset button
if st.button("🔄 Reset All Data"):
    st.session_state.expenses = []
    st.experimental_rerun()

# Income input
Income = st.number_input("💵 Monthly Income (In-Hand)", min_value=0, step=500)

# Initialize session storage
if "expenses" not in st.session_state:
    st.session_state.expenses = []

st.subheader("💸 Add Your Monthly Expenses")

# Multiple expenses at once
expense_batch = st.text_input("Enter expenses separated by commas (e.g., 500,1500,800)")

if st.button("➕ Add Expenses"):
    try:
        items = [int(x.strip()) for x in expense_batch.split(",") if x.strip().isdigit()]
        if items:
            st.session_state.expenses.extend(items)
            st.success(f"Added {len(items)} expenses")
        else:
            st.error("Enter valid numbers only.")
    except:
        st.error("Invalid format. Use commas between numbers.")

# Show expenses
if st.session_state.expenses:
    st.write("✅ **Expenses Entered:**", st.session_state.expenses)
    Total_exp = sum(st.session_state.expenses)
    Savings = Income - Total_exp
    remaining_percent = (Savings / Income) * 100 if Income > 0 else 0

    st.subheader("📊 Financial Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Expense", f"₹{Total_exp}")
    with col2:
        st.metric("Monthly Savings", f"₹{Savings}")

    st.write(f"✅ **You save:** {remaining_percent:.2f}% of your income")

    # Chart
    data = pd.DataFrame({
        "Category": ["Expenses", "Savings"],
        "Amount (₹)": [Total_exp, max(Savings, 0)]
    }).set_index("Category")

    st.subheader("📈 Expense vs Savings")
    st.bar_chart(data)

    # Motivational / Helpful Messages
    st.subheader("💡 Savings Advice")
    if remaining_percent > 80:
        st.success("🔥 Amazing! You save over 80%. Excellent financial discipline!")
    elif 60 <= remaining_percent <= 80:
        st.success("✅ Very good! You have strong savings habits.")
    elif 40 <= remaining_percent < 60:
        st.warning("🙂 Decent savings. Try reducing small expenses to increase it.")
    else:
        st.error("⚠️ Savings are low.")
        st.write("""
        ✅ Track daily spending  
        ✅ Avoid non-essential purchases  
        ✅ Use a monthly budget  
        ✅ Try 20-30% automatic saving system  
        """)

    # Loan eligibility
    st.subheader("📌 Loan Eligibility Status")
    if remaining_percent <= 40:
        st.error("❌ Not Eligible for loan")
    else:
        st.success("✅ Eligible for Loan")

        # Loan amount based on savings %
        if 40 < remaining_percent <= 60:
            loan_amount = 40000
        elif 60 < remaining_percent <= 80:
            loan_amount = 80000
        else:
            loan_amount = 150000

        # Tenure Slider
        tenure = st.slider("⏳ Select Loan Tenure (Months)", 6, 36, 12)

        # Interest rate adjustment based on tenure
        if tenure <= 12:
            interest = 10
        elif 12 < tenure <= 24:
            interest = 11
        else:
            interest = 12

        monthly_int_rate = interest / 100 / 12
        Emi = loan_amount * monthly_int_rate * ((1 + monthly_int_rate)**tenure) / ((1 + monthly_int_rate)**tenure - 1)

        st.subheader("✅ Loan Details")
        st.write(f"💵 **Approved Loan Amount:** ₹{loan_amount}")
        st.write(f"📈 **Interest Rate:** {interest}%")
        st.write(f"⏳ **Tenure:** {tenure} Months")
        st.write(f"🧾 **Estimated EMI:** ₹{round(Emi)} per month")

else:
    st.info("Enter your monthly expenses above to begin.")
