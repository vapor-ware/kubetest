:orphan:

kubetest: write integration tests on Kubernetes
===============================================

``kubetest`` is a `pytest <https://docs.pytest.org/en/latest/>`_ plugin that
makes it easier to write integration tests on Kubernetes. This allows you to
automate your Kubernetes infrastructure, networking, and disaster recovery
tests.


.. _features:

Features
--------

- A simple API for interacting with your cluster.
- Uses the `Kubernetes Python client <https://github.com/kubernetes-client/python>`_ as
  the backend, allowing more complex cluster control for actions not covered by our API.
- Loads Kubernetes manifest YAMLs into their Kubernetes models.
- Runs each test case in its own namespace.
- Automatic management of cluster objects (namespaces, role bindings, etc).
- Detailed logging to help debug test errors.
- Wait functions for object readiness, deletion, and test conditions.
- Allows you to search container logs for expected log output.
- RBAC permissions can be set at a test-case granularity using pytest markers.


Documentation
-------------
See :ref:`Contents <toc>` for full documentation. This includes installation,
setup, example usage, and API reference.

See also the :ref:`Reference <reference>` docs.

Bugs/Features
-------------
If you encounter a bug or have an idea for a new feature, open a new issue on
`GitHub <https://github.com/vapor-ware/kubetest/issues>`_, providing as much
context as you can.

License
-------
``kubetest`` is free and open source software distributed under the terms of
the `GPLv3`_ license.

:ref:`modindex`

.. _`GPLv3`: https://github.com/vapor-ware/kubetest/blob/master/LICENSE
