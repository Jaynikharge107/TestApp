import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(page_title="Loan Eligibility App", page_icon="💰")

st.title("💰 Loan Eligibility & Savings Analyzer")
st.write("Enter your monthly income and expenses to check eligibility and get savings advice.")

# --- RESET BUTTON ---
if st.button("🔄 Reset Data"):
    st.session_state.expenses = []
    st.success("Data reset!")
    st.experimental_rerun()

# --- INCOME INPUT ---
Income = st.number_input("💵 Monthly Income (In-Hand)", min_value=0, step=1000)

# --- EXPENSE INPUT ---
if "expenses" not in st.session_state:
    st.session_state.expenses = []

expense = st.text_input("💸 Enter an expense and press Enter")

if expense:
    if expense.isdigit():
        st.session_state.expenses.append(int(expense))
        st.success(f"✅ Added ₹{expense}")
    else:
        st.error("❗ Expense must be a number")

# --- DISPLAY EXPENSES ---
if st.session_state.expenses:
    st.subheader("📌 Expense Summary")
    st.write("✅ **All Expenses:**", st.session_state.expenses)

    Total_exp = sum(st.session_state.expenses)
    st.write("💸 **Total Expense:** ₹", Total_exp)

    if Income > 0:
        Savings = Income - Total_exp
        remaining_percent = (Savings / Income) * 100

        st.write(f"📊 **Savings:** ₹{Savings}")
        st.write(f"✅ **% of Salary Saved:** {remaining_percent:.2f}%")

        # ---- PIE CHART ----
        fig, ax = plt.subplots()
        values = [Total_exp, Savings]
        labels = ["Expenses", "Savings"]
        ax.pie(values, labels=labels, autopct="%1.1f%%")
        ax.set_title("Savings vs Expense Split")
        st.pyplot(fig)

        # ---- SAVINGS QUOTE ----
        st.subheader("💡 Savings Advice")
        if remaining_percent > 80:
            st.success("🔥 Awesome! You're saving more than 80% — Excellent financial discipline! 🚀")
        elif 60 <= remaining_percent <= 80:
            st.success("✅ Good job! Savings are strong. You're on a great path! 💪")
        elif 40 <= remaining_percent < 60:
            st.warning("🙂 You're doing okay. Try reducing small unnecessary expenses to improve savings.")
        else:
            st.error("⚠️ Savings are low. Try these tips:")
            st.write("""
            ✅ Track daily expenses  
            ✅ Cut down luxury spending  
            ✅ Only buy what’s required  
            ✅ Set monthly saving targets  
            """)

        # ---- LOAN ELIGIBILITY ----
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

            st.write("💵 **Approved Loan Amount:** ₹", loan_amount)
            st.write("📈 **Interest Rate:**", interest, "%")
            st.write("⏳ **Tenure:**", tenure, "Months")
            st.write(f"🧾 **Monthly EMI:** ₹{round(Emi)}")

else:
    st.info("Add expenses above. Type a number and press Enter.")
