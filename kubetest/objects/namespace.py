"""Kubetest wrapper for the Kubernetes `Namespace` API Object."""

import logging

from kubernetes import client

log = logging.getLogger('kubetest')


class Namespace:
    """Kubetest wrapper around a Kubernetes Namespace API Object.

    The actual `kubernetes.client.V1Namespace` instance that this
    wraps can be accessed via the `obj` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the Namespace.

    This wrapper does NOT subclass the kubetest.ApiObject like other
    object wrappers because it is not intended to be created or
    managed from manifest file. It is just meant to wrap the
    Namespace spec to make Namespace actions easier and the API
    more consistent.
    """

    def __init__(self, api_object):
        self.obj = api_object

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    @property
    def name(self):
        """The name of the Namespace (metadata.name)."""
        return self.obj.metadata.name

    @name.setter
    def name(self, name):
        """Set the name of the Namespace"""
        self.obj.metadata.name = name

    @classmethod
    def new(cls, name):
        """Create a new Namespace with object backing.

        Args:
            name (str): The name of the new namespace.

        Returns:
            Namespace: A new Namespace instance.
        """
        return cls(client.V1Namespace(
            metadata=client.V1ObjectMeta(
                name=name
            )
        ))

    def create(self, name=None):
        """Create the Namespace under the given name.

        Args:
            name (str): The name to create the Namespace under. If the
                name is not provided, it will be assumed to already be
                in the underlying object spec. If it is not, namespace
                operations will fail.
        """
        if name is not None:
            self.name = name

        log.info('creating namespace "%s"', self.name)
        log.debug('namespace: %s', self.obj)
        self.obj = client.CoreV1Api().create_namespace(
            body=self.obj,
        )

    def delete(self, options=None):
        """Delete the Namespace.

        Args:
             options (client.V1DeleteOptions): Options for RoleBinding deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting namespace "%s" with options "%s"', self.name, options)
        log.debug('namespace: %s', self.obj)

        return client.CoreV1Api().delete_namespace(
            name=self.name,
            body=options,
        )
