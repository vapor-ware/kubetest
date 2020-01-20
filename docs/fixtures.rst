
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


.. _kubeconfig_fixture:

kubeconfig
----------

.. autofunction:: kubetest.plugin.kubeconfig
   :noindex:

Summary
~~~~~~~

The ``kubeconfig`` fixture provides the name of the kubeconfig file which was used to
load cluster configuration for the test. This should be the same value which was passed in
via the ``--kube-config`` command line parameter.

Example Usage
~~~~~~~~~~~~~

Below is a simple trivial example of how the ``kubeconfig`` fixture may be used.

.. code-block:: python

    def test_something(kubeconfig):
        """A test case that gets the config file name via fixture."""

        assert kubeconfig == '~/.kube/config'


.. _clusterinfo_fixture:

clusterinfo
-----------

.. autofunction:: kubetest.plugin.clusterinfo
   :noindex:

Summary
~~~~~~~

The ``clusterinfo`` fixture provides some basic information about the cluster which the tests
are being run on. This information is taken from the cluster configuration and current context,
so it should match the corresponding entries in the kube config file.

.. important::
  When using the ``clusterinfo`` fixture, you should *always* specify it **after** the
  ``kube`` fixture. This is because the ``clusterinfo`` fixture does not load the
  specified kubeconfig file, whereas the ``kube`` fixture does. Invoking the ``clusterinfo``
  fixture before the ``kube`` fixture will lead to some default configuration values to be
  returned, which may not accurately reflect the actual configuration used when the tests
  are run.

  **Good**

  .. code-block:: python

      def test_example(kube, clusterinfo):
          ...

  **Bad**

  .. code-block:: python

      def test_example(clusterinfo, kube):
          ...

The ``clusterinfo`` fixture returns an instance of ``ClusterInfo``:

.. autoclass:: kubetest.plugin.ClusterInfo
   :noindex:

Example Usage
~~~~~~~~~~~~~

Below is a simple trivial example of how the ``kubeconfig`` fixture may be used.

.. code-block:: python

    def test_something(kube, clusterinfo):
        """A test case that gets cluster info via fixture."""

        assert clusterinfo.user == 'test-user'
        assert clusterinfo.context == 'text-context'
