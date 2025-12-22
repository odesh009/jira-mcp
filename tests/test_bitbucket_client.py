"""Tests for Bitbucket client."""

import pytest
from bitbucket_client import BitbucketClient


@pytest.fixture
def bitbucket_client():
    """Create a Bitbucket client for testing."""
    return BitbucketClient(username="test_user", app_password="test_password")


@pytest.mark.asyncio
async def test_client_initialization(bitbucket_client):
    """Test that the client initializes correctly."""
    assert bitbucket_client.username == "test_user"
    assert bitbucket_client.app_password == "test_password"
    assert bitbucket_client.BASE_URL == "https://api.bitbucket.org/2.0"


@pytest.mark.asyncio
async def test_client_close(bitbucket_client):
    """Test that the client closes properly."""
    await bitbucket_client.close()
