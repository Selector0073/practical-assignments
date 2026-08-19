import sys
from decimal import Decimal
import peewee
from db import init_db, db
from account_service import AccountService
from fill_data import fill_random_data



class RuntimeError(Exception):
    def __init__(self, message):
        print(message)
        sys.exit(1)



class Account:
    service = AccountService(db)

    @staticmethod
    def transaction():
        try:
            acc1 = int(sys.argv[2])
            acc2 = int(sys.argv[3])
            amount = round(Decimal(sys.argv[4]), 2)
        except IndexError:
            raise RuntimeError("Parameters acc1 id, acc2 id, amount needed")
        except (ValueError, TypeError):
            raise RuntimeError("acc1 and acc2 must be integer and amount must be float")

        try:
            Account.service.transfer(acc1, acc2, amount)
        except ValueError as exc:
            raise RuntimeError(str(exc))
        except peewee.DatabaseError:
            raise RuntimeError("Database operation failed")

    @staticmethod
    def status():
        print("Banking system — Selector0073")
        print(f"{'ID':<4} | {'Name':<12} | {'Balance':>8}")
        print("-" * 30)
        for row in Account.service.get_all_accounts():
            print(f"{row.id:<4} | {row.owner:<12} | {round(row.balance, 2):>8}")

    @staticmethod
    def get_balance():
        try:
            account_id = int(sys.argv[2])
        except IndexError:
            raise RuntimeError("Parameter id needed")
        except (ValueError, TypeError):
            raise RuntimeError("id must be integer")

        try:
            print(Account.service.get_balance(account_id))
        except ValueError as exc:
            raise RuntimeError(str(exc))

    @staticmethod
    def create_account():
        try:
            owner = sys.argv[2]
            balance = round(float(sys.argv[3]), 2)
        except IndexError:
            raise RuntimeError("Parameters owner and balance needed")
        except (ValueError, TypeError):
            raise RuntimeError("Balance must be float")

        try:
            account_id = Account.service.create_account(owner, balance)
        except peewee.IntegrityError:
            raise RuntimeError("This user already exists")

        print(f"User {owner} created (id={account_id})")


def main():
    dispatch = {
        "transaction": Account.transaction,
        "status": Account.status,
        "get": Account.get_balance,
        "create_account": Account.create_account,
        "fill-data": fill_random_data,
    }

    try:
        init_db()
    except peewee.DatabaseError:
        raise RuntimeError("Failed to initialize data base")

    try:
        dispatch[sys.argv[1]]()
    except IndexError:
        raise RuntimeError("Parameter needed (transaction, status, get, create_account, fill-data)")
    except KeyError:
        raise RuntimeError("Such parameter not found")


if __name__ == '__main__':
    main()
