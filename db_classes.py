from models import Customer, SavingsAccount, CheckingAccount

class CustomerDB:
    def __init__(self, connection):
        self.connection = connection

    def create_customer(self, name, email, password_hash, profile_img):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO customers (name, email, password_hash, profile_img)
                VALUES (%s, %s, %s, %s)
            """, (name, email, password_hash, profile_img))
            self.connection.commit()
            return cursor.lastrowid

    def get_customer_by_email(self, email):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customers WHERE email = %s", (email,))
            result = cursor.fetchone()
            if result:
                return Customer(**result)
            return None

class AccountDB:
    def __init__(self, connection):
        self.connection = connection

    def create_account(self, customer_id, account_type, balance):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO accounts (customer_id, type, balance)
                VALUES (%s, %s, %s)
            """, (customer_id, account_type, balance))
            self.connection.commit()
            return cursor.lastrowid

    def get_accounts_by_customer(self, customer_id):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM accounts WHERE customer_id = %s", (customer_id,))
            results = cursor.fetchall()
            accounts = []
            for row in results:
                if row['type'] == 'Savings':
                    acc = SavingsAccount(row['id'], float(row['balance']))
                else:
                    acc = CheckingAccount(row['id'], float(row['balance']))
                accounts.append(acc)
            return accounts

class TransactionDB:
    def __init__(self, connection):
        self.connection = connection

    def create_transaction(self, account_id, type, amount):
        with self.connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO transactions (account_id, type, amount)
                VALUES (%s, %s, %s)
            """, (account_id, type, amount))
            self.connection.commit()

    def get_transactions_by_account(self, account_id):
        with self.connection.cursor() as cursor:
            cursor.execute("SELECT * FROM transactions WHERE account_id = %s", (account_id,))
            return cursor.fetchall()
