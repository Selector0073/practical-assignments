from decimal import Decimal
import peewee
from db import Money


class AccountService:
    def __init__(self, connection):
        self.connection = connection

    def create_account(self, owner, balance: Decimal | float | int = 0):
        account = Money.create(owner=owner, balance=Decimal(balance))
        return account.id

    def get_balance(self, account_id):
        account = self.get_account(account_id)
        return account.balance

    def transfer(self, from_id, to_id, amount):
        amount = Decimal(amount)
        if amount <= 0:
            raise ValueError("Transfer amount must be greater than 0")

        with self.connection.atomic():
            from_account = self.get_account(from_id)
            to_account = self.get_account(to_id)

            if from_account.balance < amount:
                raise ValueError("Insufficient funds for the transfer")

            from_account.balance -= amount
            to_account.balance += amount
            from_account.save()
            to_account.save()

    def get_all_accounts(self):
        return list(Money.select().order_by(Money.id))

    def get_account(self, account_id):
        try:
            return Money.get(Money.id == account_id)
        except peewee.DoesNotExist:
            raise ValueError(f"Account {account_id} does not exist")
