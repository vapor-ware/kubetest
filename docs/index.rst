
kubetest
========
``kubetest`` is a `pytest <https://docs.pytest.org/en/latest/>`_ plugin that
makes it easier to write integration tests on Kubernetes. This allows you to
automate tests for your Kubernetes infrastructure, networking, and disaster recovery.

kubetest was written out of a desire to test deployment behavior in a
quasi-deterministic manner. Other solutions exist for on-cluster testing, such
as `chaos testing <https://principlesofchaos.org/>`_, but often those solutions
lack the ability to test the specific state of a small piece of the deployment.

kubetest aims to make that easier, giving you control of your cluster from within
your test cases, and providing a simple API for managing the cluster and the objects
on it.

Features
--------

- Simple API for common cluster interactions.
- Uses the `Kubernetes Python client <https://github.com/kubernetes-client/python>`_ as
  the backend, allowing more complex cluster control for actions not covered by our API.
- Load Kubernetes manifest YAMLs into their Kubernetes models.
- Each test is run in its own namespace and the namespace is created and
  deleted automatically.
- Detailed logging to help debug error cases.
- Wait functions for object readiness, deletion, and test conditions.
- Allows you to search container logs for expected log output.
- RBAC permissions can be set at a test-case granularity using pytest markers.


.. _installation:

Installation
------------
kubetest can be installed with ``pip``

.. code-block:: bash

   $ pip install kubetest


.. note::
   The kubetest package has entrypoint hooks defined in ``setup.py`` which allow it to be
   automatically made available to pytest. This means that it will run whenever pytest is run.
   Since kubetest expects a cluster to be set up and to be given configuration for that
   cluster, pytest will fail if those are not present. It is therefore recommended to only
   install kubetest in a virtual environment or other managed environment, such as a CI
   pipeline, where you can assure that cluster access and configuration are available.


Feedback
--------
Feedback for kubetest is greatly appreciated! If you experience any issues, find the
documentation unclear, have feature requests, or just have questions about it, we'd
love to know. Feel free to open an issue on `GitHub <https://github.com/vapor-ware/kubetest/issues>`_
for any feedback you may have. If you are reporting a bug, please provide as much
context as you can.


License
-------
kubetest is free and open source software distributed under the terms of
the `GPLv3`_ license.


Contents
--------

.. toctree::
   :maxdepth: 2

   usage
   fixtures
   markers
   reference
   examples
   source/modules


.. _`GPLv3`: https://github.com/vapor-ware/kubetest/blob/master/LICENSE
