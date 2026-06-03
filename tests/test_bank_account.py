"""Tests for the bank account closure example."""
import pytest
from pathlib import Path
from pebble.evaluator import make_global_env, eval_source, EvalError
import io
import sys


@pytest.fixture(scope="module")
def bank_account_env_and_output():
    """Load the bank_account.pebble file once and capture its output."""
    # Redirect stdout to capture demo output
    old_stdout = sys.stdout
    sys.stdout = captured_output = io.StringIO()

    try:
        example_file = Path(__file__).parent.parent / "examples" / "bank_account.pebble"
        with open(example_file) as f:
            source = f.read()

        env = make_global_env()
        eval_source(source, env)
    finally:
        sys.stdout = old_stdout

    demo_output = captured_output.getvalue()
    return env, demo_output


class TestBankAccount:
    """Tests for the bank account closure example."""

    def test_example_output(self, bank_account_env_and_output):
        """Test that the example file produces the correct demo output."""
        env, demo_output = bank_account_env_and_output
        # The demo should print exactly "120"
        assert demo_output.strip() == "120"

    def test_make_account_creation(self, bank_account_env_and_output):
        """Test that accounts can be created and their initial balance is correct."""
        env, _ = bank_account_env_and_output

        # Create an account with initial balance 100 and check its balance
        result = eval_source("(account-balance (make-account 100))", env)
        assert result == 100

    def test_account_balance_getter(self, bank_account_env_and_output):
        """Test the account-balance convenience function."""
        env, _ = bank_account_env_and_output

        # Create an account and check its balance
        result = eval_source("(account-balance (make-account 500))", env)
        assert result == 500

    def test_deposit_updates_balance(self, bank_account_env_and_output):
        """Test that deposit updates and returns the new balance."""
        env, _ = bank_account_env_and_output

        # Create an account, deposit 50, and check new balance
        result = eval_source(
            "(let ((a (make-account 100))) "
            "  (account-deposit! a 50) "
            "  (account-balance a))",
            env
        )
        assert result == 150

    def test_withdraw_updates_balance(self, bank_account_env_and_output):
        """Test that withdraw updates and returns the new balance."""
        env, _ = bank_account_env_and_output

        # Create an account, withdraw 75, and check new balance
        result = eval_source(
            "(let ((a (make-account 200))) "
            "  (account-withdraw! a 75) "
            "  (account-balance a))",
            env
        )
        assert result == 125

    def test_withdraw_insufficient_funds(self, bank_account_env_and_output):
        """Test that withdrawing more than balance raises an error."""
        env, _ = bank_account_env_and_output

        # Try to withdraw more than balance
        with pytest.raises(EvalError, match="Insufficient funds"):
            eval_source(
                "(let ((a (make-account 100))) "
                "  (account-withdraw! a 150))",
                env
            )

        # Verify a fresh account still has the correct balance
        # (the failed withdraw above should not affect any existing state)
        result = eval_source(
            "(let ((a (make-account 100))) "
            "  (account-balance a))",
            env
        )
        assert result == 100

    def test_sequence_of_operations(self, bank_account_env_and_output):
        """Test a sequence of deposit and withdraw operations."""
        env, _ = bank_account_env_and_output

        # Create account with 0, deposit 200, withdraw 75, deposit 25
        result = eval_source(
            "(let ((a (make-account 0))) "
            "  (account-deposit! a 200) "
            "  (account-withdraw! a 75) "
            "  (account-deposit! a 25) "
            "  (account-balance a))",
            env
        )
        assert result == 150

    def test_account_independence(self, bank_account_env_and_output):
        """Test that two accounts have independent state."""
        env, _ = bank_account_env_and_output

        # Create two accounts and verify they're independent
        result = eval_source(
            "(let ((a (make-account 100)) "
            "      (b (make-account 0))) "
            "  (account-deposit! a 50) "
            "  (account-deposit! b 75) "
            "  (list (account-balance a) (account-balance b)))",
            env
        )
        # Result should be (150 75)
        assert len(result) == 2
        assert result[0] == 150
        assert result[1] == 75

    def test_multiple_independent_accounts(self, bank_account_env_and_output):
        """Test that multiple accounts can operate independently."""
        env, _ = bank_account_env_and_output

        # Create three accounts and perform different operations on each
        result = eval_source(
            "(let ((x (make-account 1000)) "
            "      (y (make-account 500)) "
            "      (z (make-account 200))) "
            "  (account-withdraw! x 100) "
            "  (account-deposit! y 100) "
            "  (account-withdraw! z 50) "
            "  (list (account-balance x) (account-balance y) (account-balance z)))",
            env
        )
        assert len(result) == 3
        assert result[0] == 900
        assert result[1] == 600
        assert result[2] == 150
