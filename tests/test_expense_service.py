"""
Tests for expense service functionality.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal


def test_record_expense(expense_service, test_user, test_category):
    """Test expense recording"""
    expense_data = {
        'user_id': test_user.id,
        'category_id': test_category.id,
        'amount': 100.50,
        'description': 'Test expense',
        'expense_date': datetime.now().strftime('%Y-%m-%d')
    }

    # Record expense
    expense = expense_service.record_expense(**expense_data)

    assert expense is not None
    assert expense['amount'] == expense_data['amount']
    assert expense['description'] == expense_data['description']
    assert expense['category']['id'] == test_category.id


def test_expense_validation(expense_service, test_user, test_category):
    """Test expense validation"""
    # Test negative amount
    with pytest.raises(ValueError) as exc:
        expense_service.record_expense(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=-50.00,
            description="Test expense",
            expense_date=datetime.now().strftime('%Y-%m-%d')
        )
    assert "Amount must be" in str(exc.value)

    # Test invalid date
    with pytest.raises(ValueError) as exc:
        expense_service.record_expense(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=50.00,
            description="Test expense",
            expense_date="invalid-date"
        )
    assert "Invalid date format" in str(exc.value)

    # Test missing description
    with pytest.raises(ValueError) as exc:
        expense_service.record_expense(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=50.00,
            description="",
            expense_date=datetime.now().strftime('%Y-%m-%d')
        )
    assert "Description is required" in str(exc.value)


def test_get_expense_summary(expense_service, test_user, test_category):
    """Test expense summary generation"""
    # Create test expenses
    dates = [
        datetime.now(),
        datetime.now() - timedelta(days=1),
        datetime.now() - timedelta(days=2)
    ]

    for i, date in enumerate(dates):
        expense_service.record_expense(
            user_id=test_user.id,
            category_id=test_category.id,
            amount=100.00 * (i + 1),
            description=f"Test expense {i + 1}",
            expense_date=date.strftime('%Y-%m-%d')
        )

    # Get summary for last 3 days
    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    summary = expense_service.get_expense_summary(
        start_date=start_date,
        end_date=end_date
    )

    assert summary is not None
    assert summary['summary']['total_amount'] == 600.00  # 100 + 200 + 300
    assert summary['summary']['total_transactions'] == 3
    assert len(summary['by_category']) == 1


def test_get_expense_details(expense_service, test_user, test_category):
    """Test retrieving expense details"""
    # Create test expense
    expense_data = {
        'user_id': test_user.id,
        'category_id': test_category.id,
        'amount': 150.75,
        'description': 'Test expense details',
        'expense_date': datetime.now().strftime('%Y-%m-%d')
    }

    expense = expense_service.record_expense(**expense_data)

    # Get expense details
    details = expense_service.get_expense_details(expense['id'])

    assert details is not None
    assert details['amount'] == expense_data['amount']
    assert details['description'] == expense_data['description']
    assert details['category']['id'] == test_category.id
    assert details['user']['id'] == test_user.id


def test_update_expense(expense_service, test_user, test_category):
    """Test expense update"""
    # Create test expense
    expense = expense_service.record_expense(
        user_id=test_user.id,
        category_id=test_category.id,
        amount=100.00,
        description="Original expense",
        expense_date=datetime.now().strftime('%Y-%m-%d')
    )

    # Update expense
    update_data = {
        'amount': 150.00,
        'description': 'Updated expense'
    }

    updated_expense = expense_service.update_expense(
        expense_id=expense['id'],
        update_data=update_data,
        audit_user_id=test_user.id
    )

    assert updated_expense is not None
    assert updated_expense['amount'] == update_data['amount']
    assert updated_expense['description'] == update_data['description']


def test_delete_expense(expense_service, test_user, test_category):
    """Test expense deletion"""
    # Create test expense
    expense = expense_service.record_expense(
        user_id=test_user.id,
        category_id=test_category.id,
        amount=100.00,
        description="Expense to delete",
        expense_date=datetime.now().strftime('%Y-%m-%d')
    )

    # Delete expense
    result = expense_service.delete_expense(
        expense_id=expense['id'],
        audit_user_id=test_user.id
    )

    assert result is True

    # Verify expense is deleted
    details = expense_service.get_expense_details(expense['id'])
    assert details is None


def test_get_category_breakdown(expense_service, test_user):
    """Test category breakdown report"""
    # Create test categories and expenses
    categories = []
    for i in range(3):
        category = expense_service.create_category(
            name=f"Test Category {i + 1}",
            type="expense",
            description=f"Test category {i + 1}"
        )
        categories.append(category)

        # Create expenses for each category
        for j in range(2):
            expense_service.record_expense(
                user_id=test_user.id,
                category_id=category['id'],
                amount=100.00 * (j + 1),
                description=f"Test expense {j + 1}",
                expense_date=datetime.now().strftime('%Y-%m-%d')
            )

    # Get category breakdown
    start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    breakdown = expense_service.get_category_breakdown(
        start_date=start_date,
        end_date=end_date
    )

    assert len(breakdown) == 3
    for category in breakdown:
        assert category['total_amount'] == 300.00  # 100 + 200
        assert category['transaction_count'] == 2