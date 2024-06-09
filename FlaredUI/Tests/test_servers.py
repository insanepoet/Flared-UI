import pytest
from unittest.mock import patch

from FlaredUI.Modules.DB import (
    Server, ContainerManagement, VMManagement,
    create_server, get_all_servers,
    get_server_by_id, update_server,
    delete_server, db
)


# Fixtures for Server Tests
@pytest.fixture
def container_manager(init_db):
    """Create a test container manager in the database."""
    container_manager = ContainerManagement(name='docker')
    db.session.add(container_manager)
    db.session.commit()
    return container_manager


@pytest.fixture
def vm_manager(init_db):
    """Create a test VM manager in the database."""
    vm_manager = VMManagement(name='esxi')
    db.session.add(vm_manager)
    db.session.commit()
    return vm_manager


@pytest.fixture
def test_server(init_db, container_manager, vm_manager):
    """Create a test server in the database."""
    server = Server(name='test_server', hostname='test_hostname', ip_address='127.0.0.1', ssh_port=22,
                    username='test_user', password_hash='password_hash', container_manager_id=container_manager.id,
                    vm_manager_id=vm_manager.id, namespace="default")
    db.session.add(server)
    db.session.commit()
    return server


# Test Create Server
def test_create_server(client, container_manager, vm_manager, init_db):
    server_data = {
        'name': 'new_server',
        'hostname': 'new_hostname',
        'ip_address': '192.168.1.100',
        'ssh_port': 22,
        'username': 'new_user',
        'password': 'new_password',
        'container_manager_id': container_manager.id,
        'vm_manager_id': vm_manager.id,
        'namespace': 'test_namespace'
    }

    response = client.post('/api/servers/', json=server_data)
    assert response.status_code == 201
    data = response.json

    # Check if server details are returned correctly (excluding password_hash)
    assert 'id' in data
    assert data['name'] == server_data['name']
    assert data['hostname'] == server_data['hostname']
    assert data['ip_address'] == server_data['ip_address']
    assert data['ssh_port'] == server_data['ssh_port']
    assert data['username'] == server_data['username']
    assert 'password_hash' not in data  # Password hash should not be returned
    assert data['container_manager'] == container_manager.name  # Name of the container manager
    assert data['vm_manager'] == vm_manager.name  # Name of the VM manager
    assert data['namespace'] == server_data['namespace']


# Test List Servers
def test_list_servers(client, test_server, init_db):
    response = client.get('/api/servers/')
    assert response.status_code == 200
    data = response.json
    assert len(data) == 1
    assert data[0]['name'] == 'test_server'
    assert data[0]['hostname'] == 'test_hostname'
