:orphan:

kubetest
========

Write Kubernetes integration tests in Python.

``kubetest`` is a `pytest <https://docs.pytest.org/en/latest/>`_ plugin that
makes it easier to write integration tests on Kubernetes. This allows you to
automate your Kubernetes infrastructure, networking, and disaster recovery
tests.


Installation
------------
kubetest can be installed with `pip`

.. code-block:: bash

   $ pip install kubetest


.. note::
   The kubetest package has entrypoint hooks defined in ``setup.py`` which allow it to be
   automatically made available to pytest. This means that it will run whenever pytest is run.
   Since kubetest expects a cluster to be set up and to be given configuration for that
   cluster, pytest will fail if those are not present. It is therefore recommended to only
   install kubetest in a virtual environment or other managed environment, such as a CI
   pipeline, where you can assure that cluster access and configuration are available.


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


Bugs/Features
-------------
If you encounter a bug or have an idea for a new feature, open a new issue on
`GitHub <https://github.com/vapor-ware/kubetest/issues>`_, providing as much
context as you can.

License
-------
``kubetest`` is free and open source software distributed under the terms of
the `GPLv3`_ license.


Contents
--------

.. toctree::
   :maxdepth: 2

   usage
   reference
   source/modules


.. _`GPLv3`: https://github.com/vapor-ware/kubetest/blob/master/LICENSE
