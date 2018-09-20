"""Unit tests for the kubetest.manager package."""

from kubetest import manager


def test_manager_new_test():
    """Test creating a new TestMeta from the manager."""

    m = manager.KubetestManager()
    assert len(m.nodes) == 0

    c = m.new_test('node-id', 'test-name')
    assert isinstance(c, manager.TestMeta)
    assert 'kubetest-test-name-' in c.ns

    assert len(m.nodes) == 1
    assert 'node-id' in m.nodes


def test_manager_get_test():
    """Test getting an existing TestMeta from the manager."""

    m = manager.KubetestManager()
    m.nodes['foobar'] = manager.TestMeta('foo', 'bar')

    c = m.get_test('foobar')
    assert isinstance(c, manager.TestMeta)
    assert 'foo' == c.name
    assert 'bar' == c.node_id


def test_manager_get_test_none():
    """Test getting a non-existent test meta from the manager."""

    m = manager.KubetestManager()

    c = m.get_test('foobar')
    assert c is None
