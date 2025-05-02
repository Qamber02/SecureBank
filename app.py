import streamlit as st
import database
import re
import bcrypt
from models import Customer
from db_classes import CustomerDB, AccountDB, TransactionDB

# Page Config
st.set_page_config(
    page_title="SecureBank App",
    page_icon="💼",
    layout="centered",
    initial_sidebar_state="auto"
)

# Global CSS Styling
st.markdown("""
<style>
    html, body {
        font-family: 'Segoe UI', sans-serif;
        background-color: #f5f7fa;
    }
    .block-container {
        padding-top: 2rem;
    }
    .stButton>button {
        background-color: #004080;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        margin-top: 1rem;
    }
    .stButton>button:hover {
        background-color: #00264d;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: 500;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
database.create_tables()
conn = database.create_connection()
customer_db = CustomerDB(conn)
account_db = AccountDB(conn)
transaction_db = TransactionDB(conn)

# Session State
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'customer' not in st.session_state:
    st.session_state.customer = None

# Helper Functions
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def validate_email(email):
    return re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email)

def validate_password(password):
    return re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password)

# Pages
def register_page():
    with st.container():
        st.header("📝 Register")
        name = st.text_input("Name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        profile_img = st.file_uploader("Upload Profile Picture", type=["png", "jpg", "jpeg"])

        if st.button("Register"):
            if not name or not email or not password or not confirm:
                st.error("All fields are required.")
                return
            if not validate_email(email):
                st.error("Invalid email format.")
                return
            if not validate_password(password):
                st.error("Password must be at least 8 characters with letters and digits.")
                return
            if password != confirm:
                st.error("Passwords do not match.")
                return
            img_path = "images/default.png"
            if profile_img:
                img_path = f"images/{profile_img.name}"
                with open(img_path, "wb") as f:
                    f.write(profile_img.read())
            hashed = hash_password(password)
            try:
                customer_db.create_customer(name, email, hashed, img_path)
                st.success("Registration successful.")
            except Exception as e:
                st.error(f"Registration failed: {e}")

def login_page():
    with st.container():
        st.header("🔐 Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            customer = customer_db.get_customer_by_email(email)
            if customer and check_password(password, customer.password_hash):
                st.session_state.logged_in = True
                st.session_state.customer = customer
                st.success("Logged in successfully.")
            else:
                st.error("Invalid credentials.")

def dashboard():
    customer = st.session_state.customer
    st.image(customer.profile_img, caption="Profile Picture", width=100)
    st.markdown(f"## 👋 Welcome, **{customer.name}**")

    tab1, tab2, tab3 = st.tabs(["Create Account", "Deposit/Withdraw", "Transactions"])

    with tab1:
        st.subheader("Create New Account")
        account_type = st.selectbox("Type", ["Savings", "Checking"])
        balance = st.number_input("Initial Balance", min_value=0.0, step=100.0)
        if st.button("Create"):
            try:
                account_db.create_account(customer.id, account_type, balance)
                st.success(f"{account_type} account created.")
            except Exception as e:
                st.error(f"Creation failed: {e}")

    with tab2:
        st.subheader("Deposit or Withdraw")
        accounts = account_db.get_accounts_by_customer(customer.id)
        if not accounts:
            st.info("Create an account first.")
        else:
            account_map = {acc.id: acc for acc in accounts}
            selected = st.selectbox("Account", list(account_map.keys()))
            account = account_map[selected]
            action = st.radio("Action", ["Deposit", "Withdraw"])
            amount = st.number_input("Amount", min_value=0.0, step=10.0)
            if st.button("Submit"):
                try:
                    if action == "Deposit":
                        new_balance = account.deposit(amount)
                    else:
                        new_balance = account.withdraw(amount)
                    with conn.cursor() as cur:
                        cur.execute("UPDATE accounts SET balance = %s WHERE id = %s", (new_balance, account.id))
                        conn.commit()
                    transaction_db.create_transaction(account.id, action, amount)
                    st.success(f"New balance: ${new_balance:.2f}")
                except Exception as e:
                    st.error(f"Error: {e}")

    with tab3:
        st.subheader("Transaction History")
        accounts = account_db.get_accounts_by_customer(customer.id)
        if not accounts:
            st.info("No accounts yet.")
        else:
            account_ids = [acc.id for acc in accounts]
            selected_id = st.selectbox("Select Account", account_ids)
            txs = transaction_db.get_transactions_by_account(selected_id)
            if txs:
                for tx in txs:
                    st.write(f"{tx['timestamp']} - {tx['type']}: ${tx['amount']:.2f}")
            else:
                st.info("No transactions.")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.customer = None

# Main App Flow
if not st.session_state.logged_in:
    page = st.sidebar.selectbox("Page", ["Login", "Register"])
    if page == "Login":
        login_page()
    else:
        register_page()
else:
    dashboard()
