from decimal import Decimal
import pytest


class TestCreateAccount:
    def test_create_account_with_default_balance(self, service):
        account_id = service.create_account("Alice")

        assert account_id is not None
        assert service.get_balance(account_id) == Decimal("0")

    def test_create_account_with_initial_balance(self, service):
        account_id = service.create_account("Bob", 1000)

        assert service.get_balance(account_id) == Decimal("1000")


class TestGetBalance:
    def test_get_balance_of_existing_account(self, service):
        account_id = service.create_account("Carol", 250)
        balance = service.get_balance(account_id)

        assert balance == Decimal("250")

    def test_get_balance_of_nonexistent_account(self, service):
        with pytest.raises(ValueError):
            service.get_balance(9999)


class TestTransfer:
    def test_successful_transfer(self, service, funded_accounts):
        acc1, acc2 = funded_accounts

        service.transfer(acc1, acc2, 300)

        assert service.get_balance(acc1) == Decimal("700")
        assert service.get_balance(acc2) == Decimal("800")

    def test_transfer_all_funds(self, service, funded_accounts):
        acc1, acc2 = funded_accounts

        service.transfer(acc1, acc2, 1000)

        assert service.get_balance(acc1) == Decimal("0")
        assert service.get_balance(acc2) == Decimal("1500")

    def test_transfer_when_balance_insufficient(self, service, funded_accounts):
        acc1, acc2 = funded_accounts

        with pytest.raises(ValueError):
            service.transfer(acc1, acc2, 1500)

        assert service.get_balance(acc1) == Decimal("1000")
        assert service.get_balance(acc2) == Decimal("500")

    def test_transfer_negative_amount(self, service, funded_accounts):
        acc1, acc2 = funded_accounts

        with pytest.raises(ValueError):
            service.transfer(acc1, acc2, -100)

        assert service.get_balance(acc1) == Decimal("1000")
        assert service.get_balance(acc2) == Decimal("500")

    def test_transfer_from_nonexistent_account(self, service, funded_accounts):
        _, acc2 = funded_accounts

        with pytest.raises(ValueError):
            service.transfer(9999, acc2, 100)

        assert service.get_balance(acc2) == Decimal("500")

    def test_transfer_to_nonexistent_account(self, service, funded_accounts):
        acc1, _ = funded_accounts

        with pytest.raises(ValueError):
            service.transfer(acc1, 9999, 100)

        assert service.get_balance(acc1) == Decimal("1000")

    def test_multiple_consecutive_transfers(self, service, funded_accounts):
        acc1, acc2 = funded_accounts

        service.transfer(acc1, acc2, 200)
        service.transfer(acc2, acc1, 50)
        service.transfer(acc1, acc2, 100)

        assert service.get_balance(acc1) == Decimal("750")
        assert service.get_balance(acc2) == Decimal("750")
