.. _reference:

API Reference
=============

This page contains the full API reference for kubetest.

.. contents::
    :depth: 3
    :local:


.. _kubetest_client:

Client
------

.. automodule:: kubetest.client


TestClient
~~~~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.client.TestClient
   :members:
   :noindex:


.. _kubetest_objects:

Objects
-------

.. automodule:: kubetest.objects


ApiObject
~~~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.ApiObject
   :members:


ClusterRoleBinding
~~~~~~~~~~~~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.ClusterRoleBinding
   :members:


ConfigMap
~~~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.ConfigMap
   :members:


Container
~~~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.Container
   :members:


Deployment
~~~~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.Deployment
   :members:


Namespace
~~~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.Namespace
   :members:


Node
~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.Node
   :members:


Pod
~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.Pod
   :members:


RoleBinding
~~~~~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.RoleBinding
   :members:


Secret
~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.Secret
   :members:


Service
~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.objects.Service
   :members:


.. _kubetest_conditions:

Conditions
----------

.. automodule:: kubetest.condition


Policy
~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.condition.Policy
   :members:


Condition
~~~~~~~~~

.. versionadded:: 0.0.1

.. autoclass:: kubetest.condition.Condition
   :members:


Helpers
~~~~~~~

.. autofunction:: kubetest.condition.check_all

.. autofunction:: kubetest.condition.check_and_sort