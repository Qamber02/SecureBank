import bcrypt
from typing import List
from uuid import uuid4


class Customer:
    def __init__(self, name: str, email: str, password: str, profile_img: str = None):
        self.id = str(uuid4())
        self.name = name
        self.email = self._validate_email(email)
        self.password_hash = self._hash_password(password)
        self.profile_img = profile_img
        self.accounts: List[BankAccount] = []

    def _hash_password(self, password: str) -> bytes:
        if not password:
            raise ValueError("Password cannot be empty.")
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash)

    def _validate_email(self, email: str) -> str:
        if "@" not in email:
            raise ValueError("Invalid email address.")
        return email

    def add_account(self, account: "BankAccount"):
        self.accounts.append(account)


class BankAccount:
    def __init__(self, account_type: str, balance: float = 0.0):
        self.id = str(uuid4())
        self.type = account_type
        self._balance = self._validate_amount(balance)

    def _validate_amount(self, amount: float) -> float:
        if amount < 0:
            raise ValueError("Amount cannot be negative.")
        return amount

    def deposit(self, amount: float) -> float:
        amount = self._validate_amount(amount)
        self._balance += amount
        return self._balance

    def get_balance(self) -> float:
        return self._balance

    def _can_withdraw(self, amount: float) -> bool:
        raise NotImplementedError("Withdrawal logic must be implemented.")


class SavingsAccount(BankAccount):
    def __init__(self, balance: float = 0.0):
        super().__init__("Savings", balance)

    def withdraw(self, amount: float) -> float:
        amount = self._validate_amount(amount)

        if self._balance < amount:
            raise ValueError("Insufficient funds.")

        self._balance -= amount
        return self._balance


class CheckingAccount(BankAccount):
    OVERDRAFT_LIMIT = 500.0

    def __init__(self, balance: float = 0.0):
        super().__init__("Checking", balance)

    def withdraw(self, amount: float) -> float:
        amount = self._validate_amount(amount)

        if self._balance + self.OVERDRAFT_LIMIT < amount:
            raise ValueError("Exceeds overdraft limit.")

        self._balance -= amount
        return self._balance