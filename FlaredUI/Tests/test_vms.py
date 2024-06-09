import pytest
from unittest.mock import patch

from FlaredUI.Modules.DB import (
    create_vm, Server, VM, VMManagement, get_all_vms,
    get_vm_by_id, update_vm, delete_vm, db
)


# Fixtures for VM tests
@pytest.fixture
def vm_manager(init_db):
    vm_manager = VMManagement(name='esxi')
    db.session.add(vm_manager)
    db.session.commit()
    return vm_manager


@pytest.fixture
def test_server(init_db, vm_manager):
    server = Server(name='test_server', hostname='test_hostname', ip_address='127.0.0.1', ssh_port=22, username='test_user', password_hash='password_hash', container_manager_id=1, vm_manager_id=vm_manager.id, namespace="default")
    db.session.add(server)
    db.session.commit()
    return server


@pytest.fixture
def test_vm(init_db, test_server):
    vm = VM(name='test_vm', os_type='linux', os_name='Ubuntu', os_version='20.04', cpu_cores=2, memory=4096, storage=10000, state='running', guest_os_id='vm-12345', server=test_server, enabled=True)
    db.session.add(vm)
    db.session.commit()
    return vm


# Test creating a VM
def test_create_vm(client, vm_manager, init_db, test_server):
    vm_data = {'name': 'new_vm', 'os_type': 'linux', 'os_name': 'CentOS', 'os_version': '8', 'cpu_cores': 4, 'memory': 8192, 'storage': 20000, 'server_id': test_server.id, 'vm_manager_id': vm_manager.id}
    response = client.post(f'/api/servers/{test_server.id}/vms', json=vm_data)
    assert response.status_code == 201
    data = response.json

    # Check if VM details are returned correctly (excluding creation_time)
    assert 'id' in data
    assert data['name'] == vm_data['name']
    assert data['os_type'] == vm_data['os_type']
    assert data['os_name'] == vm_data['os_name']
    assert data['os_version'] == vm_data['os_version']
    assert data['cpu_cores'] == vm_data['cpu_cores']
    assert data['memory'] == vm_data['memory']
    assert data['storage'] == vm_data['storage']
    assert data['server_id'] == vm_data['server_id']


# Test listing VMs
def test_list_vms(client, test_vm, test_server, init_db):
    with patch('Backend.Modules.VMs.list_vms') as mock_list_vms:
        # Mock the return value of the list_vms function
        mock_list_vms.return_value = [{'name': 'vm1', 'os_type': 'Linux', 'state': 'running'},
                                   {'name': 'vm2', 'os_type': 'Windows', 'state': 'stopped'}]

        response = client.get(f'/api/servers/{test_server.id}/vms')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2
        assert data[0]['name'] == 'vm1'
        assert data[1]['name'] == 'vm2'


# Test getting a specific VM by ID
def test_get_vm_route(client, test_vm, test_server):
    response = client.get(f'/api/servers/{test_server.id}/vms/{test_vm.id}')
    assert response.status_code == 200
    data = response.json

    assert data['id'] == test_vm.id
    assert data['name'] == 'test_vm'


# Test updating a VM
def test_update_vm(client, test_vm, test_server, vm_manager):
    update_data = {'cpu_cores': 4, 'memory': 8192}

    response = client.put(f'/api/servers/{test_server.id}/vms/{test_vm.id}', json=update_data)
    assert response.status_code == 200
    data = response.json
    assert data['cpu_cores'] == 4
    assert data['memory'] == 8192


# Test deleting a VM
def test_delete_vm(client, test_vm, test_server, init_db):
    response = client.delete(f'/api/servers/{test_server.id}/vms/{test_vm.id}')
    assert response.status_code == 200
    assert response.json == {'message': 'VM deleted successfully'}

    # Verify VM is deleted from the database
    deleted_vm = VM.query.get(test_vm.id)
    assert deleted_vm is None
