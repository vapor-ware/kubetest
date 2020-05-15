"""Kubetest wrapper for the Kubernetes ``Event`` API Object."""

import logging

from kubernetes import client

log = logging.getLogger('kubetest')


class Event:
    """Kubetest wrapper around a Kubernetes `Event`_ API Object.

    The actual ``kubernetes.client.V1Event`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper does **NOT** subclass the ``objects.ApiObject`` like
    other object wrappers because it is not intended to be created or
    managed from manifest file. It is merely meant to wrap the
    Event object to make Event-based interactions easier

    .. _Event:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#event-v1-core
    """

    obj_type = client.V1Event

    api_clients = {
        'preferred': client.CoreV1Api,
        'v1': client.CoreV1Api,
    }

    def __init__(self, api_object) -> None:
        self.obj = api_object
        self.name = api_object.metadata.name
