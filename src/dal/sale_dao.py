from typing import List, Optional, Dict, Tuple
from datetime import datetime, date
from sqlalchemy import func, and_, desc, asc
from sqlalchemy.orm import Session, joinedload
from src.database.models import Sale, SaleItem, InventoryItem, User, AuditLog


class SaleDAO:
    def __init__(self, session: Session):
        self.session = session

    def create_sale(self, user_id: int, items: List[Dict],
                    payment_method: str, notes: Optional[str] = None) -> Tuple[Sale, List[str]]:
        """
        Create a new sale with multiple items

        Args:
            user_id: ID of the user creating the sale
            items: List of dicts with keys: inventory_item_id, quantity, unit_price
            payment_method: Method of payment
            notes: Optional notes about the sale

        Returns:
            Tuple of (Sale object, List of warning messages)
        """
        warnings = []
        total_amount = sum(item['quantity'] * item['unit_price'] for item in items)

        # Create sale record
        sale = Sale(
            user_id=user_id,
            date=datetime.utcnow(),
            total_amount=total_amount,
            payment_method=payment_method,
            notes=notes
        )
        self.session.add(sale)
        self.session.flush()  # Get sale ID without committing

        # Create sale items and update inventory
        for item in items:
            inventory_item = self.session.query(InventoryItem) \
                .filter_by(id=item['inventory_item_id']).with_for_update().first()

            if not inventory_item:
                raise ValueError(f"Inventory item {item['inventory_item_id']} not found")

            if inventory_item.quantity < item['quantity']:
                raise ValueError(
                    f"Insufficient stock for {inventory_item.name}. "
                    f"Available: {inventory_item.quantity}, Requested: {item['quantity']}"
                )

            # Create sale item
            sale_item = SaleItem(
                sale_id=sale.id,
                inventory_item_id=item['inventory_item_id'],
                quantity=item['quantity'],
                unit_price=item['unit_price']
            )
            self.session.add(sale_item)

            # Update inventory
            inventory_item.quantity -= item['quantity']

            # Check if stock is low after sale
            if inventory_item.quantity <= inventory_item.reorder_level:
                warnings.append(
                    f"Low stock alert: {inventory_item.name} "
                    f"(Current stock: {inventory_item.quantity})"
                )

            # Add inventory transaction audit
            audit = AuditLog(
                user_id=user_id,
                action='UPDATE',
                table_name='inventory_items',
                record_id=inventory_item.id,
                details=(f'Reduced quantity by {item["quantity"]} '
                         f'due to sale {sale.id}')
            )
            self.session.add(audit)

        # Add sale audit log
        audit = AuditLog(
            user_id=user_id,
            action='CREATE',
            table_name='sales',
            record_id=sale.id,
            details=f'Created sale: Total amount {total_amount}'
        )
        self.session.add(audit)

        self.session.commit()
        return sale, warnings

    def get_sale_by_id(self, sale_id: int) -> Optional[Sale]:
        """Get detailed sale information by ID"""
        return self.session.query(Sale) \
            .options(
            joinedload(Sale.user),
            joinedload(Sale.sale_items).joinedload(SaleItem.inventory_item)
        ) \
            .filter_by(id=sale_id) \
            .first()

    def get_sales_by_date_range(self, start_date: date, end_date: date,
                                user_id: Optional[int] = None,
                                payment_method: Optional[str] = None) -> List[Sale]:
        """Get sales within a date range with optional filters"""
        query = self.session.query(Sale) \
            .options(joinedload(Sale.sale_items)) \
            .filter(and_(
            func.date(Sale.date) >= start_date,
            func.date(Sale.date) <= end_date
        ))

        if user_id:
            query = query.filter_by(user_id=user_id)
        if payment_method:
            query = query.filter_by(payment_method=payment_method)

        return query.order_by(desc(Sale.date)).all()

    def get_daily_sales_summary(self, target_date: date) -> Dict:
        """Generate detailed daily sales summary"""
        # Get total sales and transaction count
        daily_stats = self.session.query(
            func.sum(Sale.total_amount).label('total_amount'),
            func.count(Sale.id).label('transaction_count'),
            func.avg(Sale.total_amount).label('average_sale')
        ).filter(func.date(Sale.date) == target_date).first()

        # Get hourly breakdown
        hourly_sales = self.session.query(
            func.extract('hour', Sale.date).label('hour'),
            func.sum(Sale.total_amount).label('amount'),
            func.count(Sale.id).label('count')
        ).filter(func.date(Sale.date) == target_date) \
            .group_by(func.extract('hour', Sale.date)) \
            .all()

        # Get payment methods breakdown
        payment_methods = self.session.query(
            Sale.payment_method,
            func.sum(Sale.total_amount).label('amount'),
            func.count(Sale.id).label('count')
        ).filter(func.date(Sale.date) == target_date) \
            .group_by(Sale.payment_method) \
            .all()

        # Get top-selling items
        top_items = self.session.query(
            InventoryItem.name,
            func.sum(SaleItem.quantity).label('quantity'),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label('revenue')
        ).join(SaleItem.inventory_item) \
            .join(Sale) \
            .filter(func.date(Sale.date) == target_date) \
            .group_by(InventoryItem.name) \
            .order_by(desc(func.sum(SaleItem.quantity * SaleItem.unit_price))) \
            .limit(10) \
            .all()

        # Get staff performance
        staff_performance = self.session.query(
            User.username,
            func.count(Sale.id).label('sales_count'),
            func.sum(Sale.total_amount).label('total_sales')
        ).join(Sale.user) \
            .filter(func.date(Sale.date) == target_date) \
            .group_by(User.username) \
            .all()

        return {
            'date': target_date,
            'summary': {
                'total_sales': float(daily_stats[0]) if daily_stats[0] else 0.0,
                'transaction_count': daily_stats[1] or 0,
                'average_sale': float(daily_stats[2]) if daily_stats[2] else 0.0
            },
            'hourly_sales': [
                {
                    'hour': int(hour[0]),
                    'amount': float(hour[1]),
                    'count': hour[2]
                }
                for hour in hourly_sales
            ],
            'payment_methods': [
                {
                    'method': pm[0],
                    'amount': float(pm[1]),
                    'count': pm[2]
                }
                for pm in payment_methods
            ],
            'top_items': [
                {
                    'name': item[0],
                    'quantity': item[1],
                    'revenue': float(item[2])
                }
                for item in top_items
            ],
            'staff_performance': [
                {
                    'username': perf[0],
                    'sales_count': perf[1],
                    'total_sales': float(perf[2])
                }
                for perf in staff_performance
            ]
        }

    def get_sales_report(self, start_date: date, end_date: date,
                         group_by: str = 'day') -> Dict:
        """
        Generate comprehensive sales report for a date range
        group_by: 'day', 'week', or 'month'
        """
        if group_by == 'day':
            date_group = func.date(Sale.date)
        elif group_by == 'week':
            date_group = func.date_trunc('week', Sale.date)
        elif group_by == 'month':
            date_group = func.date_trunc('month', Sale.date)
        else:
            raise ValueError("group_by must be 'day', 'week', or 'month'")

        # Get grouped sales totals
        sales_over_time = self.session.query(
            date_group.label('date'),
            func.sum(Sale.total_amount).label('total_amount'),
            func.count(Sale.id).label('transaction_count'),
            func.avg(Sale.total_amount).label('average_sale')
        ).filter(and_(
            func.date(Sale.date) >= start_date,
            func.date(Sale.date) <= end_date
        )) \
            .group_by(date_group) \
            .order_by(asc('date')) \
            .all()

        # Get category sales
        category_sales = self.session.query(
            InventoryItem.name,
            func.sum(SaleItem.quantity).label('quantity'),
            func.sum(SaleItem.quantity * SaleItem.unit_price).label('revenue')
        ).join(SaleItem.inventory_item) \
            .join(Sale) \
            .filter(and_(
            func.date(Sale.date) >= start_date,
            func.date(Sale.date) <= end_date
        )) \
            .group_by(InventoryItem.name) \
            .order_by(desc(func.sum(SaleItem.quantity * SaleItem.unit_price))) \
            .all()

        # Calculate summary statistics
        total_stats = self.session.query(
            func.sum(Sale.total_amount).label('total_revenue'),
            func.count(Sale.id).label('total_transactions'),
            func.avg(Sale.total_amount).label('average_transaction')
        ).filter(and_(
            func.date(Sale.date) >= start_date,
            func.date(Sale.date) <= end_date
        )).first()

        return {
            'period': {
                'start_date': start_date,
                'end_date': end_date,
                'grouping': group_by
            },
            'summary': {
                'total_revenue': float(total_stats[0]) if total_stats[0] else 0.0,
                'total_transactions': total_stats[1] or 0,
                'average_transaction': float(total_stats[2]) if total_stats[2] else 0.0
            },
            'sales_over_time': [
                {
                    'date': sale[0],
                    'total_amount': float(sale[1]),
                    'transaction_count': sale[2],
                    'average_sale': float(sale[3]) if sale[3] else 0.0
                }
                for sale in sales_over_time
            ],
            'category_sales': [
                {
                    'name': cat[0],
                    'quantity': cat[1],
                    'revenue': float(cat[2])
                }
                for cat in category_sales
            ]
        }

    def void_sale(self, sale_id: int, user_id: int, reason: str) -> bool:
        """Void a sale and restore inventory"""
        sale = self.get_sale_by_id(sale_id)
        if not sale:
            return False

        # Restore inventory quantities
        for sale_item in sale.sale_items:
            inventory_item = sale_item.inventory_item
            inventory_item.quantity += sale_item.quantity

            # Add inventory adjustment audit
            audit = AuditLog(
                user_id=user_id,
                action='UPDATE',
                table_name='inventory_items',
                record_id=inventory_item.id,
                details=f'Restored quantity {sale_item.quantity} due to void of sale {sale_id}'
            )
            self.session.add(audit)

        # Add void audit log
        audit = AuditLog(
            user_id=user_id,
            action='VOID',
            table_name='sales',
            record_id=sale_id,
            details=f'Voided sale: {reason}'
        )
        self.session.add(audit)

        # Delete sale items and sale
        for sale_item in sale.sale_items:
            self.session.delete(sale_item)
        self.session.delete(sale)

        self.session.commit()
        return True