import pytest
from unittest.mock import patch

from FlaredUI.Modules.DB import (
    db, Tunnel, TLD, create_route, get_routes_for_tunnel,
    update_route, delete_route, get_application_by_id, Application
)


# Test get_routes_for_tunnel
def test_get_routes_for_tunnel(client, init_db, test_tunnel, test_application):
    response = client.get(f'/api/cloudflare/tunnels/{test_tunnel.id}/routes')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]['id'] == test_application.id


# Test create_route
@patch('Backend.Modules.Cloudflare.cloudflared_route_create')
@patch('Backend.Modules.Cloudflare.generate_cloudflared_config')
def test_create_route(mock_generate_config, mock_cloudflared_route_create, client, init_db, test_tunnel,
                     test_application):
    data = {'application_id': test_application.id, 'tunnel_id': test_tunnel.id}
    response = client.post('/api/cloudflare/routes', json=data)
    assert response.status_code == 201
    mock_cloudflared_route_create.assert_called_once_with(test_tunnel.uuid, test_application.hostname,
                                                         test_application.service_url)
    mock_generate_config.assert_called_once_with(test_tunnel.id)


# Test update_route
def test_update_route(client, init_db, test_tunnel, test_application):
    test_application.tunnels.append(test_tunnel)
    db.session.commit()

    with patch('Backend.Modules.Cloudflare.cloudflared_route_delete') as mock_delete, \
            patch('Backend.Modules.Cloudflare.cloudflared_route_create') as mock_create, \
            patch('Backend.Modules.Cloudflare.generate_cloudflared_config') as mock_generate_config:

        data = {'hostname': 'updated_hostname'}
        response = client.put(f'/api/cloudflare/routes/{test_application.id}', json=data)
        assert response.status_code == 200
        data = response.get_json()
        assert data['application']['hostname'] == 'updated_hostname'

        mock_delete.assert_called_once()
        mock_create.assert_called_once()
        mock_generate_config.assert_called_once()

# Test delete_route
def test_delete_route(client, init_db, test_tunnel, test_application):
    test_application.tunnels.append(test_tunnel)
    db.session.commit()

    with patch('Backend.Modules.Cloudflare.cloudflared_route_delete') as mock_delete:
        response = client.delete(f'/api/cloudflare/routes/{test_application.id}')
        assert response.status_code == 200
        assert test_application not in test_tunnel.applications
        mock_delete.assert_called_once()


#Fixtures for Routes Tests
@pytest.fixture
def test_tld(init_db):
    """Create a test TLD in the database."""
    tld = TLD(name='example.com')
    db.session.add(tld)
    db.session.commit()
    return tld


@pytest.fixture
def test_tunnel(init_db, test_tld):
    """Create a test tunnel in the database."""
    tunnel = Tunnel(name='test_tunnel', uuid='test_uuid', domain='test.example.com', description='Test tunnel')
    tunnel.tlds.append(test_tld)
    db.session.add(tunnel)
    db.session.commit()
    return tunnel


@pytest.fixture
def test_application(init_db, test_server):
    """Create a test application in the database."""
    application = Application(name='test_application', exposed_ports='{"tcp": [80, 443]}', server=test_server,
                              hostname='app1')
    db.session.add(application)
    db.session.commit()
    return application
