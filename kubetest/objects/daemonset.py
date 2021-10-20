"""Kubetest wrapper for the Kubernetes ``DaemonSet`` API Object."""

import logging
import uuid
from typing import List

from kubernetes import client

from kubetest.utils import selector_string

from .api_object import ApiObject
from .pod import Pod

log = logging.getLogger("kubetest")


class DaemonSet(ApiObject):
    """Kubetest wrapper around a Kubernetes `DaemonSet`_ API Object.

    The actual ``kubernetes.client.V1DaemonSet`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `DaemonSet`_.

    .. DaemonSet:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.18/#daemonset-v1-apps
    """

    obj_type = client.V1DaemonSet

    api_clients = {
        "preferred": client.AppsV1Api,
        "apps/v1": client.AppsV1Api,
    }

    def __init__(self, *args, **kwargs) -> None:
        super(DaemonSet, self).__init__(*args, **kwargs)
        self._add_kubetest_labels()

    def _add_kubetest_labels(self) -> None:
        """Add a kubetest label to the DaemonSet object.

        This allows kubetest to more easily and reliably search for and aggregate
        API objects, such as getting the Pods for a DaemonSet.

        The kubetest label key is "kubetest/<obj kind>" where the obj kind is
        the lower-cased kind of the obj.
        """
        self.klabel_key = "kubetest/daemonset"
        if self.obj.metadata.labels:
            self.klabel_uid = self.obj.metadata.labels.get(self.klabel_key, None)
        else:
            self.klabel_uid = None
        if not self.klabel_uid:
            self.klabel_uid = str(uuid.uuid4())

        # fixme: it would be nice to clean up this label setting logic a bit
        #   and possibly abstract it out to something more generalized, but
        #   that is difficult to do given the differences in object attributes

        # Set the base metadata label
        if self.obj.metadata is None:
            self.obj.metadata = client.V1ObjectMeta()

        if self.obj.metadata.labels is None:
            self.obj.metadata.labels = {}

        if self.klabel_key not in self.obj.metadata.labels:
            self.obj.metadata.labels[self.klabel_key] = self.klabel_uid

        # If no spec is set, there is nothing to set additional labels on
        if self.obj.spec is None:
            log.warning("daemonset spec not set - cannot set kubetest label")
            return

        # Set the selector label
        if self.obj.spec.selector is None:
            self.obj.spec.selector = client.V1LabelSelector()

        if self.obj.spec.selector.match_labels is None:
            self.obj.spec.selector.match_labels = {}

        if self.klabel_key not in self.obj.spec.selector.match_labels:
            self.obj.spec.selector.match_labels[self.klabel_key] = self.klabel_uid

        # Set the template label
        if self.obj.spec.template is None:
            self.obj.spec.template = client.V1PodTemplateSpec()

        if self.obj.spec.template.metadata is None:
            self.obj.spec.template.metadata = client.V1ObjectMeta(labels={})

        if self.klabel_key not in self.obj.spec.template.metadata.labels:
            self.obj.spec.template.metadata.labels[self.klabel_key] = self.klabel_uid

    def create(self, namespace: str = None) -> None:
        """Create the DaemonSet under the given namespace.

        Args:
            namespace: The namespace to create the DaemonSet under.
                If the DaemonSet was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info(f'creating daemonset "{self.name}" in namespace "{self.namespace}"')
        log.debug(f"daemonset: {self.obj}")

        self.obj = self.api_client.create_namespaced_daemon_set(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the DaemonSet.

        This method expects the DaemonSet to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options: Options for DaemonSet deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info(f'deleting daemonset "{self.name}"')
        log.debug(f"delete options: {options}")
        log.debug(f"daemonset: {self.obj}")

        return self.api_client.delete_namespaced_daemon_set(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes DaemonSet resource."""
        self.obj = self.api_client.read_namespaced_daemon_set_status(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self) -> bool:
        """Check if the DaemonSet is in the ready state.

        Returns:
            True if in the ready state; False otherwise.
        """
        self.refresh()

        # if there is no status, the daemonset is definitely not ready
        status = self.obj.status
        if status is None:
            return False

        # check the status for the number of desired pod count and compare
        # it to the number of ready pods. if the numbers are
        # equal, the daemonset is ready; otherwise it is not ready.
        # TODO (etd) - we may want some logging in here eventually
        desired = status.desired_number_scheduled
        ready = status.number_ready

        if desired is None:
            return False

        return desired == ready

    def status(self) -> client.V1DaemonSetStatus:
        """Get the status of the DaemonSet.

        Returns:
            The status of the DaemonSet.
        """
        log.info(f'checking status of daemonset "{self.name}"')
        # first, refresh the daemonset state to ensure the latest status
        self.refresh()

        # return the status from the daemonset
        return self.obj.status

    def get_pods(self) -> List[Pod]:
        """Get the pods for the DaemonSet.

        Returns:
            A list of pods that belong to the DaemonSet.
        """
        log.info(f'getting pods for daemonset "{self.name}"')

        pods = client.CoreV1Api().list_namespaced_pod(
            namespace=self.namespace,
            label_selector=selector_string({self.klabel_key: self.klabel_uid}),
        )

        pods = [Pod(p) for p in pods.items]
        log.debug(f"pods: {pods}")
        return pods
