from typing import Optional, Dict, List
from datetime import datetime, timedelta
import logging
from sqlalchemy.orm import Session
from src.dal.user_dao import UserDAO
from src.utils.security import hash_password, verify_password, generate_reset_token
from src.utils.validators import validate_email, validate_password, validate_username
from src.database.models import UserRole
from src.config import PASSWORD_RESET_TIMEOUT_DAYS

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, session: Session):
        self.session = session
        self.user_dao = UserDAO(session)

    def register_user(self, username: str, email: str, password: str,
                      role: UserRole = UserRole.STAFF) -> Dict:
        """Register a new user with validation"""
        try:
            # Validate input
            username_valid, username_error = validate_username(username)
            if not username_valid:
                raise ValueError(username_error)

            email_valid, email_error = validate_email(email)
            if not email_valid:
                raise ValueError(email_error)

            password_valid, password_error = validate_password(password)
            if not password_valid:
                raise ValueError(password_error)

            # Check if username or email already exists
            if self.user_dao.get_user_by_username(username):
                raise ValueError("Username already exists")

            if self.user_dao.get_user_by_email(email):
                raise ValueError("Email already exists")

            # Create user
            hashed_password = hash_password(password)
            user = self.user_dao.create_user(username, email, hashed_password, role)

            logger.info(f"Successfully registered new user: {username}")

            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'created_at': user.created_at.isoformat()
            }

        except Exception as e:
            logger.error(f"User registration failed: {str(e)}")
            raise

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data if successful"""
        try:
            user = self.user_dao.get_user_by_username(username)

            if not user:
                logger.warning(f"Authentication failed: User not found - {username}")
                return None

            if not verify_password(password, user.password_hash):
                logger.warning(f"Authentication failed: Invalid password - {username}")
                return None

            # Update last login time
            self.user_dao.update_last_login(user.id)

            logger.info(f"User authenticated successfully: {username}")

            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'last_login': user.last_login.isoformat()
            }

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise

    def initiate_password_reset(self, email: str) -> Optional[str]:
        """Initiate password reset process"""
        try:
            user = self.user_dao.get_user_by_email(email)
            if not user:
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return None

            # Generate reset token
            reset_token = generate_reset_token()
            expiry = datetime.utcnow() + timedelta(days=PASSWORD_RESET_TIMEOUT_DAYS)

            # Save token to database
            if self.user_dao.set_reset_token(user.id, reset_token, expiry):
                logger.info(f"Password reset initiated for user: {user.username}")
                return reset_token

            return None

        except Exception as e:
            logger.error(f"Password reset initiation failed: {str(e)}")
            raise

    def reset_password(self, reset_token: str, new_password: str) -> bool:
        """Reset user password using reset token"""
        try:
            user = self.user_dao.verify_reset_token(reset_token)
            if not user:
                logger.warning("Invalid or expired reset token")
                return False

            # Validate new password
            password_valid, password_error = validate_password(new_password)
            if not password_valid:
                raise ValueError(password_error)

            # Update password
            new_password_hash = hash_password(new_password)
            if self.user_dao.update_password(user.id, new_password_hash, user.id):
                logger.info(f"Password reset successful for user: {user.username}")
                return True

            return False

        except Exception as e:
            logger.error(f"Password reset failed: {str(e)}")
            raise

    def change_password(self, user_id: int, current_password: str,
                        new_password: str) -> bool:
        """Change user password"""
        try:
            user = self.user_dao.get_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")

            # Verify current password
            if not verify_password(current_password, user.password_hash):
                raise ValueError("Current password is incorrect")

            # Validate new password
            password_valid, password_error = validate_password(new_password)
            if not password_valid:
                raise ValueError(password_error)

            # Update password
            new_password_hash = hash_password(new_password)
            if self.user_dao.update_password(user_id, new_password_hash, user_id):
                logger.info(f"Password changed successfully for user: {user.username}")
                return True

            return False

        except Exception as e:
            logger.error(f"Password change failed: {str(e)}")
            raise

    def update_user_profile(self, user_id: int, update_data: Dict,
                            audit_user_id: int) -> Optional[Dict]:
        """Update user profile information"""
        try:
            # Validate email if being updated
            if 'email' in update_data:
                email_valid, email_error = validate_email(update_data['email'])
                if not email_valid:
                    raise ValueError(email_error)

                # Check if email is already taken
                existing_user = self.user_dao.get_user_by_email(update_data['email'])
                if existing_user and existing_user.id != user_id:
                    raise ValueError("Email already in use")

            updated_user = self.user_dao.update_user(user_id, update_data, audit_user_id)
            if not updated_user:
                return None

            logger.info(f"Profile updated for user: {updated_user.username}")

            return {
                'id': updated_user.id,
                'username': updated_user.username,
                'email': updated_user.email,
                'role': updated_user.role.value,
                'last_login': updated_user.last_login.isoformat() if updated_user.last_login else None
            }

        except Exception as e:
            logger.error(f"Profile update failed: {str(e)}")
            raise