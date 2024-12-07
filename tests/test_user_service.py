"""
Tests for user service functionality.
"""

import pytest
from datetime import datetime
from src.database.models import UserRole
from src.utils.security import verify_password


def test_create_user(user_service):
    """Test user creation"""
    user_data = {
        'username': 'newuser',
        'email': 'newuser@test.com',
        'password': 'Password123!',
        'role': UserRole.STAFF
    }

    # Create user
    user = user_service.create_user(**user_data)

    assert user is not None
    assert user['username'] == user_data['username']
    assert user['email'] == user_data['email']
    assert user['role'] == UserRole.STAFF.value
    assert user['is_active'] is True


def test_create_user_validation(user_service):
    """Test user creation validation"""
    # Test invalid username
    with pytest.raises(ValueError) as exc:
        user_service.create_user(
            username="us",  # Too short
            email="test@test.com",
            password="Password123!",
            role=UserRole.STAFF
        )
    assert "Username must be" in str(exc.value)

    # Test invalid email
    with pytest.raises(ValueError) as exc:
        user_service.create_user(
            username="validuser",
            email="invalid-email",
            password="Password123!",
            role=UserRole.STAFF
        )
    assert "Invalid email format" in str(exc.value)

    # Test weak password
    with pytest.raises(ValueError) as exc:
        user_service.create_user(
            username="validuser",
            email="test@test.com",
            password="weak",
            role=UserRole.STAFF
        )
    assert "Password must" in str(exc.value)


def test_authenticate_user(user_service):
    """Test user authentication"""
    # Create test user
    user_data = {
        'username': 'authuser',
        'email': 'auth@test.com',
        'password': 'Password123!',
        'role': UserRole.STAFF
    }
    user_service.create_user(**user_data)

    # Test valid authentication
    auth_result = user_service.authenticate_user(
        username=user_data['username'],
        password=user_data['password']
    )

    assert auth_result is not None
    assert auth_result['username'] == user_data['username']
    assert auth_result['last_login'] is not None

    # Test invalid password
    auth_result = user_service.authenticate_user(
        username=user_data['username'],
        password="wrong-password"
    )
    assert auth_result is None

    # Test non-existent user
    auth_result = user_service.authenticate_user(
        username="nonexistent",
        password="Password123!"
    )
    assert auth_result is None


def test_change_password(user_service):
    """Test password change functionality"""
    # Create test user
    user_data = {
        'username': 'pwduser',
        'email': 'pwd@test.com',
        'password': 'Password123!',
        'role': UserRole.STAFF
    }
    user = user_service.create_user(**user_data)

    # Change password
    result = user_service.change_password(
        user_id=user['id'],
        current_password=user_data['password'],
        new_password='NewPassword123!'
    )

    assert result is True

    # Verify new password works
    auth_result = user_service.authenticate_user(
        username=user_data['username'],
        password='NewPassword123!'
    )
    assert auth_result is not None

    # Verify old password doesn't work
    auth_result = user_service.authenticate_user(
        username=user_data['username'],
        password=user_data['password']
    )
    assert auth_result is None


def test_update_user_profile(user_service):
    """Test user profile update"""
    # Create test user
    user_data = {
        'username': 'updateuser',
        'email': 'update@test.com',
        'password': 'Password123!',
        'role': UserRole.STAFF
    }
    user = user_service.create_user(**user_data)

    # Update profile
    update_data = {
        'email': 'newemail@test.com',
        'role': UserRole.MANAGER
    }

    updated_user = user_service.update_user_profile(
        user_id=user['id'],
        update_data=update_data,
        audit_user_id=1
    )

    assert updated_user is not None
    assert updated_user['email'] == update_data['email']
    assert updated_user['role'] == UserRole.MANAGER.value


def test_deactivate_reactivate_user(user_service):
    """Test user deactivation and reactivation"""
    # Create test user
    user_data = {
        'username': 'statususer',
        'email': 'status@test.com',
        'password': 'Password123!',
        'role': UserRole.STAFF
    }
    user = user_service.create_user(**user_data)

    # Deactivate user
    result = user_service.deactivate_user(
        user_id=user['id'],
        audit_user_id=1
    )
    assert result is True

    # Verify deactivated user can't login
    auth_result = user_service.authenticate_user(
        username=user_data['username'],
        password=user_data['password']
    )
    assert auth_result is None

    # Reactivate user
    result = user_service.reactivate_user(
        user_id=user['id'],
        audit_user_id=1
    )
    assert result is True

    # Verify reactivated user can login
    auth_result = user_service.authenticate_user(
        username=user_data['username'],
        password=user_data['password']
    )
    assert auth_result is not None


def test_get_user_by_id(user_service):
    """Test retrieving user by ID"""
    # Create test user
    user_data = {
        'username': 'getuser',
        'email': 'get@test.com',
        'password': 'Password123!',
        'role': UserRole.STAFF
    }
    created_user = user_service.create_user(**user_data)

    # Get user by ID
    user = user_service.get_user_by_id(created_user['id'])

    assert user is not None
    assert user['username'] == user_data['username']
    assert user['email'] == user_data['email']

    # Test non-existent user
    user = user_service.get_user_by_id(9999)
    assert user is None