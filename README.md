# SecureBank

SecureBank is a lightweight, modular web banking application built with [Streamlit](https://streamlit.io/) and backed by a MySQL database. It allows users to register, log in securely, and manage checking or savings accounts with real-time updates.

---

##  Features

-  Secure user authentication with bcrypt password hashing
- Checking & savings account logic with overdraft/sufficient funds validation
- 📊 Streamlit-based UI for login, registration, and dashboard
- 🗃️ Modular database layer with PyMySQL
- 🧪 Unit tests using Pytest
- 📁 Clean folder structure for easy scaling & maintenance

---

## 🛠️ Project Structure

```
securebank/
├── app.py              # Streamlit entry point
├── database.py         # DB connection + schema creation
├── db_classes.py       # CRUD wrappers for customers, accounts, transactions
├── models.py           # Business logic: CheckingAccount, SavingsAccount
├── utils.py            # Password hashing and verification
├── tests/              # Pytest-based test cases
├── images/             # App assets (icons, logos, etc.)
├── requirements.txt    # Python dependencies
├── README.md           # Project overview
└── .gitignore
```

---

## ⚙️ Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/Qamber02/SecureBank.git
cd SecureBank
```

### 2. Set up a virtual environment (optional but recommended)
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure your MySQL database

Create a database named `securebank` and update the credentials in `database.py`:
```python
DB_CONFIG = {
    "host": "localhost",
    "user": "your_username",
    "password": "your_password",
    "db": "securebank"
}
```

### 5. Initialize the database
```bash
python -c "from database import create_tables; create_tables()"
```

### 6. Run the app
```bash
streamlit run app.py
```

---

## 🧪 Running Tests
```bash
pytest
```

---

## 📌 TODOs
- [ ] Add user profile image uploads
- [ ] Implement deposit/withdraw UI
- [ ] Add transaction filtering and charts
- [ ] Connect to external APIs (e.g. currency rates)

---

## 📄 License
This project is open-source and licensed under the MIT License.

---

## 🤝 Contributing
Pull requests are welcome! For major changes, open an issue first to discuss what you'd like to add or modify.

---

## 👨‍💻 Author
**[@Qamber02](https://github.com/Qamber02)** — Feel free to reach out with suggestions or collaboration ideas.
