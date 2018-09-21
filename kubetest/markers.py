"""Pytest markers for Kubetest."""

from kubernetes import client

from kubetest.objects import ClusterRoleBinding, RoleBinding


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
