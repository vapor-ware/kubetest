"""Kubetest wrapper for the Kubernetes ``StatefulSet`` API Object."""

import logging
import uuid

from kubernetes import client

from kubetest.utils import selector_string

from .api_object import ApiObject
from .pod import Pod

log = logging.getLogger('kubetest')


class StatefulSet(ApiObject):
    """Kubetest wrapper around a Kubernetes `StatefulSet`_ API Object.

    The actual ``kubernetes.client.V1StatefulSet`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `StatefulSet`_.

    .. StatefulSet:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/#statefulset-v1-apps
    """

    obj_type = client.V1StatefulSet

    api_clients = {
        'preferred': client.AppsV1Api,
        'apps/v1': client.AppsV1Api,
        'apps/v1beta1': client.AppsV1beta1Api,
        'apps/v1beta2': client.AppsV1beta2Api,
    }

    def __init__(self, *args, **kwargs):
        super(StatefulSet, self).__init__(*args, **kwargs)
        self._add_kubetest_labels()

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def _add_kubetest_labels(self):
        """Add a kubetest label to the StatefulSet object.

        This allows kubetest to more easily and reliably search for and aggregate
        API objects, such as getting the Pods for a StatefulSet.

        The kubetest label key is "kubetest/<obj kind>" where the obj kind is
        the lower-cased kind of the obj.
        """
        self.klabel_key = 'kubetest/statefulset'
        self.klabel_uid = self.obj.metadata.labels.get(self.klabel_key, None)
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
            log.warning('statefulset spec not set - cannot set kubetest label')
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

    def create(self, namespace=None):
        """Create the StatefulSet under the given namespace.

        Args:
            namespace (str): The namespace to create the StatefulSet under.
                If the StatefulSet was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info('creating statefulset "%s" in namespace "%s"', self.name,
                 self.namespace)
        log.debug('statefulset: %s', self.obj)

        self.obj = self.api_client.create_namespaced_stateful_set(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options):
        """Delete the StatefulSet.

        This method expects the StatefulSet to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options (client.V1DeleteOptions): Options for StatefulSet deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting statefulset "%s"', self.name)
        log.debug('delete options: %s', options)
        log.debug('statefulset: %s', self.obj)

        return self.api_client.delete_namespaced_stateful_set(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes StatefulSet resource."""
        self.obj = self.api_client.read_namespaced_stateful_set_status(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self):
        """Check if the StatefulSet is in the ready state.

        Returns:
            bool: True if in the ready state; False otherwise.
        """
        self.refresh()

        # if there is no status, the statefulset is definitely not ready
        status = self.obj.status
        if status is None:
            return False

        # check the status for the number of total replicas and compare
        # it to the number of ready replicas. if the numbers are
        # equal, the statefulset is ready; otherwise it is not ready.
        # TODO (etd) - we may want some logging in here eventually
        total = status.replicas
        ready = status.ready_replicas

        if total is None:
            return False

        return total == ready

    def status(self):
        """Get the status of the StatefulSet.

        Returns:
            client.V1StatefulSetStatus: The status of the StatefulSet.
        """
        log.info('checking status of statefulset "%s"', self.name)
        # first, refresh the statefulset state to ensure the latest status
        self.refresh()

        # return the status from the statefulset
        return self.obj.status

    def get_pods(self):
        """Get the pods for the StatefulSet.

        Returns:
            list[Pod]: A list of pods that belong to the statefulset.
        """
        log.info('getting pods for statefulset "%s"', self.name)

        pods = client.CoreV1Api().list_namespaced_pod(
            namespace=self.namespace,
            label_selector=selector_string({self.klabel_key: self.klabel_uid})
        )

        pods = [Pod(p) for p in pods.items]
        log.debug('pods: %s', pods)
        return pods
