import pytest
from unittest.mock import patch

from FlaredUI.Modules.DB import db, create_tunnel, get_tunnel_by_id
from FlaredUI.Modules.Cloudflare import (
    create_cloudflared_tunnel,
    list_cloudflared_tunnels,
    get_cloudflared_tunnel_info,
    cloudflared_tunnel_run,
    cloudflared_tunnel_delete,
    cloudflared_tunnel_cleanup,
    generate_cloudflared_config,
)
from FlaredUI.Modules.DB import db
from FlaredUI.Modules.DB.Models import Tunnel


# Mock Cloudflared Functions
@pytest.fixture
def mocked_tunnel():
    with patch('Backend.Modules.Cloudflare.Tunnel.create_cloudflared_tunnel') as mock_create:
        mock_create.return_value = {'id': 'mocked_tunnel_id', 'name': 'test_tunnel', 'connection_state': 'CONNECTED'}
        yield Tunnel(name='test_tunnel', uuid='test_uuid', domain='example.com', description='Test tunnel')


@patch('Backend.Modules.Cloudflare.Tunnel.create_cloudflared_tunnel')
@patch('Backend.Modules.Cloudflare.Tunnel.generate_cloudflared_config')
def test_create_tunnel(mock_generate_config, mock_create_tunnel, client, init_db):
    mock_create_tunnel.return_value = {'id': 'mocked_tunnel_id', 'name': 'test_tunnel', 'connection_state': 'CONNECTED'}

    # Test valid tunnel creation
    data = {'name': 'test_tunnel', 'domain': 'example.com', 'description': 'Test tunnel'}
    response = client.post('/api/cloudflare/tunnels', json=data)
    assert response.status_code == 201
    assert response.json['name'] == 'test_tunnel'
    mock_generate_config.assert_called_once()

    # Test duplicate tunnel name
    response = client.post('/api/cloudflare/tunnels', json=data)
    assert response.status_code == 500


def test_get_all_tunnels(client, mocked_tunnel, init_db):
    with patch('Backend.Modules.Cloudflare.Tunnel.get_cloudflared_tunnel_info') as mock_get_info:
        mock_get_info.return_value = {'id': 'mocked_tunnel_id', 'name': 'test_tunnel', 'connection_state': 'CONNECTED'}

        # Create tunnel entry
        db.session.add(mocked_tunnel)
        db.session.commit()

        response = client.get('/api/cloudflare/tunnels')
        assert response.status_code == 200
        data = response.json
        assert len(data) == 1
        assert data[0]['name'] == 'test_tunnel'
        assert data[0]['cloudflare_tunnel_details'] == {'id': 'mocked_tunnel_id', 'name': 'test_tunnel',
                                                        'connection_state': 'CONNECTED'}

# TODO: add more tests for updating, deleting, starting, and stopping tunnels
