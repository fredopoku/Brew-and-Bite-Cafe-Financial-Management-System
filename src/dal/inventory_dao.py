from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.database.models import InventoryItem, InventoryTransaction, AuditLog


class InventoryDAO:
    def __init__(self, session: Session):
        self.session = session

    def create_item(self, name: str, description: str, quantity: int,
                    unit_cost: float, reorder_level: int,
                    audit_user_id: int) -> InventoryItem:
        """Create a new inventory item"""
        item = InventoryItem(
            name=name,
            description=description,
            quantity=quantity,
            unit_cost=unit_cost,
            reorder_level=reorder_level,
            last_restocked=datetime.utcnow()
        )
        self.session.add(item)

        # Add initial inventory transaction
        if quantity > 0:
            transaction = InventoryTransaction(
                inventory_item_id=item.id,
                transaction_type='initial',
                quantity=quantity,
                user_id=audit_user_id,
                notes='Initial inventory setup'
            )
            self.session.add(transaction)

        # Add audit log
        audit = AuditLog(
            user_id=audit_user_id,
            action='CREATE',
            table_name='inventory_items',
            details=f'Created inventory item: {name}'
        )
        self.session.add(audit)

        self.session.commit()
        return item

    def get_item_by_id(self, item_id: int) -> Optional[InventoryItem]:
        """Get inventory item by ID"""
        return self.session.query(InventoryItem).filter_by(id=item_id).first()

    def get_all_items(self) -> List[InventoryItem]:
        """Get all inventory items"""
        return self.session.query(InventoryItem).order_by(InventoryItem.name).all()

    def get_low_stock_items(self) -> List[InventoryItem]:
        """Get items that are below reorder level"""
        return self.session.query(InventoryItem) \
            .filter(InventoryItem.quantity <= InventoryItem.reorder_level) \
            .all()

    def update_quantity(self, item_id: int, quantity_change: int,
                        transaction_type: str, user_id: int,
                        notes: Optional[str] = None) -> Optional[InventoryItem]:
        """Update inventory quantity and record transaction"""
        item = self.get_item_by_id(item_id)
        if not item:
            return None

        # Update quantity
        item.quantity += quantity_change

        if quantity_change > 0:
            item.last_restocked = datetime.utcnow()

        # Record transaction
        transaction = InventoryTransaction(
            inventory_item_id=item_id,
            transaction_type=transaction_type,
            quantity=quantity_change,
            user_id=user_id,
            notes=notes
        )
        self.session.add(transaction)

        # Add audit log
        audit = AuditLog(
            user_id=user_id,
            action='UPDATE',
            table_name='inventory_items',
            record_id=item_id,
            details=f'Updated quantity by {quantity_change}: {transaction_type}'
        )
        self.session.add(audit)

        self.session.commit()
        return item

    def update_item(self, item_id: int, update_data: dict,
                    audit_user_id: int) -> Optional[InventoryItem]:
        """Update inventory item details"""
        item = self.get_item_by_id(item_id)
        if not item:
            return None

        for key, value in update_data.items():
            if hasattr(item, key):
                setattr(item, key, value)

        # Add audit log
        audit = AuditLog(
            user_id=audit_user_id,
            action='UPDATE',
            table_name='inventory_items',
            record_id=item_id,
            details=f'Updated item details: {update_data}'
        )
        self.session.add(audit)

        self.session.commit()
        return item

    def get_transaction_history(self, item_id: int,
                                limit: Optional[int] = None) -> List[InventoryTransaction]:
        """Get transaction history for an item"""
        query = self.session.query(InventoryTransaction) \
            .filter_by(inventory_item_id=item_id) \
            .order_by(InventoryTransaction.date.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    def get_inventory_value(self) -> float:
        """Calculate total inventory value"""
        result = self.session.query(
            func.sum(InventoryItem.quantity * InventoryItem.unit_cost)
        ).scalar()
        return float(result) if result else 0.0