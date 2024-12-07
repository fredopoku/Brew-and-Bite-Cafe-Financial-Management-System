"""
Tests for sales service functionality.
"""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal


def test_create_sale(sales_service, test_user, test_inventory_item):
    """Test sale creation"""
    items = [{
        'inventory_item_id': test_inventory_item.id,
        'quantity': 2,
        'unit_price': 25.00
    }]

    # Create sale
    sale, warnings = sales_service.create_sale(
        user_id=test_user.id,
        items=items,
        payment_method='cash',
        notes="Test sale"
    )

    assert sale is not None
    assert sale['total_amount'] == 50.00  # 2 * 25.00
    assert sale['payment_method'] == 'cash'
    assert len(sale['items']) == 1
    assert len(warnings) == 0


def test_sale_validation(sales_service, test_user, test_inventory_item):
    """Test sale validation"""
    # Test negative quantity
    with pytest.raises(ValueError) as exc:
        sales_service.create_sale(
            user_id=test_user.id,
            items=[{
                'inventory_item_id': test_inventory_item.id,
                'quantity': -1,
                'unit_price': 25.00
            }],
            payment_method='cash'
        )
    assert "Invalid quantity" in str(exc.value)

    # Test negative unit price
    with pytest.raises(ValueError) as exc:
        sales_service.create_sale(
            user_id=test_user.id,
            items=[{
                'inventory_item_id': test_inventory_item.id,
                'quantity': 1,
                'unit_price': -25.00
            }],
            payment_method='cash'
        )
    assert "Invalid unit price" in str(exc.value)

    # Test insufficient stock
    original_quantity = test_inventory_item.quantity
    with pytest.raises(ValueError) as exc:
        sales_service.create_sale(
            user_id=test_user.id,
            items=[{
                'inventory_item_id': test_inventory_item.id,
                'quantity': original_quantity + 1,
                'unit_price': 25.00
            }],
            payment_method='cash'
        )
    assert "Insufficient stock" in str(exc.value)


def test_get_sale_details(sales_service, test_user, test_inventory_item):
    """Test retrieving sale details"""
    # Create test sale
    items = [{
        'inventory_item_id': test_inventory_item.id,
        'quantity': 2,
        'unit_price': 25.00
    }]

    sale, _ = sales_service.create_sale(
        user_id=test_user.id,
        items=items,
        payment_method='cash',
        notes="Test sale details"
    )

    # Get sale details
    details = sales_service.get_sale_details(sale['id'])

    assert details is not None
    assert details['total_amount'] == 50.00
    assert details['user']['id'] == test_user.id
    assert len(details['items']) == 1
    assert details['items'][0]['quantity'] == 2


def test_void_sale(sales_service, test_user, test_inventory_item):
    """Test sale voiding"""
    # Create test sale
    initial_quantity = test_inventory_item.quantity
    items = [{
        'inventory_item_id': test_inventory_item.id,
        'quantity': 2,
        'unit_price': 25.00
    }]

    sale, _ = sales_service.create_sale(
        user_id=test_user.id,
        items=items,
        payment_method='cash'
    )

    # Void sale
    result = sales_service.void_sale(
        sale_id=sale['id'],
        user_id=test_user.id,
        reason="Test void"
    )

    assert result is True

    # Verify inventory restored
    status = sales_service.inventory_service.get_inventory_status()
    item = next(item for item in status['items'] if item['id'] == test_inventory_item.id)
    assert item['quantity'] == initial_quantity


def test_get_daily_sales_summary(sales_service, test_user, test_inventory_item):
    """Test daily sales summary"""
    # Create multiple sales
    items = [{
        'inventory_item_id': test_inventory_item.id,
        'quantity': 1,
        'unit_price': 25.00
    }]

    for _ in range(3):
        sales_service.create_sale(
            user_id=test_user.id,
            items=items,
            payment_method='cash'
        )

    # Get daily summary
    today = datetime.now().strftime('%Y-%m-%d')
    summary = sales_service.get_daily_sales_summary(today)

    assert summary['summary']['total_sales'] == 75.00  # 3 * 25.00
    assert summary['summary']['transaction_count'] == 3
    assert len(summary['payment_methods']) == 1
    assert summary['payment_methods'][0]['method'] == 'cash'


def test_get_sales_report(sales_service, test_user, test_inventory_item):
    """Test sales report generation"""
    # Create sales over multiple days
    items = [{
        'inventory_item_id': test_inventory_item.id,
        'quantity': 1,
        'unit_price': 25.00
    }]

    dates = [
        datetime.now(),
        datetime.now() - timedelta(days=1),
        datetime.now() - timedelta(days=2)
    ]

    for _ in range(3):
        sales_service.create_sale(
            user_id=test_user.id,
            items=items,
            payment_method='cash'
        )

    # Get sales report
    start_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    report = sales_service.get_sales_report(
        start_date=start_date,
        end_date=end_date,
        group_by='day'
    )

    assert report['summary']['total_revenue'] == 75.00  # 3 * 25.00
    assert report['summary']['total_transactions'] == 3
    assert len(report['sales_over_time']) >= 1


def test_get_top_selling_items(sales_service, test_user, test_inventory_item):
    """Test top selling items report"""
    # Create another test item
    other_item = sales_service.inventory_service.add_inventory_item(
        name="Other Test Item",
        description="Another test item",
        quantity=100,
        unit_cost=15.00,
        reorder_level=10,
        audit_user_id=1
    )

    # Create sales with different items
    sales_data = [
        # First item sold more times but less revenue
        [{
            'inventory_item_id': test_inventory_item.id,
            'quantity': 1,
            'unit_price': 25.00
        }],
        # Second item sold fewer times but more revenue
        [{
            'inventory_item_id': other_item['id'],
            'quantity': 2,
            'unit_price': 30.00
        }]
    ]

    for items in sales_data:
        sales_service.create_sale(
            user_id=test_user.id,
            items=items,
            payment_method='cash'
        )

        # Get top selling items
    start_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    top_items = sales_service.get_top_selling_items(
        start_date=start_date,
        end_date=end_date,
        limit=10
    )

    assert len(top_items) == 2
    # First item should be the one with more revenue
    assert top_items[0]['name'] == "Other Test Item"
    assert top_items[0]['quantity'] == 2
    assert top_items[0]['revenue'] == 60.00  # 2 * 30.00


def test_sales_with_multiple_items(sales_service, test_user, test_inventory_item):
    """Test creating sales with multiple items"""
    # Create another test item
    second_item = sales_service.inventory_service.add_inventory_item(
        name="Second Test Item",
        description="Another test item",
        quantity=100,
        unit_cost=15.00,
        reorder_level=10,
        audit_user_id=1
    )

    # Create sale with multiple items
    items = [
        {
            'inventory_item_id': test_inventory_item.id,
            'quantity': 2,
            'unit_price': 25.00
        },
        {
            'inventory_item_id': second_item['id'],
            'quantity': 3,
            'unit_price': 30.00
        }
    ]

    sale, warnings = sales_service.create_sale(
        user_id=test_user.id,
        items=items,
        payment_method='card',
        notes="Multi-item test sale"
    )

    assert sale is not None
    assert sale['total_amount'] == 140.00  # (2 * 25.00) + (3 * 30.00)
    assert len(sale['items']) == 2
    assert len(warnings) == 0


def test_sales_by_payment_method(sales_service, test_user, test_inventory_item):
    """Test sales filtering by payment method"""
    # Create sales with different payment methods
    items = [{
        'inventory_item_id': test_inventory_item.id,
        'quantity': 1,
        'unit_price': 25.00
    }]

    payment_methods = ['cash', 'card', 'mobile']
    for method in payment_methods:
        sales_service.create_sale(
            user_id=test_user.id,
            items=items,
            payment_method=method
        )

    # Get sales report
    start_date = datetime.now().strftime('%Y-%m-%d')
    end_date = start_date

    summary = sales_service.get_daily_sales_summary(start_date)

    assert len(summary['payment_methods']) == 3
    for pm in summary['payment_methods']:
        assert pm['amount'] == 25.00
        assert pm['count'] == 1


def test_sales_date_range_validation(sales_service):
    """Test sales report date range validation"""
    # Test end date before start date
    with pytest.raises(ValueError) as exc:
        sales_service.get_sales_report(
            start_date=(datetime.now()).strftime('%Y-%m-%d'),
            end_date=(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        )
    assert "Start date must be before end date" in str(exc.value)

    # Test invalid date format
    with pytest.raises(ValueError) as exc:
        sales_service.get_sales_report(
            start_date="invalid-date",
            end_date=datetime.now().strftime('%Y-%m-%d')
        )
    assert "Invalid date format" in str(exc.value)


def test_low_stock_warning(sales_service, test_user, test_inventory_item):
    """Test low stock warnings during sale"""
    # Update item to have quantity just above reorder level
    sales_service.inventory_service.update_stock(
        item_id=test_inventory_item.id,
        quantity_change=-(test_inventory_item.quantity - test_inventory_item.reorder_level - 2),
        transaction_type='adjustment',
        user_id=test_user.id,
        notes="Adjust for low stock test"
    )

    # Create sale that will trigger low stock warning
    items = [{
        'inventory_item_id': test_inventory_item.id,
        'quantity': 2,
        'unit_price': 25.00
    }]

    sale, warnings = sales_service.create_sale(
        user_id=test_user.id,
        items=items,
        payment_method='cash'
    )

    assert len(warnings) > 0
    assert any("Low stock alert" in warning for warning in warnings)


def test_sale_items_validation(sales_service, test_user, test_inventory_item):
    """Test validation of sale items"""
    # Test empty items list
    with pytest.raises(ValueError) as exc:
        sales_service.create_sale(
            user_id=test_user.id,
            items=[],
            payment_method='cash'
        )
    assert "No items in sale" in str(exc.value)

    # Test invalid inventory item ID
    with pytest.raises(ValueError) as exc:
        sales_service.create_sale(
            user_id=test_user.id,
            items=[{
                'inventory_item_id': 99999,  # Non-existent ID
                'quantity': 1,
                'unit_price': 25.00
            }],
            payment_method='cash'
        )
    assert "Invalid inventory item ID" in str(exc.value)


def test_sales_reporting_aggregation(sales_service, test_user, test_inventory_item):
    """Test sales reporting with different aggregation periods"""
    # Create sales across different days
    items = [{
        'inventory_item_id': test_inventory_item.id,
        'quantity': 1,
        'unit_price': 25.00
    }]

    for i in range(10):  # Create sales across different days
        sales_service.create_sale(
            user_id=test_user.id,
            items=items,
            payment_method='cash'
        )

    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    end_date = datetime.now().strftime('%Y-%m-%d')

    # Test different grouping periods
    groupings = ['day', 'week', 'month']
    for group_by in groupings:
        report = sales_service.get_sales_report(
            start_date=start_date,
            end_date=end_date,
            group_by=group_by
        )

        assert report is not None
        assert 'sales_over_time' in report
        assert 'summary' in report
        assert report['summary']['total_revenue'] == 250.00  # 10 sales * 25.00