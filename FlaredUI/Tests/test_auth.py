import pytest

from FlaredUI.Modules.DB import db
from FlaredUI.Modules.Auth import userpass_login, userpass_logout, oauth, create_oauth
from FlaredUI.Modules.DB import User
from unittest.mock import patch
from flask import redirect, url_for


# Test User/Password Authentication
def test_userpass_login_success(client, init_db):
    # Create a test user in the database
    user_data = {'username': 'testuser', 'email': 'testuser@example.com', 'password': 'testpassword'}
    User.create_user(user_data)

    # Send a login request
    response = client.post('/api/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })

    assert response.status_code == 302  # Expect a redirect after successful login
    assert b'Login successful' in response.data


def test_userpass_login_failure(client, init_db):
    # Create a test user in the database
    user_data = {'username': 'testuser', 'email': 'testuser@example.com', 'password': 'testpassword'}
    User.create_user(user_data)

    response = client.post('/api/auth/login', data={
        'username': 'testuser',
        'password': 'wrongpassword'
    })

    assert response.status_code == 401
    assert b'Invalid credentials' in response.data


# Test OAuth Authentication (Mock)
@patch('Backend.Modules.Auth.oauth_login')
def test_oauth_login(mock_oauth_login, client):
    # Mock the oauth_login function to return a redirect response
    mock_oauth_login.return_value = redirect(url_for('index'))

    response = client.get('/api/auth/oauth/github')  # Test GitHub OAuth
    assert response.status_code == 302


# TODO: Add more tests for other OAuth providers and error cases

@pytest.fixture
def authenticated_user(client):
    """Fixture to create and log in a test user."""
    user_data = {'username': 'testuser', 'email': 'testuser@example.com', 'password': 'testpassword'}
    user = User.create_user(user_data)
    with client.session_transaction() as session:
        session['_user_id'] = user.id  # Simulate login
    return user


def test_logout(client, authenticated_user):
    """Test logging out a user."""
    response = client.get('/api/auth/logout')
    assert response.status_code == 302  # Expect a redirect after logout
    assert b'Logged out' in response.data
