import streamlit as st
import database
import re
import bcrypt
import os
from models import Customer
from db_classes import CustomerDB, AccountDB, TransactionDB

# --- CONFIG & STYLING ---
st.set_page_config(page_title="SecureBank", page_icon="💼", layout="centered")

def apply_custom_css():
    st.markdown("""
    <style>
        .main { background-color: #f8f9fa; }
        .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
        .stTabs [data-baseweb="tab-list"] { gap: 24px; }
        .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- DB INITIALIZATION ---
@st.cache_resource
def get_db_connections():
    database.create_tables()
    conn = database.create_connection()
    return conn, CustomerDB(conn), AccountDB(conn), TransactionDB(conn)

conn, customer_db, account_db, transaction_db = get_db_connections()

# --- UTILS ---
def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def validate_inputs(email, password, confirm=None):
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        return False, "Invalid email format."
    if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$', password):
        return False, "Password must be 8+ characters with letters & numbers."
    if confirm is not None and password != confirm:
        return False, "Passwords do not match."
    return True, ""

# --- PAGE FUNCTIONS ---
def register_page():
    st.header("📝 Create Account")
    with st.form("registration_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        profile_img = st.file_uploader("Profile Picture", type=["png", "jpg"])
        submit = st.form_submit_button("Register")

        if submit:
            is_valid, msg = validate_inputs(email, password, confirm)
            if not is_valid:
                st.error(msg)
            else:
                img_path = "images/default.png"
                if profile_img:
                    if not os.path.exists("images"): os.makedirs("images")
                    img_path = f"images/{email}_{profile_img.name}"
                    with open(img_path, "wb") as f:
                        f.write(profile_img.getbuffer())
                
                try:
                    customer_db.create_customer(name, email, hash_password(password), img_path)
                    st.success("Account created! Please login.")
                except Exception as e:
                    st.error(f"Error: {e}")

def login_page():
    st.header("🔐 Member Login")
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")

        if submit:
            customer = customer_db.get_customer_by_email(email)
            if customer and check_password(password, customer.password_hash):
                st.session_state.logged_in = True
                st.session_state.customer = customer
                st.rerun() # Refresh to show dashboard
            else:
                st.error("Invalid email or password.")

def dashboard():
    user = st.session_state.customer
    
    # Sidebar Profile
    with st.sidebar:
        st.image(user.profile_img, width=100)
        st.title(f"Hello, {user.name.split()[0]}!")
        if st.button("Log Out"):
            st.session_state.logged_in = False
            st.session_state.customer = None
            st.rerun()

    tab1, tab2, tab3 = st.tabs(["💰 Accounts", "💸 Transfer", "📜 History"])

    with tab1:
        st.subheader("Your Accounts")
        accounts = account_db.get_accounts_by_customer(user.id)
        if accounts:
            for acc in accounts:
                with st.expander(f"{acc.account_type} - {acc.id}"):
                    st.metric("Balance", f"${acc.balance:,.2f}")
        else:
            st.info("You don't have any accounts yet.")
        
        with st.popover("Open New Account"):
            acc_type = st.selectbox("Type", ["Savings", "Checking"], key="new_acc_type")
            init_bal = st.number_input("Initial Deposit", min_value=0.0)
            if st.button("Create Account"):
                account_db.create_account(user.id, acc_type, init_bal)
                st.success("Account opened!")
                st.rerun()

    with tab2:
        st.subheader("Transaction")
        accounts = account_db.get_accounts_by_customer(user.id)
        if accounts:
            acc_options = {f"{a.account_type} (***{str(a.id)[-4:]})": a for a in accounts}
            selected_label = st.selectbox("Select Account", options=list(acc_options.keys()))
            selected_acc = acc_options[selected_label]
            
            col1, col2 = st.columns(2)
            action = col1.radio("Action", ["Deposit", "Withdraw"])
            amount = col2.number_input("Amount ($)", min_value=0.01, step=10.0)
            
            if st.button("Execute Transaction"):
                try:
                    new_balance = selected_acc.deposit(amount) if action == "Deposit" else selected_acc.withdraw(amount)
                    
                    # NOTE: Move this update logic into account_db.update_balance()
                    account_db.update_balance(selected_acc.id, new_balance)
                    transaction_db.create_transaction(selected_acc.id, action, amount)
                    
                    st.success(f"Success! New balance: ${new_balance:,.2f}")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        else:
            st.warning("Create an account to start banking.")

    with tab3:
        st.subheader("Recent Activity")
        # Fetch and display transactions in a clean table/dataframe
        # ... (Implementation of transaction history)

# --- MAIN APP FLOW ---
def main():
    apply_custom_css()
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        page = st.sidebar.radio("Navigation", ["Login", "Register"])
        if page == "Login": login_page()
        else: register_page()
    else:
        dashboard()

if __name__ == "__main__":
    main()
