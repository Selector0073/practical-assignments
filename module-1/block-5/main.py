from db import init_db, DataBase
from fill_data import fill_random_data
import sys, os
import peewee
from dotenv import load_dotenv
from decimal import Decimal

class RuntimeError(Exception):
    def __init__(self, message):
        print(message)
        sys.exit(1)

# ---

class Account:
    @staticmethod
    def transaction():
        try:
            acc1 = int(sys.argv[2])
            acc2 = int(sys.argv[3])
            almount = round(Decimal(sys.argv[4]), 2)
        except IndexError:
            raise RuntimeError("Parameters acc1 id, acc2 id, almount needed")
        except (ValueError, TypeError):
            raise RuntimeError("acc1 and acc2 must be integer and almount must be float")

        try:
            DataBase.transaction(acc1, acc2, almount)
        except peewee.DoesNotExist:
            raise RuntimeError("Accounts does not exist")
        except peewee.IntegrityError:
            raise RuntimeError("almount must be >0.0")

    @staticmethod
    def get_all_accounts():
        print("Banking system — Selector0073")
        print(f"{'ID':<4} | {'Name':<12} | {'Balance':>8}")
        print("-" * 30)
        for row in DataBase.get_all_accounts():
            print(f"{row.id:<4} | {row.owner:<12} | {round(row.balance, 2):>8}")

    @staticmethod
    def get_balance():
        try:
            id = int(sys.argv[2])
        except IndexError:
            raise RuntimeError("Parameter id needed")
        except (ValueError, TypeError):
            raise RuntimeError("id must be integer")
        try:
            data = DataBase.get_by_id(id)
            print(f"{data.id} | {data.owner} | {round(data.balance, 2)}")
        except peewee.DoesNotExist:
            raise RuntimeError("Account does not exist")

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
            DataBase.create(owner, balance)
        except peewee.IntegrityError:
            raise RuntimeError("This user already exists")

        print(f"User \"{owner}\" created")



def main():
    dispatch = {
        "transaction": Account.transaction,
        "get_all_accounts": Account.get_all_accounts,
        "get": Account.get_balance,
        "create_account": Account.create_account,
        "fill-data": fill_random_data,
    }

    try:
        load_dotenv()
        TESTING = os.getenv("TESTNG") == "true"
    except:
        raise RuntimeError("Failed to connect to .env")

    try:
        init_db(TESTING)
    except peewee.DatabaseError:
        raise RuntimeError("Failed to initialize data base")

    try:
        dispatch[sys.argv[1]]()
    except IndexError:
        raise RuntimeError("Parameter needed (transaction, get, get_all_accounts, create_account, fill-data)")
    except KeyError:
        raise RuntimeError("Such parameter not found")


if __name__ == '__main__':
    main()