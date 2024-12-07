"""
Test configuration and fixtures for the Brew and Bite Café Management System.
"""

import pytest
import os
import tempfile
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from typing import Generator

from src.database.models import Base, User, Category, UserRole, InventoryItem
from src.utils.security import hash_password


@pytest.fixture(scope="session")
def test_db() -> Generator[Session, None, None]:
    """Create a temporary test database"""
    # Create temporary database file
    db_fd, db_path = tempfile.mkstemp()
    db_url = f"sqlite:///{db_path}"

    # Create database engine
    engine = create_engine(db_url)

    # Create all tables
    Base.metadata.create_all(engine)

    # Create session factory
    TestSession = sessionmaker(bind=engine)
    session = TestSession()

    # Create test data
    _create_test_data(session)

    yield session

    # Cleanup
    session.close()
    os.close(db_fd)
    os.unlink(db_path)


def _create_test_data(session: Session) -> None:
    """Create initial test data"""
    try:
        # Create test users
        users = [
            User(
                username="admin_test",
                email="admin@test.com",
                password_hash=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True
            ),
            User(
                username="manager_test",
                email="manager@test.com",
                password_hash=hash_password("manager123"),
                role=UserRole.MANAGER,
                is_active=True
            ),
            User(
                username="staff_test",
                email="staff@test.com",
                password_hash=hash_password("staff123"),
                role=UserRole.STAFF,
                is_active=True
            )
        ]
        session.add_all(users)

        # Create test categories
        categories = [
            Category(name="Food", type="expense", description="Food supplies"),
            Category(name="Utilities", type="expense", description="Utility bills"),
            Category(name="Drinks", type="expense", description="Beverages"),
            Category(name="Food Sales", type="income", description="Food revenue"),
            Category(name="Drink Sales", type="income", description="Beverage revenue")
        ]
        session.add_all(categories)

        # Create test inventory items
        items = [
            InventoryItem(
                name="Coffee Beans",
                description="Premium coffee beans",
                quantity=100,
                unit_cost=20.00,
                reorder_level=20
            ),
            InventoryItem(
                name="Milk",
                description="Fresh milk",
                quantity=50,
                unit_cost=2.50,
                reorder_level=10
            )
        ]
        session.add_all(items)

        session.commit()

    except Exception as e:
        session.rollback()
        raise


# Service fixtures
@pytest.fixture
def user_service(test_db):
    """Create user service instance"""
    from src.bll.user_service import UserService
    return UserService(test_db)


@pytest.fixture
def expense_service(test_db):
    """Create expense service instance"""
    from src.bll.expense_service import ExpenseService
    return ExpenseService(test_db)


@pytest.fixture
def inventory_service(test_db):
    """Create inventory service instance"""
    from src.bll.inventory_service import InventoryService
    return InventoryService(test_db)


@pytest.fixture
def sales_service(test_db):
    """Create sales service instance"""
    from src.bll.sales_service import SalesService
    return SalesService(test_db)


# Data fixtures
@pytest.fixture
def test_user(test_db) -> User:
    """Create a test user"""
    user = User(
        username="test_user",
        email="test@example.com",
        password_hash=hash_password("test123"),
        role=UserRole.STAFF,
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    return user


@pytest.fixture
def test_category(test_db) -> Category:
    """Create a test category"""
    category = Category(
        name="Test Category",
        type="expense",
        description="Test category description"
    )
    test_db.add(category)
    test_db.commit()
    return category


@pytest.fixture
def test_inventory_item(test_db) -> InventoryItem:
    """Create a test inventory item"""
    item = InventoryItem(
        name="Test Item",
        description="Test item description",
        quantity=50,
        unit_cost=10.00,
        reorder_level=10
    )
    test_db.add(item)
    test_db.commit()
    return item