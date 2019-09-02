"""An example of using kubetest to manage a persistentvolume and persistentvolumeclaim."""

import time

import pytest


@pytest.mark.applymanifests('data', files=[
    'simple-persistentvolume.yaml',
    'simple-persistentvolumeclaim.yaml',
])
def test_pv_pvc(kube):
    """Test pv and pvc methods"""

    kube.wait_for_registered(timeout=120)
    time.sleep(10)

    pv = kube.get_persistentvolume()
    assert "my-pv" in pv

    pvc = kube.get_persistentvolumeclaim()
    assert "my-pvc" in pvc
