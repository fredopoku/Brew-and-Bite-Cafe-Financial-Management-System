from typing import Dict, List, Optional
from datetime import datetime, date
import logging
from decimal import Decimal
from sqlalchemy.orm import Session
from src.dal.expense_dao import ExpenseDAO
from src.utils.validators import validate_amount, validate_date
from src.database.models import Category

logger = logging.getLogger(__name__)


class ExpenseService:
    def __init__(self, session: Session):
        self.session = session
        self.expense_dao = ExpenseDAO(session)

    def record_expense(self, user_id: int, category_id: int, amount: float,
                       description: str, expense_date: str = None) -> Dict:
        """Record a new expense with validation"""
        try:
            # Validate amount
            amount_valid, amount_error = validate_amount(str(amount))
            if not amount_valid:
                raise ValueError(amount_error)

            # Validate and parse date
            if expense_date:
                date_valid, date_error = validate_date(expense_date)
                if not date_valid:
                    raise ValueError(date_error)
                parsed_date = datetime.strptime(expense_date, '%Y-%m-%d').date()
            else:
                parsed_date = datetime.now().date()

            # Validate category exists
            category = self.session.query(Category).filter_by(
                id=category_id, type='expense'
            ).first()
            if not category:
                raise ValueError("Invalid expense category")

            # Record expense
            expense = self.expense_dao.create_expense(
                user_id=user_id,
                category_id=category_id,
                amount=Decimal(str(amount)),
                description=description,
                expense_date=parsed_date
            )

            logger.info(f"Expense recorded successfully: {amount} in {category.name}")

            return {
                'id': expense.id,
                'amount': float(expense.amount),
                'category': expense.category.name,
                'date': expense.date.isoformat(),
                'description': expense.description
            }

        except Exception as e:
            logger.error(f"Failed to record expense: {str(e)}")
            raise

    def get_expense_summary(self, start_date: str, end_date: str,
                            category_id: Optional[int] = None) -> Dict:
        """Get expense summary for a date range"""
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

            # Get expense summary from DAO
            summary = self.expense_dao.get_expense_summary_by_category(start, end)

            # Calculate totals
            total_amount = sum(item['total_amount'] for item in summary)
            total_transactions = sum(item['transaction_count'] for item in summary)

            return {
                'period': {
                    'start_date': start_date,
                    'end_date': end_date
                },
                'summary': {
                    'total_amount': float(total_amount),
                    'total_transactions': total_transactions,
                    'average_transaction': float(total_amount / total_transactions) if total_transactions > 0 else 0
                },
                'by_category': summary
            }

        except Exception as e:
            logger.error(f"Failed to get expense summary: {str(e)}")
            raise

    def get_expense_details(self, expense_id: int) -> Optional[Dict]:
        """Get detailed information about a specific expense"""
        try:
            expense = self.expense_dao.get_expense_by_id(expense_id)
            if not expense:
                return None

            return {
                'id': expense.id,
                'amount': float(expense.amount),
                'category': {
                    'id': expense.category.id,
                    'name': expense.category.name
                },
                'date': expense.date.isoformat(),
                'description': expense.description,
                'user': {
                    'id': expense.user.id,
                    'username': expense.user.username
                },
                'created_at': expense.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"Failed to get expense details: {str(e)}")
            raise

    def update_expense(self, expense_id: int, update_data: Dict,
                       audit_user_id: int) -> Optional[Dict]:
        """Update expense information"""
        try:
            # Validate amount if provided
            if 'amount' in update_data:
                amount_valid, amount_error = validate_amount(str(update_data['amount']))
                if not amount_valid:
                    raise ValueError(amount_error)
                update_data['amount'] = Decimal(str(update_data['amount']))

            # Validate date if provided
            if 'date' in update_data:
                date_valid, date_error = validate_date(update_data['date'])
                if not date_valid:
                    raise ValueError(date_error)
                update_data['date'] = datetime.strptime(update_data['date'], '%Y-%m-%d').date()

            # Validate category if provided
            if 'category_id' in update_data:
                category = self.session.query(Category).filter_by(
                    id=update_data['category_id'], type='expense'
                ).first()
                if not category:
                    raise ValueError("Invalid expense category")

            updated_expense = self.expense_dao.update_expense(
                expense_id, update_data, audit_user_id
            )
            if not updated_expense:
                return None

            logger.info(f"Expense {expense_id} updated successfully")

            return self.get_expense_details(expense_id)

        except Exception as e:
            logger.error(f"Failed to update expense: {str(e)}")
            raise

    def delete_expense(self, expense_id: int, audit_user_id: int) -> bool:
        """Delete an expense record"""
        try:
            if self.expense_dao.delete_expense(expense_id, audit_user_id):
                logger.info(f"Expense {expense_id} deleted successfully")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete expense: {str(e)}")
            raise

    def get_category_breakdown(self, start_date: str, end_date: str) -> List[Dict]:
        """Get expense breakdown by category for a date range"""
        try:
            # Validate dates
            for date_str in [start_date, end_date]:
                date_valid, date_error = validate_date(date_str)
                if not date_valid:
                    raise ValueError(date_error)

            # Parse dates
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()

            return self.expense_dao.get_expense_summary_by_category(start, end)

        except Exception as e:
            logger.error(f"Failed to get category breakdown: {str(e)}")
            raise