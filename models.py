import bcrypt

class Customer:
    def __init__(self, id, name, email, password_hash, profile_img):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
        self.profile_img = profile_img
        self.accounts = []

class BankAccount:
    def __init__(self, id, account_type, balance=0.0):
        self._balance = balance
        self.id = id
        self.type = account_type

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit must be positive.")
        self._balance += amount
        return self._balance

    def get_balance(self):
        return self._balance

class SavingsAccount(BankAccount):
    def __init__(self, id, balance=0.0):
        super().__init__(id, "Savings", balance)

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal must be positive.")
        if self._balance >= amount:
            self._balance -= amount
        else:
            raise ValueError("Insufficient funds.")
        return self._balance

class CheckingAccount(BankAccount):
    OVERDRAFT_LIMIT = 500.0

    def __init__(self, id, balance=0.0):
        super().__init__(id, "Checking", balance)

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal must be positive.")
        if self._balance + self.OVERDRAFT_LIMIT >= amount:
            self._balance -= amount
        else:
            raise ValueError("Withdrawal exceeds overdraft limit.")
        return self._balance