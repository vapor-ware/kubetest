"""Kubetest wrapper for the Kubernetes ``version`` API Object."""

from kubernetes import client
from kubetest.objects import ApiObject


class Version(ApiObject):
    """Kubetest wrapper around a Kubernetes `VersionInfo`_ API Object.

    The actual ``kubernetes.client.VersionInfo`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `VersionInfo`_.

    .. _VersionInfo:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.21/#
    """

    obj_type = client.VersionInfo

    api_clients = {
        'preferred': client.VersionApi,
        'v1': client.VersionApi,
    }

    def __init__(self):
        super().__init__(get_version())

    def create(self, namespace: str = None) -> None:
        pass

    def delete(self, options: client.V1DeleteOptions) -> client.V1Status:
        pass

    def refresh(self) -> None:
        self.obj = get_version()

    def is_ready(self) -> bool:
        pass

    def git_version(self):
        return self.obj.git_version

    def major_minor_version(self):
        return self.obj.major, self.obj.minor


def get_version():
    return Version.preferred_client().get_code()
