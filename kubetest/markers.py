"""Custom pytest markers for kubetest."""

import os

from kubernetes import client

from kubetest.manifest import load_file, load_path
from kubetest.objects import ApiObject, ClusterRoleBinding, RoleBinding

APPLYMANIFEST_INI = (
    'applymanifests(path, files=None): '
    'load the YAML manifests from the specified path and create them on the cluster. '
    'By default, all YAML files found in the specified path will be loaded and created. '
    'If a list is passed to the files parameter, only the files in the path matching '
    'to a name in the files list will be loaded and created. This marker is similar to '
    'the "kubectl apply -f <dir>" command. Loading manifests via this marker will not '
    'prohibit you from loading other manifests manually. Use the "kube" fixture to get '
    'references to the created objects. Manifests loaded via this marker are registered '
    'with the internal test case metainfo and can be waited upon for creation via the '
    '"kube" fixture "wait_until_created" method.'
)

CLUSTERROLEBINDING_INI = (
    'clusterrolebinding(name, subject_kind=None, subject_name=None): '
    'create and use a Kubernetes ClusterRoleBinding for the test case. The generated '
    'cluster role binding will be automatically created and removed for each marked '
    'test. The name of the role must be specified. Only existing ClusterRoles can be '
    'used. Optionally, the subject_kind (User, Group, ServiceAccount) and subject_name '
    'can be specified to set a target subject for the ClusterRoleBinding. If no '
    'subject is specified, it will default to all users in the namespace and all '
    'service accounts. If a subject is specified, both the subject kind and name must '
    'be present. The ClusterRoleBinding will always use the apiGroup '
    '"rbac.authorization.k8s.io" for both subjects and roleRefs. For more information, '
    'see https://kubernetes.io/docs/reference/access-authn-authz/rbac/'
)

ROLEBINDING_INI = (
    'rolebinding(kind, name, subject_kind=None, subject_name=None): '
    'create and use a Kubernetes RoleBinding for the test case. The generated role '
    'binding will use the generated test-case namespace and will be automatically '
    'removed once the test completes. The role kind (Role, ClusterRole) must be '
    'specified along with the name of the role. Only existing Roles or ClusterRoles '
    'can be used. Optionally, the subject_kind (User, Group, ServiceAccount) and '
    'subject_name can be specified to set a target subject for the RoleBinding. If '
    'no subject is specified, it will default to all users in the namespace and all '
    'service accounts. If a subject is specified, both the subject kind and name '
    'must be present. The RoleBinding will always use the apiGroup '
    '"rbac.authorization.k8s.io" for both subjects and roleRefs. For more information, '
    'see https://kubernetes.io/docs/reference/access-authn-authz/rbac/'
)


def register(config):
    """Register kubetest markers with pytest.

    Args:
        config: The pytest config that markers will be registered to.
    """
    config.addinivalue_line('markers', APPLYMANIFEST_INI)
    config.addinivalue_line('markers', CLUSTERROLEBINDING_INI)
    config.addinivalue_line('markers', ROLEBINDING_INI)


def apply_manifest_from_marker(item, client):
    """Load manifests and create the API objects for the specified files.

    This gets called for every `pytest.mark.applymanifests` marker on
    test cases.

    Once a manifest has been loaded, the API objects will be registered
    with the test cases' TestMeta. This allows some easier control via
    the "kube" fixture, such as waiting for all objects to be created.

    Args:
        item: The pytest test item.
        client (manager.TestMeta): The metainfo object for the marked
            test case.
    """
    for mark in item.iter_markers(name='applymanifests'):
        dir_path = mark.args[0]
        files = mark.kwargs.get('files')

        # We expect the path specified to either be absolute or relative
        # from the test file. If the path is relative, add the directory
        # that the test file resides in as a prefix to the dir_path.
        if not os.path.isabs(dir_path):
            dir_path = os.path.abspath(
                os.path.join(os.path.dirname(item.fspath), dir_path)
            )

        # If there are any files specified, we will only load those files.
        # Otherwise, we'll load everything in the directory.
        if files is None:
            objs = load_path(dir_path)
        else:
            objs = [load_file(os.path.join(dir_path, f)) for f in files]

        # For each of the loaded Kubernetes resources, we'll want to wrap it
        # in the equivalent kubetest wrapper. If the resource does not have
        # an equivalent kubetest wrapper, error out. We cannot reliably create
        # the resource without our ApiObject wrapper semantics.
        wrapped = []
        for obj in objs:
            found = False
            for klass in ApiObject.__subclasses__():
                if obj.kind == klass.__name__:
                    wrapped.append(klass(obj))
                    found = True
                    break
            if not found:
                raise ValueError(
                    'Unable to match loaded object to an internal wrapper '
                    'class: {}'.format(obj)
                )

        client.register_objects(wrapped)


def rolebindings_from_marker(item, namespace):
    """Create RoleBindings for the test case if the test is marked
    with the `pytest.mark.rolebinding` marker.

    Args:
        item (pytest.Item): The pytest test item.
        namespace (str): The namespace of the test case.

    Returns:
        list[objects.RoleBinding]: The RoleBindings that were
            generated from the test case markers.
    """
    rolebindings = []
    for mark in item.iter_markers(name='rolebinding'):
        kind = mark.args[0]
        name = mark.args[1]
        subj_kind = mark.kwargs.get('subject_kind')
        subj_name = mark.kwargs.get('subject_name')

        subj = get_custom_rbac_subject(namespace, subj_kind, subj_name)
        if not subj:
            subj = get_default_rbac_subjects(namespace)

        rolebindings.append(RoleBinding(client.V1RoleBinding(
            metadata=client.V1ObjectMeta(
                name='kubetest:{}'.format(item.name),
                namespace=namespace,
            ),
            role_ref=client.V1RoleRef(
                api_group='rbac.authorization.k8s.io',
                kind=kind,
                name=name,
            ),
            subjects=subj,
        )))

    return rolebindings


def clusterrolebindings_from_marker(item, namespace):
    """Create ClusterRoleBindings for the test case if the test case
    is marked with the `pytest.mark.clusterrolebinding` marker.

    Args:
        item (pytest.Item): The pytest test item.
        namespace (str): The namespace of the test case.

    Return:
        list[objects.ClusterRoleBinding]: The ClusterRoleBindings that
            were generated from the test case markers.
    """
    clusterrolebindings = []
    for mark in item.iter_markers(name='clusterrolebinding'):
        name = mark.args[0]
        subj_kind = mark.kwargs.get('subject_kind')
        subj_name = mark.kwargs.get('subject_name')

        subj = get_custom_rbac_subject(namespace, subj_kind, subj_name)
        if not subj:
            subj = get_default_rbac_subjects(namespace)

        clusterrolebindings.append(ClusterRoleBinding(client.V1ClusterRoleBinding(
            metadata=client.V1ObjectMeta(
                name='kubetest:{}'.format(item.name),
            ),
            role_ref=client.V1RoleRef(
                api_group='rbac.authorization.k8s.io',
                kind='ClusterRole',
                name=name,
            ),
            subjects=subj,
        )))

    return clusterrolebindings


def get_custom_rbac_subject(namespace, kind, name):
    """Create a custom RBAC subject for the given namespace.

    Both `kind` and `name` must be specified. If one is set and
    the other is not (None), an error will be raised.

    Args:
        namespace (str): The namespace of the Subject.
        kind (str): The subject kind. This should be one of:
            'User', 'Group', or 'ServiceAccount'.
        name (str): The name of the Subject.

    Returns:
        list[client.V1Subject]: The custom RBAC subject.

    Raises:
        ValueError: One of `kind` and `name` are None.
    """
    # check that both `kind` and `name` are set.
    if (kind and not name) or (not kind and name):
        raise ValueError(
            'One of subject_kind and subject_name were specified, but both must '
            'be specified when defining a custom Subject.'
        )

    # otherwise, if a custom subject is specified, create it
    if name is not None and kind is not None:
        return [
            client.V1Subject(
                api_group='rbac.authorization.k8s.io',
                namespace=namespace,
                kind=kind,
                name=name,
            )
        ]
    else:
        return []


def get_default_rbac_subjects(namespace):
    """Get the default RBAC Subjects.

    The default subjects will allow:
      - all authenticated users
      - all unauthenticated users
      - all service accounts

    Args:
        namespace (str): The namespace of the Subjects.

    Returns:
        list[client.V1Subject]: The default RBAC subjects.
    """
    return [
        # all authenticated users
        client.V1Subject(
            api_group='rbac.authorization.k8s.io',
            namespace=namespace,
            name='system:authenticated',
            kind='Group',
        ),
        # all unauthenticated users
        client.V1Subject(
            api_group='rbac.authorization.k8s.io',
            namespace=namespace,
            name='system:unauthenticated',
            kind='Group',
        ),
        # all service accounts
        client.V1Subject(
            api_group='rbac.authorization.k8s.io',
            namespace=namespace,
            name='system:serviceaccounts',
            kind='Group',
        ),
    ]
