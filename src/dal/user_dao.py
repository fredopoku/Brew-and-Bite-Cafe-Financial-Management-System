from typing import Optional, List
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from src.database.models import User, AuditLog, UserRole
from src.utils.logger import log_function_call


class UserDAO:
    def __init__(self, session: Session):
        self.session = session

    @log_function_call
    def create_user(self, username: str, email: str, password_hash: str, role: UserRole = UserRole.STAFF) -> User:
        """Create a new user"""
        user = User(
            username=username,
            email=email,
            password_hash=password_hash,
            role=role,
            is_active=True,
            created_at=datetime.utcnow()
        )
        self.session.add(user)

        # Add audit log
        audit = AuditLog(
            user_id=None,  # System action for new user creation
            action='CREATE',
            table_name='users',
            details=f'Created new user: {username}'
        )
        self.session.add(audit)

        self.session.commit()
        return user

    @log_function_call
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.session.query(User).filter_by(id=user_id, is_active=True).first()

    @log_function_call
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.session.query(User).filter_by(username=username, is_active=True).first()

    @log_function_call
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.session.query(User).filter_by(email=email, is_active=True).first()

    @log_function_call
    def get_users(self, search_term: Optional[str] = None, role: Optional[UserRole] = None) -> List[User]:
        """Get all active users, optionally filtered by search term and role"""
        query = self.session.query(User).filter_by(is_active=True)

        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                or_(
                    User.username.ilike(search),
                    User.email.ilike(search)
                )
            )

        if role:
            query = query.filter_by(role=role)

        return query.all()

    @log_function_call
    def update_user(self, user_id: int, update_data: dict, audit_user_id: int) -> Optional[User]:
        """Update user data"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None

        # Update user attributes
        for key, value in update_data.items():
            if hasattr(user, key) and key not in ['id', 'password_hash']:
                setattr(user, key, value)

        # Add audit log
        audit = AuditLog(
            user_id=audit_user_id,
            action='UPDATE',
            table_name='users',
            record_id=user_id,
            details=f'Updated user data: {update_data}'
        )
        self.session.add(audit)

        self.session.commit()
        return user

    @log_function_call
    def update_password(self, user_id: int, new_password_hash: str, audit_user_id: int) -> bool:
        """Update user's password"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.password_hash = new_password_hash
        user.reset_token = None
        user.reset_token_expiry = None

        # Add audit log
        audit = AuditLog(
            user_id=audit_user_id,
            action='UPDATE',
            table_name='users',
            record_id=user_id,
            details='Updated user password'
        )
        self.session.add(audit)

        self.session.commit()
        return True

    @log_function_call
    def set_reset_token(self, user_id: int, reset_token: str, expiry: datetime) -> bool:
        """Set password reset token"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.reset_token = reset_token
        user.reset_token_expiry = expiry
        self.session.commit()
        return True

    @log_function_call
    def verify_reset_token(self, reset_token: str) -> Optional[User]:
        """Verify reset token and return user if valid"""
        user = self.session.query(User).filter(
            and_(
                User.reset_token == reset_token,
                User.reset_token_expiry > datetime.utcnow(),
                User.is_active == True
            )
        ).first()
        return user

    @log_function_call
    def deactivate_user(self, user_id: int, audit_user_id: int) -> bool:
        """Deactivate a user (soft delete)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.is_active = False

        # Add audit log
        audit = AuditLog(
            user_id=audit_user_id,
            action='DEACTIVATE',
            table_name='users',
            record_id=user_id,
            details=f'Deactivated user: {user.username}'
        )
        self.session.add(audit)

        self.session.commit()
        return True

    @log_function_call
    def reactivate_user(self, user_id: int, audit_user_id: int) -> bool:
        """Reactivate a deactivated user"""
        user = self.session.query(User).filter_by(id=user_id).first()
        if not user:
            return False

        user.is_active = True

        # Add audit log
        audit = AuditLog(
            user_id=audit_user_id,
            action='REACTIVATE',
            table_name='users',
            record_id=user_id,
            details=f'Reactivated user: {user.username}'
        )
        self.session.add(audit)

        self.session.commit()
        return True

    @log_function_call
    def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False

        user.last_login = datetime.utcnow()
        self.session.commit()
        return True