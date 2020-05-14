"""Unit tests for the kubetest.manager package."""

from kubetest import manager


def test_manager_new_test():
    """Test creating a new TestMeta from the manager."""

    m = manager.KubetestManager()
    assert len(m.nodes) == 0

    c = m.new_test('node-id', 'test-name', True, None)
    assert isinstance(c, manager.TestMeta)
    assert 'kubetest-test-name-' in c.ns

    assert len(m.nodes) == 1
    assert 'node-id' in m.nodes


def test_manager_new_test_with_ns_name():
    """Test creating a new TestMeta with a given namespace name
    from the manager.
    """

    m = manager.KubetestManager()
    c = m.new_test('node-id', 'test-name', True, 'my-test')
    assert isinstance(c, manager.TestMeta)
    assert c.ns == 'my-test'
    assert c.namespace_create is True


def test_manager_new_test_without_ns():
    """Test creating a new TestMeta without namespace creation
    from the manager.
    """

    m = manager.KubetestManager()
    c = m.new_test('node-id', 'test-name', False, None)
    assert isinstance(c, manager.TestMeta)
    assert c.namespace_create is False


def test_manager_get_test():
    """Test getting an existing TestMeta from the manager."""

    m = manager.KubetestManager()
    m.nodes['foobar'] = manager.TestMeta('foo', 'bar', True, None)

    c = m.get_test('foobar')
    assert isinstance(c, manager.TestMeta)
    assert 'foo' == c.name
    assert 'bar' == c.node_id


def test_manager_get_test_none():
    """Test getting a non-existent test meta from the manager."""

    m = manager.KubetestManager()

    c = m.get_test('foobar')
    assert c is None
