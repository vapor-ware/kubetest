"""Unit tests for the kubetest.manifest package."""

import pytest

from kubetest.objects import PersistentVolume


class TestPV:
    """Tests for kubetest.objects.persistentvolume"""

    def test_dummy_create_pv(self, kube, simple_persistentvolume):
        kubetest_pv = PersistentVolume(simple_persistentvolume)
        print(kube)
        print(dir(kube))
        1/0
        kubetest_pv.create()

    @pytest.mark.dependency(depends=["test_dummy_create_pv"])
    def test_simple_persistentvolume_auto_delete(self, kube, simple_persistentvolume):
        assert(kube.get_persistentvolumes() == [])
