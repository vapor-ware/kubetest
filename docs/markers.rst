
.. _kube_markers:

Markers
=======
This section defines the `markers <https://docs.pytest.org/en/latest/mark.html>`_
that ``kubetest`` makes available when installed.

.. note::

    Use ``pytest --markers`` to get a complete list of available markers
    along with their descriptions.

.. _applymanifest_marker:

Apply Manifest
--------------

Summary
~~~~~~~

.. code-block:: python

    @pytest.mark.applymanifest(path)

``applymanifest`` allows you to load a Kubernetes manifest file and create the
resource(s) on the cluster.

Description
~~~~~~~~~~~
Load the YAML manifest with the specified ``path`` and create the corresponding
resource(s) on the cluster.

Loading a manifest via this marker does not prohibit you from manually loading other
manifests later in the test case. You can use the :ref:`kube_fixture` fixture to get
object references to the created resources. Manifests loaded via this marker are
registered with the internal test case ``MetaInfo`` and can be waited upon for
creation via the :ref:`kube_fixture` fixture's ``wait_until_created`` method.

The path to the directory should either be an absolute path, or a path relative
from the test file. This marker can be used multiple times on a test case. If you
wish to load multiple manifests at once, consider using the :ref:`applymanifests_marker`
marker.

This marker is similar to the ``kubectl apply -f <file>`` command.

Examples
~~~~~~~~
- Load a manifest YAML for a deployment

  .. code-block:: python

      @pytest.mark.applymanifest('./deployment.yaml')
      def test_something(kube):
          ...

- Load multiple manifests

  .. code-block:: python

      @pytest.mark.applymanifest('manifests/test/service.yaml')
      @pytest.mark.applymanifest('manifests/test/deployment.yaml')
      def test_something(kube):
          ...


.. _applymanifests_marker:

Apply Manifests
---------------

Summary
~~~~~~~

.. code-block:: python

    @pytest.mark.applymanifests(dir, files=None)

``applymanifests`` allows you to load Kubernetes manifests from the specified
directory and create the resources on the cluster.

Description
~~~~~~~~~~~
Load the YAML manifests from the specified ``path`` and create the corresponding
resources on the cluster. By default all YAML files found in the specified ``dir``
will be loaded and created. A list of file names can be passed to the ``files``
parameter, which would limit manifest application to only those YAMLs matching the
provided file names in the directory.

Loading manifests via this marker does not prohibit you from manually loading other
manifests later in the test case. You can use the :ref:`kube_fixture` fixture to get
object references to the created resources. Manifests loaded via this marker are
registered with the internal test case ``MetaInfo`` and can be waited upon for
creation via the :ref:`kube_fixture` fixture's ``wait_until_created`` method.

The path to the directory should either be an absolute path, or a path relative
from the test file. This marker can be used multiple times on a test case.

When specifying specific files to use from within a directory, or when specifying
multiple source directories, the order does not matter. The manifests are loaded,
bucketed, and then applied to the cluster in the following order:

- Namespace
- RoleBinding
- ClusterRoleBinding
- Secret
- Service
- ConfigMap
- Deployment
- Pod

This marker is similar to the ``kubectl apply -f <dir>`` command.

Examples
~~~~~~~~
- Load manifest YAMLs from a ``manifests`` directory

  .. code-block:: python

      @pytest.mark.applymanifests('manifests')
      def test_something(kube):
          ...

- Load specific manifest YAMLs from a ``manifests`` directory

  .. code-block:: python

      @pytest.mark.applymanifests('manifests', files=[
          'deployment.yaml',
          'service.yml'
      ])
      def test_something(kube):
          ...

- Load manifest YAMLs from a ``manifests`` directory and wait for the
  registered objects to be ready

  .. code-block:: python

      @pytest.mark.applymanifests('manifests')
      def test_something(kube):
          kube.wait_for_registered(timeout=60)
          ...

- Load manifests from multiple directories for a single test case

  .. code-block:: python

      @pytest.mark.applymanifests('manifests')
      @pytest.mark.applymanifests('common')
      def test_something(kube):
          ...


.. _clusterrolebinding_marker:

Cluster Role Binding
--------------------

Summary
~~~~~~~

.. code-block:: python

    @pytest.mark.clusterrolebinding(name, subject_kind=None, subject_name=None)

``clusterrolebinding`` creates a ``ClusterRoleBinding`` resource for the cluster
that will exist for the lifespan of the test case. The named cluster role must
already exist on the cluster.

Description
~~~~~~~~~~~
Create and use a Kubernetes ClusterRoleBinding for the test case. The generated
ClusterRoleBinding will be automatically created and removed for each marked test.
The name of the cluster role must be specified and the ClusterRole must already exist.
This marker can be used multiple times on a test case.

Optionally, the ``subject_kind`` (one of: *User*, *Group*, *ServiceAccount*) and
``subject_name`` can be specified to set a custom target subject for the generated
ClusterRoleBinding. If a custom target subject is specified, both ``subject_kind``
and ``subject_name`` must be specified. If no custom subject is specified, the
generated ClusterRoleBinding will default to all users and all service accounts.

The ClusterRoleBinding created via this marker will always use an ``apiGroup`` of
"rbac.authorization.k8s.io" for both subjects and roleRefs. Generated ClusterRoleBindings
will be created with the ``kubetest:`` prefix.

For more information, see: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

- To see all existing ClusterRoleBindings, use ``kubectl get clusterrolebindings``
- To see all existing ClusterRoles, use ``kubectl get clusterroles``

Examples
~~~~~~~~
- Use the "cluster-admin" role binding with the default subject

  .. code-block:: python

      @pytest.mark.clusterrolebinding('cluster-admin')
      def test_something(kube):
        ...

- Use the "cluster-admin" role on a custom target subject

  .. code-block:: python

      @pytest.mark.clusterrolebinding('cluster-admin', subject_kind='ServiceAccount', subject_name='custom-acct')
      def test_something(kube):
          ...

- Set multiple ClusterRoleBindings for the test case

  .. code-block:: python

      @pytest.mark.clusterrolebinding('system:node')
      @pytest.mark.clusterrolebinding('system:discovery')
      def test_something(kube):
          ...


.. _rolebinding_marker:

Role Binding
------------

Summary
~~~~~~~

.. code-block:: python

    @pytest.mark.rolebinding(kind, name, subject_kind=None, subject_name=None)

``rolebinding`` creates a ``RoleBinding`` resource for the cluster that will exist
for the lifespan of the test case. The named role must already exist on the cluster.


Description
~~~~~~~~~~~
Create and use a Kubernetes RoleBinding for the test case. The generated RoleBinding
will use the generated test case namespace and will be automatically created for each
marked test case and removed once each test completes. The role ``kind`` (one of:
*Role*, *ClusterRole*) must be specified along with the ``name`` of the role. Only
existing Roles or ClusterRoles can be used. This marker can be used multiple times on
a test case.

Optionally, the ``subject_kind`` (one of: *User*, *Group*, *ServiceAccount*) and
``subject_name`` can be specified to set a custom target subject for the generated
RoleBinding. If a custom target subject is specified, both ``subject_kind`` and
``subject_name`` must be specified. If no custom subject is specified, the generated
RoleBinding will default to all users in the namespace and all service accounts.

The RoleBinding created via this marker will always use an ``apiGroup`` of
"rbac.authorization.k8s.io" for both subjects and roleRefs.

For more information, see: https://kubernetes.io/docs/reference/access-authn-authz/rbac/

- To see all existing RoleBindings, use ``kubectl get rolebindings``
- To see all existing Roles, use ``kubectl get roles``

Examples
~~~~~~~~
- Use a RoleBinding with the default subject

  .. code-block:: python

      @pytest.mark.rolebinding('Role', 'test-role')
      def test_something(kube):
          ...

- Use a RoleBinding with a custom target subject

  .. code-block:: python

      @pytest.mark.rolebinding('Role', 'test-role', subject_kind='Group', subject_name='example')
      def test_something(kube):
          ...

- Set multiple RoleBindings for the test case

  .. code-block:: python

      @pytest.mark.rolebinding('Role', 'test-role')
      @pytest.mark.rolebinding('ClusterRole', 'custom-cluster-role')
      def test_something(kube):
          ...

.. _namespace_marker:

Namespace
------------

Summary
~~~~~~~

.. code-block:: python

    @pytest.mark.namespace(create=True, name=None)

``namespace`` helps defining the way namespaces are handled for each test case.


Description
~~~~~~~~~~~

Namespace configuration for this test.
By default a new namespace with a randomized name is created for each test case.
Set ``create`` to False to not create any namespace.
Set ``name`` to a string to use give the namespace a specific name, or set to None to generate a unique name.

Note: When ``create`` is False, the objects created by test test are not automatically deleted

Examples
~~~~~~~~
- Do not create a namespace for a given test

  .. code-block:: python

      @pytest.mark.namespace(create=False)
      def test_something(kube):
          ...

- Do not create a namespace and create all objects in existing-ns

  .. code-block:: python

      @pytest.mark.namespace(create=False, name='existing-ns')
      def test_something(kube):
          ...

- Create a namespace with a specific name

  .. code-block:: python

      @pytest.namespace(create=True, name='specific-name')
      def test_something(kube):
          ...

