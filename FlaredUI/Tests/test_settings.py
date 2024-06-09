import pytest
from unittest.mock import patch

from FlaredUI.Modules.DB import (
    db, create_app_setting, get_all_app_settings,
    get_app_setting_by_id, get_app_setting_by_name,
    update_app_setting, delete_app_setting, User, Settings
)


@pytest.fixture
def authenticated_user(client):
    user_data = {'username': 'testuser', 'email': 'testuser@example.com', 'password': 'testpassword'}
    user = User.create_user(user_data)
    with client.session_transaction() as session:
        session['_user_id'] = user.id  # Simulate login
    return user


# Test create_app_setting
def test_create_app_setting(client, authenticated_user, init_db):
    with patch('Backend.Modules.DB.Settings.current_user', authenticated_user):
        data = {'name': 'test_setting', 'value': 'test_value'}
        response = client.post('/api/settings', json=data)
        assert response.status_code == 201
        data = response.json
        assert data['name'] == 'test_setting'
        assert data['value'] == 'test_value'


# Test get_all_app_settings
def test_get_all_app_settings(client, authenticated_user, init_db):
    with patch('Backend.Modules.DB.Settings.current_user', authenticated_user):
        settings = Settings.get_all_app_settings()
        response = client.get('/api/settings')
        assert response.status_code == 200
        data = response.json
        assert len(data) == len(settings)

# Test get_app_setting_by_id
def test_get_app_setting_by_id(client, authenticated_user, init_db):
    with patch('Backend.Modules.DB.Settings.current_user', authenticated_user):
        setting = create_app_setting({'name': 'test_setting', 'value': 'test_value', 'modified_by': authenticated_user.id})
        response = client.get(f'/api/settings/{setting.id}')
        assert response.status_code == 200
        data = response.json
        assert data['name'] == 'test_setting'
        assert data['value'] == 'test_value'

# Test get_app_setting_by_name
def test_get_app_setting_by_name(client, authenticated_user, init_db):
    with patch('Backend.Modules.DB.Settings.current_user', authenticated_user):
        setting = create_app_setting({'name': 'test_setting', 'value': 'test_value', 'modified_by': authenticated_user.id})
        response = client.get('/api/settings', query_string={'name': 'test_setting'})
        assert response.status_code == 200
        data = response.json
        assert data['name'] == 'test_setting'
        assert data['value'] == 'test_value'
