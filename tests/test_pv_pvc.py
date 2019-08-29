"""An example of using kubetest to manage a persistentvolume and persistentvolumeclaim."""

import os
import pytest
import time

@pytest.mark.applymanifests('data', files=[
    'simple-persistentvolume.yaml',
    'simple-persistentvolumeclaim.yaml',
])

def test_pv_pvc(kube):

    # Wait for the objects registered via marker to be ready.
    kube.wait_for_registered(timeout=120)
    time.sleep(10)

## PERSISTENT VOLUME
    # get persistent volume
    pv = kube.get_persistentvolume()
    assert "my-pv" in pv

## PERSISTENT VOLUME CLAIM
    # get persistent volume claim
    pvc = kube.get_persistentvolumeclaim()
    assert "my-pvc" in pvc
