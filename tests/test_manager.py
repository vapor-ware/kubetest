"""Unit tests for the kubetest.manager package."""

from kubetest import client, manager


def test_manager_new_client():
    """Test creating a new TestClient from the manager."""

    m = manager.KubetestManager()
    assert len(m.clients) == 0

    c = m.new_client('node-id', 'test-name')
    assert isinstance(c, client.TestClient)
    assert 'kubetest-test-name-' in c.namespace

    assert len(m.clients) == 1
    assert 'node-id' in m.clients


def test_manager_get_client():
    """Test getting an existing client from the manager."""

    m = manager.KubetestManager()
    m.clients['foobar'] = client.TestClient('xyz')

    c = m.get_client('foobar')
    assert isinstance(c, client.TestClient)
    assert 'xyz' == c.namespace


def test_manager_get_client_none():
    """Test getting a non-existent client from the manager."""

    m = manager.KubetestManager()

    c = m.get_client('foobar')
    assert c is None
