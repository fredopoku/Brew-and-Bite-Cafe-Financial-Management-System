from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from src.database.models import Expense, Category, AuditLog


class ExpenseDAO:
    def __init__(self, session: Session):
        self.session = session

    def create_expense(self, user_id: int, category_id: int, amount: float,
                       description: str, expense_date: date) -> Expense:
        """Create a new expense record"""
        expense = Expense(
            user_id=user_id,
            category_id=category_id,
            amount=amount,
            description=description,
            date=expense_date,
            created_at=datetime.utcnow()
        )
        self.session.add(expense)

        # Add audit log
        audit = AuditLog(
            user_id=user_id,
            action='CREATE',
            table_name='expenses',
            details=f'Created expense: Amount {amount}, Category {category_id}'
        )
        self.session.add(audit)

        self.session.commit()
        return expense

    def get_expense_by_id(self, expense_id: int) -> Optional[Expense]:
        """Get expense by ID"""
        return self.session.query(Expense).filter_by(id=expense_id).first()

    def get_expenses_by_date_range(self, start_date: date, end_date: date,
                                   user_id: Optional[int] = None) -> List[Expense]:
        """Get expenses within a date range"""
        query = self.session.query(Expense).filter(
            Expense.date.between(start_date, end_date)
        )

        if user_id:
            query = query.filter_by(user_id=user_id)

        return query.order_by(Expense.date.desc()).all()

    def get_expenses_by_category(self, category_id: int,
                                 start_date: Optional[date] = None,
                                 end_date: Optional[date] = None) -> List[Expense]:
        """Get expenses by category with optional date range"""
        query = self.session.query(Expense).filter_by(category_id=category_id)

        if start_date and end_date:
            query = query.filter(Expense.date.between(start_date, end_date))

        return query.order_by(Expense.date.desc()).all()

    def get_total_expenses(self, start_date: date, end_date: date,
                           category_id: Optional[int] = None) -> float:
        """Get total expenses for a date range and optional category"""
        query = self.session.query(func.sum(Expense.amount)) \
            .filter(Expense.date.between(start_date, end_date))

        if category_id:
            query = query.filter_by(category_id=category_id)

        result = query.scalar()
        return float(result) if result else 0.0

    def update_expense(self, expense_id: int, update_data: dict, audit_user_id: int) -> Optional[Expense]:
        """Update expense record"""
        expense = self.get_expense_by_id(expense_id)
        if not expense:
            return None

        for key, value in update_data.items():
            if hasattr(expense, key):
                setattr(expense, key, value)

        # Add audit log
        audit = AuditLog(
            user_id=audit_user_id,
            action='UPDATE',
            table_name='expenses',
            record_id=expense_id,
            details=f'Updated expense: {update_data}'
        )
        self.session.add(audit)

        self.session.commit()
        return expense

    def delete_expense(self, expense_id: int, audit_user_id: int) -> bool:
        """Delete expense record"""
        expense = self.get_expense_by_id(expense_id)
        if not expense:
            return False

        # Add audit log before deletion
        audit = AuditLog(
            user_id=audit_user_id,
            action='DELETE',
            table_name='expenses',
            record_id=expense_id,
            details=f'Deleted expense: Amount {expense.amount}, Category {expense.category_id}'
        )
        self.session.add(audit)

        self.session.delete(expense)
        self.session.commit()
        return True

    def get_expense_summary_by_category(self, start_date: date,
                                        end_date: date) -> List[dict]:
        """Get expense summary grouped by category"""
        summary = self.session.query(
            Category.name,
            func.sum(Expense.amount).label('total_amount'),
            func.count(Expense.id).label('transaction_count')
        ).join(Category) \
            .filter(Expense.date.between(start_date, end_date)) \
            .group_by(Category.name) \
            .all()

        return [
            {
                'category': item[0],
                'total_amount': float(item[1]),
                'transaction_count': item[2]
            }
            for item in summary
        ]