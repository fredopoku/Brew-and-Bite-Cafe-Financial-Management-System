from typing import Optional, Dict, Tuple
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import User, UserRole
from src.dal.user_dao import UserDAO
from src.utils.security import hash_password, verify_password, generate_reset_token
from src.config import SESSION_TIMEOUT_MINUTES

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, session: Session):
        self.session = session
        self.user_dao = UserDAO(session)
        self._active_sessions = {}  # Store active user sessions

    def login(self, username: str, password: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Authenticate user and create a session

        Returns:
            Tuple of (success, user_data, error_message)
        """
        try:
            user = self.user_dao.get_user_by_username(username)

            if not user:
                return False, None, "Invalid username or password"

            if not user.is_active:
                return False, None, "Account is deactivated"

            if not verify_password(password, user.password_hash):
                return False, None, "Invalid username or password"

            # Update last login
            self.user_dao.update_last_login(user.id)

            # Create session
            session_data = self._create_session(user)

            logger.info(f"User logged in successfully: {username}")
            return True, session_data, None

        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False, None, f"Login failed: {str(e)}"

    def _create_session(self, user: User) -> Dict:
        """Create a new session for user"""
        session_data = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'created_at': datetime.utcnow(),
            'expires_at': datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
        }

        self._active_sessions[user.id] = session_data
        return session_data

    def logout(self, user_id: int) -> bool:
        """Log out user and invalidate session"""
        try:
            if user_id in self._active_sessions:
                del self._active_sessions[user_id]
                logger.info(f"User logged out successfully: {user_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            return False

    def validate_session(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Validate user session
        Returns: (is_valid, error_message)
        """
        try:
            session = self._active_sessions.get(user_id)
            if not session:
                return False, "No active session found"

            if datetime.utcnow() > session['expires_at']:
                self.logout(user_id)
                return False, "Session expired"

            # Extend session
            session['expires_at'] = datetime.utcnow() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
            return True, None

        except Exception as e:
            logger.error(f"Session validation failed: {str(e)}")
            return False, f"Session validation failed: {str(e)}"

    def check_permission(self, user_id: int, required_role: UserRole) -> Tuple[bool, Optional[str]]:
        """
        Check if user has required role
        Returns: (has_permission, error_message)
        """
        try:
            # Validate session first
            session_valid, error = self.validate_session(user_id)
            if not session_valid:
                return False, error

            session = self._active_sessions.get(user_id)
            user_role = UserRole(session['role'])

            # Admin has access to everything
            if user_role == UserRole.ADMIN:
                return True, None

            # Check role hierarchy
            role_hierarchy = {
                UserRole.ADMIN: 3,
                UserRole.MANAGER: 2,
                UserRole.STAFF: 1
            }

            if role_hierarchy[user_role] >= role_hierarchy[required_role]:
                return True, None

            return False, "Insufficient permissions"

        except Exception as e:
            logger.error(f"Permission check failed: {str(e)}")
            return False, f"Permission check failed: {str(e)}"

    def get_user_permissions(self, user_id: int) -> Dict:
        """Get user's permissions"""
        try:
            session = self._active_sessions.get(user_id)
            if not session:
                return {}

            user_role = UserRole(session['role'])

            # Define permissions based on role
            base_permissions = {
                'view_sales': True,
                'view_inventory': True,
                'view_expenses': True
            }

            manager_permissions = {
                **base_permissions,
                'manage_inventory': True,
                'manage_expenses': True,
                'view_reports': True,
                'manage_sales': True
            }

            admin_permissions = {
                **manager_permissions,
                'manage_users': True,
                'manage_settings': True,
                'view_audit_logs': True,
                'export_data': True
            }

            if user_role == UserRole.ADMIN:
                return admin_permissions
            elif user_role == UserRole.MANAGER:
                return manager_permissions
            else:
                return base_permissions

        except Exception as e:
            logger.error(f"Failed to get user permissions: {str(e)}")
            return {}

    def change_user_role(self, admin_user_id: int, target_user_id: int,
                         new_role: UserRole) -> Tuple[bool, Optional[str]]:
        """Change user's role (admin only)"""
        try:
            # Verify admin permissions
            has_permission, error = self.check_permission(admin_user_id, UserRole.ADMIN)
            if not has_permission:
                return False, error

            # Update user role
            result = self.user_dao.update_user(
                target_user_id,
                {'role': new_role},
                admin_user_id
            )

            if result:
                # Update session if user is logged in
                if target_user_id in self._active_sessions:
                    self._active_sessions[target_user_id]['role'] = new_role.value

                logger.info(f"User role updated: {target_user_id} to {new_role.value}")
                return True, None

            return False, "Failed to update user role"

        except Exception as e:
            logger.error(f"Role change failed: {str(e)}")
            return False, f"Role change failed: {str(e)}"

    def clean_expired_sessions(self):
        """Clean up expired sessions"""
        try:
            current_time = datetime.utcnow()
            expired_sessions = [
                user_id for user_id, session in self._active_sessions.items()
                if session['expires_at'] < current_time
            ]

            for user_id in expired_sessions:
                self.logout(user_id)

            if expired_sessions:
                logger.info(f"Cleaned {len(expired_sessions)} expired sessions")

        except Exception as e:
            logger.error(f"Session cleanup failed: {str(e)}")