from typing import Dict, List, Optional, Tuple
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from src import validate_amount, validate_quantity, validate_date
from src.dal.sale_dao import SaleDAO
from src.dal.inventory_dao import InventoryDAO
from src.database import Sale
from src.utils import logger


class SalesService:
    def __init__(self, session: Session):
        self.session = session
        self.sale_dao = SaleDAO(session)
        self.inventory_dao = InventoryDAO(session)

    def create_sale(self, user_id: int, items: List[Dict],
                    payment_method: str, notes: Optional[str] = None) -> Tuple[Dict, List[str]]:
        """
        Create a new sale with validation

        Args:
            user_id: ID of the user creating the sale
            items: List of dicts with keys: inventory_item_id, quantity, unit_price
            payment_method: Method of payment
            notes: Optional notes about the sale

        Returns:
            Tuple of (sale details, warning messages)
        """
        try:
            warnings = []

            # Validate items
            for item in items:
                # Validate quantity
                quantity_valid, quantity_error = validate_quantity(str(item['quantity']))
                if not quantity_valid:
                    raise ValueError(f"Invalid quantity for item {item['inventory_item_id']}: {quantity_error}")

                # Validate unit price
                price_valid, price_error = validate_amount(str(item['unit_price']))
                if not price_valid:
                    raise ValueError(f"Invalid unit price for item {item['inventory_item_id']}: {price_error}")

                # Check inventory availability
                inventory_item = self.inventory_dao.get_item_by_id(item['inventory_item_id'])
                if not inventory_item:
                    raise ValueError(f"Invalid inventory item ID: {item['inventory_item_id']}")

                if inventory_item.quantity < item['quantity']:
                    raise ValueError(
                        f"Insufficient stock for {inventory_item.name}. "
                        f"Available: {inventory_item.quantity}, Requested: {item['quantity']}"
                    )

                # Convert to Decimal for precise calculations
                item['unit_price'] = Decimal(str(item['unit_price']))

            # Create sale
            sale, sale_warnings = self.sale_dao.create_sale(
                user_id=user_id,
                items=items,
                payment_method=payment_method,
                notes=notes
            )

            warnings.extend(sale_warnings)

            return self._format_sale_response(sale), warnings

        except Exception as e:
            logger.error(f"Failed to create sale: {str(e)}")
            raise

    def _format_sale_response(self, sale: Sale) -> Dict:
        """Format sale object for response"""
        return {
            'id': sale.id,
            'date': sale.date.isoformat(),
            'total_amount': float(sale.total_amount),
            'payment_method': sale.payment_method,
            'notes': sale.notes,
            'items': [
                {
                    'inventory_item': {
                        'id': item.inventory_item.id,
                        'name': item.inventory_item.name
                    },
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'subtotal': float(item.quantity * item.unit_price)
                }
                for item in sale.sale_items
            ],
            'user': {
                'id': sale.user.id,
                'username': sale.user.username
            }
        }

    def get_sale_details(self, sale_id: int) -> Optional[Dict]:
        """Get detailed information about a specific sale"""
        try:
            sale = self.sale_dao.get_sale_by_id(sale_id)
            if not sale:
                return None

            return self._format_sale_response(sale)

        except Exception as e:
            logger.error(f"Failed to get sale details: {str(e)}")
            raise

    def void_sale(self, sale_id: int, user_id: int, reason: str) -> bool:
        """Void a sale and restore inventory"""
        try:
            return self.sale_dao.void_sale(sale_id, user_id, reason)

        except Exception as e:
            logger.error(f"Failed to void sale: {str(e)}")
            raise

    def get_daily_sales_summary(self, target_date: str) -> Dict:
        """Get detailed sales summary for a specific date"""
        try:
            # Validate date
            date_valid, date_error = validate_date(target_date)
            if not date_valid:
                raise ValueError(date_error)

            parsed_date = datetime.strptime(target_date, '%Y-%m-%d').date()

            return self.sale_dao.get_daily_sales_summary(parsed_date)

        except Exception as e:
            logger.error(f"Failed to get daily sales summary: {str(e)}")
            raise

    def get_sales_report(self, start_date: str, end_date: str,
                         group_by: str = 'day') -> Dict:
        """Generate comprehensive sales report"""
        try:
            # Validate dates
            for date_str in [start_date, end_date]:
                date_valid, date_error = validate_date(date_str)
                if not date_valid:
                    raise ValueError(date_error)

            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()

            if start > end:
                raise ValueError("Start date must be before end date")

            # Validate grouping
            valid_groupings = ['day', 'week', 'month']
            if group_by not in valid_groupings:
                raise ValueError(f"Invalid grouping. Must be one of: {', '.join(valid_groupings)}")

            return self.sale_dao.get_sales_report(start, end, group_by)

        except Exception as e:
            logger.error(f"Failed to generate sales report: {str(e)}")
            raise

    def get_top_selling_items(self, start_date: str, end_date: str,
                              limit: int = 10) -> List[Dict]:
        """Get top-selling items for a date range"""
        try:
            # Validate dates
            for date_str in [start_date, end_date]:
                date_valid, date_error = validate_date(date_str)
                if not date_valid:
                    raise ValueError(date_error)

            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()

            return self.sale_dao.get_top_selling_items(start, end, limit)

        except Exception as e:
            logger.error(f"Failed to get top selling items: {str(e)}")
            raise