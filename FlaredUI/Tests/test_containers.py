import pytest
from unittest.mock import patch

from FlaredUI.Modules.DB import db, create_container, Server, Container, ContainerManagement


# Fixtures for Container Tests
@pytest.fixture
def test_server(init_db):
    """Create a test server in the database."""
    container_manager = ContainerManagement(name='docker')
    db.session.add(container_manager)
    db.session.commit()
    server = Server(name='test_server', hostname='test_hostname', ip_address='127.0.0.1', ssh_port=22, username='test_user', password_hash='password_hash', container_manager_id=container_manager.id, vm_manager_id=1, namespace="default")
    db.session.add(server)
    db.session.commit()
    return server


@pytest.fixture
def test_container(test_server):
    """Create a test container in the database."""
    container = Container(name='test_container', image='test_image', state='running', server=test_server, enabled=True, hostname='test_hostname')
    db.session.add(container)
    db.session.commit()
    return container


# Test listing containers
@patch('Backend.Modules.Containers.list_containers')
def test_list_containers_route(mock_list_containers, client, test_server):
    # Mock the return value of the list_containers function
    mock_list_containers.return_value = [
        {'name': 'container1', 'image': 'image1', 'state': 'running'},
        {'name': 'container2', 'image': 'image2', 'state': 'stopped'}
    ]

    # Test the route
    response = client.get(f'/api/servers/{test_server.id}/containers')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2  # Check if 2 containers are returned
    assert data[0]['name'] == 'container1'


# Test getting a specific container's information
@patch('Backend.Modules.Containers.get_container_info')
def test_get_container_route(mock_get_container_info, client, test_server, test_container):
    # Mock the return value of get_container_info
    mock_get_container_info.return_value = {'name': 'test_container', 'image': 'test_image', 'state': 'running'}

    # Test the route
    response = client.get(f'/api/servers/{test_server.id}/containers/{test_container.name}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'test_container'

# TODO: add more tests for container update, deletion, etc.
