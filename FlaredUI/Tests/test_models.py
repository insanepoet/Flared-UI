import pytest

from FlaredUI.Modules.DB import (
    db, User, OAuth, OAuthProvider, Tunnel, ContainerManagement,
    VMManagement, Server, Container, VM, Application, ApiKeys,
    AppSettings, PluginRepository, Plugin
)
from datetime import datetime, timezone


# --- User Model Tests ---
def test_user_model(init_db):
    user = User(username="testuser", email="testuser@example.com", password_hash="hashed_password")
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    assert user.password_hash == "hashed_password"

    # Test setting and checking password
    user.set_password("newpassword")
    assert user.check_password("newpassword") == True
    assert user.check_password("wrongpassword") == False

    # Test to_dict method
    user_dict = user.to_dict()
    assert "password_hash" not in user_dict


# --- OAuth Model Tests ---
def test_oauth_model(init_db):
    oauth_provider = OAuthProvider(platform="test_platform", client_id="test_client_id",
                                   client_secret="test_client_secret")
    user = User(username="testuser", email="testuser@example.com", password_hash="hashed_password")
    oauth = OAuth(user=user, provider=oauth_provider, oauth_id="test_oauth_id")

    db.session.add(oauth_provider)
    db.session.add(user)
    db.session.add(oauth)
    db.session.commit()

    assert oauth.user == user
    assert oauth.provider == oauth_provider
    assert oauth.oauth_id == "test_oauth_id"
    assert isinstance(oauth.created_at, datetime)

# TODO: write tests for remainder of models
