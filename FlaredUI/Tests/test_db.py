import pytest
from unittest.mock import patch

from FlaredUI.Modules.DB import (
    User as UserModel, Tunnel, TLD, ContainerManagement,
    VMManagement, db, User, Tunnels, Contained, Managers, ApiKeys, Settings, Plugins
)


# Tests for Users Module
def test_create_user(client, init_db):
    user_data = {'username': 'testuser', 'email': 'testuser@example.com', 'password': 'testpassword'}
    user = User.create_user(user_data)
    assert user.username == 'testuser'
    assert user.email == 'testuser@example.com'


def test_get_user_by_id(client, init_db):
    user_data = {'username': 'testuser', 'email': 'testuser@example.com', 'password': 'testpassword'}
    created_user = User.create_user(user_data)
    retrieved_user = User.get_user_by_id(created_user.id)
    assert retrieved_user.username == 'testuser'


# Tests for Tunnels Module
def test_create_tunnel(client, init_db):
    tld = TLD(name='example.com')
    db.session.add(tld)
    db.session.commit()

    with patch('Backend.Modules.Cloudflare.Tunnel.create_cloudflared_tunnel') as mock_create_tunnel:
        mock_create_tunnel.return_value = {'id': 'mocked_tunnel_id', 'name': 'test_tunnel',
                                           'connection_state': 'CONNECTED'}

        data = {'name': 'test_tunnel', 'domain': 'test.example.com', 'description': 'Test tunnel', 'tlds': ['example.com']}
        tunnel = Tunnels.create_tunnel(data)

        assert tunnel.name == 'test_tunnel'
        assert tunnel.uuid  # Check if UUID was generated
        assert tunnel.domain == 'test.example.com'
        assert tunnel.description == 'Test tunnel'
        assert tunnel.tlds[0].name == 'example.com'  # Check TLD association


# TODO: Add more tests for other tunnel operations: get_all_tunnels, get_tunnel_by_id, update_tunnel, delete_tunnel

# Tests for Contained Module
def test_create_container(client, init_db, test_server):
    data = {'name': 'test_container', 'image': 'nginx', 'server_id': test_server.id}
    container = Contained.create_container(data)

    assert container.name == 'test_container'
    assert container.image == 'nginx'
    assert container.server_id == test_server.id


# Tests for Managers Module
def test_get_container_managers(client, init_db):
    Managers.create_container_managers()
    managers = Managers.get_container_managers()
    assert len(managers) > 0


def test_get_vm_managers(client, init_db):
    Managers.create_vm_managers()
    managers = Managers.get_vm_managers()
    assert len(managers) > 0
