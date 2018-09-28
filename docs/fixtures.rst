
Fixtures
========
This section defines the `fixtures <https://docs.pytest.org/en/latest/fixture.html>`_
that ``kubetest`` makes available when installed.

.. note::

    Use ``pytest --fixtures`` to get a complete list of available fixtures
    along with their descriptions.


.. _kube_fixture:

kube
----

.. autofunction:: kubetest.plugin.kube
   :noindex:

Summary
~~~~~~~
The ``kube`` fixture is the "entrypoint" for using kubetest. In addition to returning
a client that can be used to manage your cluster from within the test case, it also
provides automatic management of the test case on the cluster.

What this means is that it will create a Namespace specific to that test case (prefixed
with ``kubetest-``) and will create any resources specified by the kubetest :ref:`kube_markers`.
Once the test has completed, the test client and all test-associated resources set up
by this fixture are cleaned up.

For the full API for the test client provided by the ``kube`` fixture, see the
:ref:`kubetest_client` documentation.

Example Usage
~~~~~~~~~~~~~
Below is a simple trivial example of how the ``kube`` fixture can be used.
See the :ref:`examples` page for more.

.. code-block:: python

   def test_simple_deployment(kube):
      """Test that a simple deployment runs as intended."""

      # Load and create a deployment
      deployment = kube.load_deployment('path/to/deployment.yaml')
      deployment.create()

      # Wait until the deployment is in the ready state and then
      # refresh its underlying object data
      deployment.wait_until_ready(timeout=10)
      deployment.refresh()

      # Get the pods from the deployment and check that we have
      # the right number of replicas
      pods = deployment.get_pods()
      assert len(pods) == 1

      # Get the pod, ensure that it is ready, then get the containers
      # for that pod.
      pod = pods[0]
      pod.wait_until_ready(timeout=10)

      containers = pod.get_containers()
      assert len(containers) == 1
