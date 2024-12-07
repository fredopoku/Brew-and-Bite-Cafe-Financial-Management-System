"""
Tests for inventory service functionality.
"""

import pytest
from datetime import datetime
from decimal import Decimal


def test_add_inventory_item(inventory_service):
    """Test adding new inventory item"""
    item_data = {
        'name': 'Test Coffee',
        'description': 'Premium coffee beans',
        'quantity': 100,
        'unit_cost': 20.50,
        'reorder_level': 20,
        'audit_user_id': 1
    }

    # Add item
    item = inventory_service.add_inventory_item(**item_data)

    assert item is not None
    assert item['name'] == item_data['name']
    assert item['quantity'] == item_data['quantity']
    assert float(item['unit_cost']) == item_data['unit_cost']
    assert item['reorder_level'] == item_data['reorder_level']


def test_inventory_validation(inventory_service):
    """Test inventory item validation"""
    # Test negative quantity
    with pytest.raises(ValueError) as exc:
        inventory_service.add_inventory_item(
            name="Test Item",
            description="Test description",
            quantity=-10,
            unit_cost=10.00,
            reorder_level=5,
            audit_user_id=1
        )
    assert "Quantity cannot be negative" in str(exc.value)

    # Test negative unit cost
    with pytest.raises(ValueError) as exc:
        inventory_service.add_inventory_item(
            name="Test Item",
            description="Test description",
            quantity=10,
            unit_cost=-10.00,
            reorder_level=5,
            audit_user_id=1
        )
    assert "Unit cost cannot be negative" in str(exc.value)

    # Test negative reorder level
    with pytest.raises(ValueError) as exc:
        inventory_service.add_inventory_item(
            name="Test Item",
            description="Test description",
            quantity=10,
            unit_cost=10.00,
            reorder_level=-5,
            audit_user_id=1
        )
    assert "Reorder level cannot be negative" in str(exc.value)


def test_update_stock(inventory_service, test_inventory_item):
    """Test stock update functionality"""
    # Add stock
    item, warning = inventory_service.update_stock(
        item_id=test_inventory_item.id,
        quantity_change=50,
        transaction_type='restock',
        user_id=1,
        notes="Restocking test"
    )

    assert item is not None
    assert item['quantity'] == test_inventory_item.quantity + 50
    assert warning is None

    # Remove stock
    item, warning = inventory_service.update_stock(
        item_id=test_inventory_item.id,
        quantity_change=-20,
        transaction_type='sale',
        user_id=1,
        notes="Sale test"
    )

    assert item is not None
    assert item['quantity'] == test_inventory_item.quantity + 30  # +50 -20

    # Test low stock warning
    item, warning = inventory_service.update_stock(
        item_id=test_inventory_item.id,
        quantity_change=-(item['quantity'] - 5),
        transaction_type='adjustment',
        user_id=1,
        notes="Adjustment test"
    )

    assert warning is not None
    assert "Low stock alert" in warning


def test_get_inventory_status(inventory_service, test_inventory_item):
    """Test inventory status report"""
    # Create additional test items
    inventory_service.add_inventory_item(
        name="Low Stock Item",
        description="Item with low stock",
        quantity=5,
        unit_cost=15.00,
        reorder_level=10,
        audit_user_id=1
    )

    inventory_service.add_inventory_item(
        name="Out of Stock Item",
        description="Item with no stock",
        quantity=0,
        unit_cost=25.00,
        reorder_level=10,
        audit_user_id=1
    )

    # Get inventory status
    status = inventory_service.get_inventory_status()

    assert status is not None
    assert status['total_items'] >= 3
    assert 'total_value' in status
    assert len(status['alerts']['low_stock_items']) >= 1
    assert len(status['alerts']['out_of_stock_items']) >= 1

    # Verify item categorization
    low_stock_names = [item['name'] for item in status['alerts']['low_stock_items']]
    out_of_stock_names = [item['name'] for item in status['alerts']['out_of_stock_items']]

    assert "Low Stock Item" in low_stock_names
    assert "Out of Stock Item" in out_of_stock_names


def test_get_transaction_history(inventory_service, test_inventory_item):
    """Test transaction history retrieval"""
    # Create some transactions
    transactions = [
        (50, 'restock', "Initial restock"),
        (-20, 'sale', "Test sale"),
        (10, 'adjustment', "Inventory correction")
    ]

    for qty, type_, notes in transactions:
        inventory_service.update_stock(
            item_id=test_inventory_item.id,
            quantity_change=qty,
            transaction_type=type_,
            user_id=1,
            notes=notes
        )

    # Get transaction history
    history = inventory_service.get_transaction_history(test_inventory_item.id)

    assert len(history) >= 3
    # Transactions should be in reverse chronological order
    assert history[0]['type'] == 'adjustment'
    assert history[1]['type'] == 'sale'
    assert history[2]['type'] == 'restock'


def test_total_value_calculation(inventory_service):
    """Test inventory total value calculation"""
    items_data = [
        {
            'name': 'Value Test 1',
            'description': 'Test item 1',
            'quantity': 100,
            'unit_cost': 10.00,
            'reorder_level': 20
        },
        {
            'name': 'Value Test 2',
            'description': 'Test item 2',
            'quantity': 50,
            'unit_cost': 20.00,
            'reorder_level': 10
        }
    ]

    expected_total = sum(item['quantity'] * item['unit_cost'] for item in items_data)

    # Add test items
    for item_data in items_data:
        inventory_service.add_inventory_item(
            **item_data,
            audit_user_id=1
        )

    # Get inventory status
    status = inventory_service.get_inventory_status()

    # The total value should be at least the sum of our test items
    assert float(status['total_value']) >= expected_total


def test_batch_stock_update(inventory_service, test_inventory_item):
    """Test batch stock update functionality"""
    updates = [
        (test_inventory_item.id, 50, 'restock', "Batch restock"),
        (test_inventory_item.id, -20, 'sale', "Batch sale"),
        (test_inventory_item.id, 10, 'adjustment', "Batch adjustment")
    ]

    results = inventory_service.batch_update_stock(
        updates=updates,
        user_id=1
    )

    assert len(results) == 3
    assert all(result['success'] for result in results)

    # Verify final quantity
    status = inventory_service.get_inventory_status()
    item = next(item for item in status['items'] if item['id'] == test_inventory_item.id)
    assert item['quantity'] == test_inventory_item.quantity + 40  # +50 -20 +10