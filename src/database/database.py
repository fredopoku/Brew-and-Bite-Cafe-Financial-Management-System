from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import logging
from datetime import datetime
import os

from src.config import DATABASE_URL
from src.models import Base, User, Category, InventoryItem, UserRole
from src.utils.security import hash_password

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionFactory = sessionmaker(bind=engine)

# Create thread-safe session factory
Session = scoped_session(SessionFactory)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        session.close()

def initialize_database():
    """Initialize the database with tables and default data."""
    try:
        # Setup data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)

        logger.info("Initializing database...")

        # Create all tables
        Base.metadata.create_all(engine)
        logger.info("Database tables created successfully")

        with session_scope() as session:
            # Create default admin user if not exists
            admin_exists = session.query(User).filter_by(username='admin').first()
            if not admin_exists:
                admin_password = hash_password('admin123')
                admin_user = User(
                    username='admin',
                    email='admin@brewandbite.com',
                    password_hash=admin_password,
                    role=UserRole.ADMIN
                )
                session.add(admin_user)
                logger.info("Admin user created successfully")

            # Create default categories if they don't exist
            default_categories = [
                ('Food Supplies', 'expense', 'Raw ingredients and food supplies'),
                ('Beverages', 'expense', 'Coffee beans, tea, and other beverages'),
                ('Utilities', 'expense', 'Electricity, water, gas, etc.'),
                ('Salaries', 'expense', 'Employee wages and salaries'),
                ('Equipment', 'expense', 'Kitchen and cafe equipment'),
                ('Marketing', 'expense', 'Advertising and promotions'),
                ('Food Sales', 'income', 'Revenue from food items'),
                ('Beverage Sales', 'income', 'Revenue from beverages')
            ]

            for name, type_, description in default_categories:
                category_exists = session.query(Category).filter_by(name=name).first()
                if not category_exists:
                    category = Category(
                        name=name,
                        type=type_,
                        description=description
                    )
                    session.add(category)

            # Add default inventory items
            default_inventory = [
                ('Coffee Beans (1kg)', 'Premium Arabica coffee beans', 50, 20.0, 10),
                ('Milk (1L)', 'Fresh whole milk', 100, 2.5, 20),
                ('Sugar (1kg)', 'White granulated sugar', 75, 1.5, 15),
                ('Tea Bags (box)', 'Assorted tea bags', 30, 5.0, 8),
                ('Cups (pack)', 'Disposable coffee cups', 200, 0.25, 50)
            ]

            for name, desc, qty, cost, reorder in default_inventory:
                item_exists = session.query(InventoryItem).filter_by(name=name).first()
                if not item_exists:
                    item = InventoryItem(
                        name=name,
                        description=desc,
                        quantity=qty,
                        unit_cost=cost,
                        reorder_level=reorder
                    )
                    session.add(item)

            logger.info("Default data created successfully")

    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def get_session():
    """Get a new database session."""
    return Session()

def backup_database():
    """Create a backup of the database."""
    try:
        # Create backups directory if it doesn't exist
        os.makedirs('data/backups', exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f'data/backups/brew_and_bite_backup_{timestamp}.db'

        # Create backup copy
        with open('data/brew_and_bite.db', 'rb') as source:
            with open(backup_path, 'wb') as backup:
                backup.write(source.read())

        logger.info(f"Database backup created successfully at {backup_path}")
        return True
    except Exception as e:
        logger.error(f"Database backup failed: {str(e)}")
        return False