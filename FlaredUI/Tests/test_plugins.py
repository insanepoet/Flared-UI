import pytest
from unittest.mock import patch

from FlaredUI.Modules.DB import (
    create_plugin_repo, get_plugin_repos, get_plugin_repo_by_id,
    update_plugin_repo, delete_plugin_repo, create_plugin,
    get_plugins, get_plugin_by_id, PluginRepository,
    Plugin, User, db
)


# Fixtures
@pytest.fixture
def authenticated_user(client):
    user_data = {'username': 'testuser', 'email': 'testuser@example.com', 'password': 'testpassword'}
    user = User.create_user(user_data)
    with client.session_transaction() as session:
        session['_user_id'] = user.id  # Simulate login
    return user


@pytest.fixture
def test_repo(init_db):
    repo = PluginRepository(name='Test Repo', url='https://example.com/repo')
    db.session.add(repo)
    db.session.commit()
    return repo


# --- Plugin Repository Tests ---

def test_create_plugin_repo(client, authenticated_user, init_db):
    with patch('Backend.Modules.DB.Plugins.current_user', authenticated_user):
        data = {'name': 'New Repo', 'url': 'https://newrepo.com'}
        response = client.post('/api/plugins/repositories', json=data)
        assert response.status_code == 201
        data = response.json
        assert data['name'] == 'New Repo'


def test_list_plugin_repositories(client, test_repo, init_db):
    response = client.get('/api/plugins/repositories')
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]['name'] == 'Test Repo'


# Test get_plugin_repo_by_id
def test_get_plugin_repo_by_id(client, test_repo, init_db):
    response = client.get(f'/api/plugins/repositories/{test_repo.id}')
    assert response.status_code == 200
    data = response.json
    assert data['id'] == test_repo.id
    assert data['name'] == 'Test Repo'
    assert data['url'] == 'https://example.com/repo'


# Test update_plugin_repo
def test_update_plugin_repo(client, test_repo, init_db):
    updated_data = {'name': 'Updated Repo Name', 'url': 'https://updatedrepo.com'}
    response = client.put(f'/api/plugins/repositories/{test_repo.id}', json=updated_data)
    assert response.status_code == 200
    data = response.json
    assert data['name'] == 'Updated Repo Name'
    assert data['url'] == 'https://updatedrepo.com'


# Test delete_plugin_repo
def test_delete_plugin_repo(client, test_repo, init_db):
    response = client.delete(f'/api/plugins/repositories/{test_repo.id}')
    assert response.status_code == 200
    assert response.json == {'message': f"Plugin repository '{test_repo.name}' deleted"}

    # Verify repo is deleted from the database
    deleted_repo = PluginRepository.query.get(test_repo.id)
    assert deleted_repo is None


# --- Plugin Tests ---
def test_create_plugin(client, authenticated_user, test_repo, init_db):
    with patch('Backend.Modules.DB.Plugins.current_user', authenticated_user):
        data = {'name': 'Test Plugin', 'type': 'backend', 'repository_id': test_repo.id}
        response = client.post('/api/plugins/', json=data)
        assert response.status_code == 201
        data = response.json
        assert data['name'] == 'Test Plugin'


# Test get_plugin_by_id
def test_get_plugin_by_id(client, test_plugin, init_db):
    response = client.get(f'/api/plugins/{test_plugin.id}')
    assert response.status_code == 200
    data = response.json
    assert data['id'] == test_plugin.id
    assert data['name'] == 'Test Plugin'
    assert data['type'] == 'backend'


# Test get_plugins
def test_get_plugins(client, test_plugin, init_db):
    response = client.get('/api/plugins/')
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]['name'] == 'Test Plugin'


# Test update_plugin
def test_update_plugin(client, authenticated_user, test_plugin, init_db):
    with patch('Backend.Modules.DB.Plugins.current_user', authenticated_user):
        updated_data = {'name': 'Updated Plugin Name', 'version': '1.1.0'}
        response = client.put(f'/api/plugins/{test_plugin.id}', json=updated_data)
        assert response.status_code == 200
        data = response.json
        assert data['name'] == 'Updated Plugin Name'
        assert data['version'] == '1.1.0'


# Test delete_plugin
def test_delete_plugin(client, authenticated_user, test_plugin, init_db):
    with patch('Backend.Modules.DB.Plugins.current_user', authenticated_user):
        response = client.delete(f'/api/plugins/{test_plugin.id}')
        assert response.status_code == 200
        assert response.json == {'message': f"Plugin '{test_plugin.name}' deleted"}

        # Verify plugin is deleted from the database
        deleted_plugin = Plugin.query.get(test_plugin.id)
        assert deleted_plugin is None


@pytest.fixture
def test_plugin(test_repo, init_db):
    """Create a test plugin in the database."""
    plugin = Plugin(name='Test Plugin', type='backend', repository=test_repo)
    db.session.add(plugin)
    db.session.commit()
    return plugin
