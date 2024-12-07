from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from src.dal.inventory_dao import InventoryDAO
from src.utils.validators import validate_amount, validate_quantity
from src.database.models import InventoryItem

logger = logging.getLogger(__name__)


class InventoryService:
    def __init__(self, session: Session):
        self.session = session
        self.inventory_dao = InventoryDAO(session)

    def add_inventory_item(self, name: str, description: str, quantity: int,
                           unit_cost: float, reorder_level: int,
                           audit_user_id: int) -> Dict:
        """Add a new inventory item"""
        try:
            # Validate quantity
            quantity_valid, quantity_error = validate_quantity(str(quantity))
            if not quantity_valid:
                raise ValueError(quantity_error)

            # Validate unit cost
            cost_valid, cost_error = validate_amount(str(unit_cost))
            if not cost_valid:
                raise ValueError(cost_error)

            # Validate reorder level
            if reorder_level < 0:
                raise ValueError("Reorder level cannot be negative")

            # Create inventory item
            item = self.inventory_dao.create_item(
                name=name,
                description=description,
                quantity=quantity,
                unit_cost=Decimal(str(unit_cost)),
                reorder_level=reorder_level,
                audit_user_id=audit_user_id
            )

            logger.info(f"Inventory item added successfully: {name}")

            return {
                'id': item.id,
                'name': item.name,
                'description': item.description,
                'quantity': item.quantity,
                'unit_cost': float(item.unit_cost),
                'reorder_level': item.reorder_level,
                'last_restocked': item.last_restocked.isoformat() if item.last_restocked else None
            }

        except Exception as e:
            logger.error(f"Failed to add inventory item: {str(e)}")
            raise

    def update_stock(self, item_id: int, quantity_change: int,
                     transaction_type: str, user_id: int,
                     notes: Optional[str] = None) -> Tuple[Dict, Optional[str]]:
        """Update inventory stock levels"""
        try:
            # Validate quantity change
            quantity_valid, quantity_error = validate_quantity(str(abs(quantity_change)))
            if not quantity_valid:
                raise ValueError(quantity_error)

            # Validate transaction type
            valid_types = ['restock', 'sale', 'adjustment']
            if transaction_type not in valid_types:
                raise ValueError(f"Invalid transaction type. Must be one of: {', '.join(valid_types)}")

            # Update stock
            item = self.inventory_dao.update_quantity(
                item_id=item_id,
                quantity_change=quantity_change,
                transaction_type=transaction_type,
                user_id=user_id,
                notes=notes
            )

            if not item:
                raise ValueError("Inventory item not found")

            # Check if stock is below reorder level
            warning = None
            if item.quantity <= item.reorder_level:
                warning = f"Low stock alert: Current quantity ({item.quantity}) is at or below reorder level ({item.reorder_level})"

            logger.info(f"Stock updated for {item.name}: {quantity_change} units ({transaction_type})")

            return {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'unit_cost': float(item.unit_cost),
                'transaction_type': transaction_type,
                'last_restocked': item.last_restocked.isoformat() if item.last_restocked else None
            }, warning

        except Exception as e:
            logger.error(f"Failed to update stock: {str(e)}")
            raise

    def get_inventory_status(self) -> Dict:
        """Get current inventory status with alerts"""
        try:
            # Get all inventory items
            items = self.inventory_dao.get_all_items()

            # Calculate total inventory value
            total_value = sum(item.quantity * item.unit_cost for item in items)

            # Identify low stock items
            low_stock = [item for item in items if item.quantity <= item.reorder_level]

            # Identify out of stock items
            out_of_stock = [item for item in items if item.quantity == 0]

            return {
                'total_items': len(items),
                'total_value': float(total_value),
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'quantity': item.quantity,
                        'unit_cost': float(item.unit_cost),
                        'total_value': float(item.quantity * item.unit_cost),
                        'reorder_level': item.reorder_level,
                        'status': 'out_of_stock' if item.quantity == 0 else
                        'low_stock' if item.quantity <= item.reorder_level else 'normal'
                    }
                    for item in items
                ],
                'alerts': {
                    'low_stock_items': [
                        {
                            'id': item.id,
                            'name': item.name,
                            'quantity': item.quantity,
                            'reorder_level': item.reorder_level
                        }
                        for item in low_stock
                    ],
                    'out_of_stock_items': [
                        {
                            'id': item.id,
                            'name': item.name
                        }
                        for item in out_of_stock
                    ]
                }
            }

        except Exception as e:
            logger.error(f"Failed to get inventory status: {str(e)}")
            raise

    def get_transaction_history(self, item_id: int, limit: Optional[int] = None) -> List[Dict]:
        """Get transaction history for an inventory item"""
        try:
            transactions = self.inventory_dao.get_transaction_history(item_id, limit)

            return [
                {
                    'transaction_id': trans.id,
                    'date': trans.date.isoformat(),
                    'type': trans.transaction_type,
                    'quantity': trans.quantity,
                    'notes': trans.notes,
                    'user': {
                        'id': trans.user.id,
                        'username': trans.user.username
                    }
                }
                for trans in transactions
            ]

        except Exception as e:
            logger.error(f"Failed to get transaction history: {str(e)}")
            raise