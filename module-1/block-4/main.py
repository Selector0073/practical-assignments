from db import init_db, status_db, transaction_db, add_account_db
from fill_data import fill_random_data
import sys

def transaction():
    try:
        from_id = int(sys.argv[2])
        to_id = int(sys.argv[3])
        amount = round(float(sys.argv[4]), 2)
    except IndexError:
        print("Parameters needed: from_id, to_id, amount")
        sys.exit(1)
    except ValueError:
        print("Parameters needed: int, int, float")
        sys.exit(1)

    if not isinstance(from_id, int) | isinstance(to_id, int):
        print("Parameters 2 and 3 must be integer user id")
        sys.exit(1)
    if not isinstance(amount, float):
        print("Parameters 4 must be float money count")
        sys.exit(1)
    if float(amount) <= 0.0:
        print("Parameters 5 must be >0")
        sys.exit(1)

    transaction_db(from_id, to_id, amount)

def status():
    status_db()

def add_account():
    try:
        add_account_db(sys.argv[2], sys.argv[3])
    except:
        print("Wrong parameter (string float)")
        sys.exit(1)

def main():
    dispatch = {
        "transaction": transaction,
        "status": status,
        "add_account": add_account,
        "fill-data": fill_random_data,
    }

    try:
        init_db()
    except KeyError:
        print("Failed to initialize the database")
        sys.exit(1)

    try:
        parameter = sys.argv[1]
    except IndexError:
        print("Parameter needed")
        sys.exit(1)
    try:
        dispatch[parameter]()
    except KeyError:
        print("Wrong parameter")
        sys.exit(1)


if __name__ == '__main__':
    main()