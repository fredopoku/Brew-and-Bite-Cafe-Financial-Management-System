"""
Tests for database models and initialization.
"""

import pytest
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from src.database.models import User, Category, Expense, InventoryItem, Sale, UserRole
from src.utils.security import hash_password, verify_password


def test_user_creation(test_db):
    """Test user model creation"""
    # Create test user
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.STAFF,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()

    # Retrieve user
    saved_user = test_db.query(User).filter_by(username="testuser").first()
    assert saved_user is not None
    assert saved_user.email == "test@example.com"
    assert saved_user.role == UserRole.STAFF
    assert saved_user.is_active is True
    assert verify_password("password123", saved_user.password_hash)


def test_user_unique_constraints(test_db):
    """Test user model unique constraints"""
    # Create first user
    user1 = User(
        username="uniqueuser",
        email="unique@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.STAFF
    )
    test_db.add(user1)
    test_db.commit()

    # Try to create user with same username
    user2 = User(
        username="uniqueuser",
        email="different@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.STAFF
    )
    test_db.add(user2)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()

    # Try to create user with same email
    user3 = User(
        username="differentuser",
        email="unique@example.com",
        password_hash=hash_password("password123"),
        role=UserRole.STAFF
    )
    test_db.add(user3)
    with pytest.raises(IntegrityError):
        test_db.commit()
    test_db.rollback()


def test_category_creation(test_db):
    """Test category model creation"""
    category = Category(
        name="Test Category",
        type="expense",
        description="Test description"
    )
    test_db.add(category)
    test_db.commit()

    saved_category = test_db.query(Category).filter_by(name="Test Category").first()
    assert saved_category is not None
    assert saved_category.type == "expense"
    assert saved_category.description == "Test description"


def test_inventory_item_creation(test_db):
    """Test inventory item model creation"""
    item = InventoryItem(
        name="Test Item",
        description="Test description",
        quantity=100,
        unit_cost=10.50,
        reorder_level=20
    )
    test_db.add(item)
    test_db.commit()

    saved_item = test_db.query(InventoryItem).filter_by(name="Test Item").first()
    assert saved_item is not None
    assert saved_item.quantity == 100
    assert saved_item.unit_cost == 10.50
    assert saved_item.reorder_level == 20


def test_expense_creation(test_db, test_user, test_category):
    """Test expense model creation"""
    expense = Expense(
        user_id=test_user.id,
        category_id=test_category.id,
        amount=100.50,
        description="Test expense",
        date=datetime.utcnow()
    )
    test_db.add(expense)
    test_db.commit()

    saved_expense = test_db.query(Expense) \
        .filter_by(user_id=test_user.id) \
        .first()

    assert saved_expense is not None
    assert saved_expense.amount == 100.50
    assert saved_expense.category_id == test_category.id


def test_sale_creation(test_db, test_user, test_inventory_item):
    """Test sale model creation"""
    # Create sale
    sale = Sale(
        user_id=test_user.id,
        date=datetime.utcnow(),
        total_amount=50.00,
        payment_method="cash",
        notes="Test sale"
    )
    test_db.add(sale)
    test_db.commit()

    saved_sale = test_db.query(Sale) \
        .filter_by(user_id=test_user.id) \
        .first()

    assert saved_sale is not None
    assert saved_sale.total_amount == 50.00
    assert saved_sale.payment_method == "cash"


def test_relationships(test_db, test_user, test_category, test_inventory_item):
    """Test model relationships"""
    # Create expense
    expense = Expense(
        user_id=test_user.id,
        category_id=test_category.id,
        amount=75.00,
        description="Test relationship expense",
        date=datetime.utcnow()
    )
    test_db.add(expense)
    test_db.commit()

    # Test expense relationships
    assert expense.user.id == test_user.id
    assert expense.category.id == test_category.id

    # Test user relationships
    assert test_user.expenses[0].amount == 75.00

    # Test category relationships
    assert test_category.expenses[0].description == "Test relationship expense"