"""Kubetest wrapper for the Kubernetes ``Job`` API Object."""

import logging
import uuid
from typing import List

from kubernetes import client

from kubetest.utils import selector_string

from kubetest.objects.api_object import ApiObject
from kubetest.objects.pod import Pod

log = logging.getLogger("kubetest")


class Job(ApiObject):
    """Kubetest wrapper around a Kubernetes `Job`_ API Object.

    The actual ``kubernetes.client.V1Job`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `V1Job`_.

    .. _Job:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.21/#job-v1-batch
    """

    obj_type = client.V1Job

    api_clients = {
        "preferred": client.BatchV1Api,
        "batch/v1": client.BatchV1Api,
    }

    def __init__(self, *args, **kwargs) -> None:
        super(Job, self).__init__(*args, **kwargs)
        self._add_kubetest_labels()

    def _add_kubetest_labels(self) -> None:
        """Add a kubetest label to the Job object.

        This allows kubetest to more easily and reliably search for and aggregate
        API objects, such as getting the Pods for a Job.

        The kubetest label key is "kubetest/<obj kind>" where the obj kind is
        the lower-cased kind of the obj.
        """
        self.klabel_key = "kubetest/job"
        if self.obj.metadata.labels:
            self.klabel_uid = self.obj.metadata.labels.get(self.klabel_key, None)
        else:
            self.klabel_uid = None
        if not self.klabel_uid:
            self.klabel_uid = str(uuid.uuid4())

        # FIXME: it would be nice to clean up this label setting logic a bit
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
            log.warning("job spec not set - cannot set kubetest label")
            return

        self.obj.spec.manual_selector = True

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
        """Create the Job under the given namespace.

        Args:
            namespace: The namespace to create the Job under.
                If the Job was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info(f'creating job "{self.name}" in namespace "{self.namespace}"')
        log.debug(f"job: {self.obj}")

        self.obj = self.api_client.create_namespaced_job(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options: client.V1DeleteOptions = None) -> client.V1Status:
        """Delete the Job.

        This method expects the Job to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options: Options for Job deletion.

        Returns:
            The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info(f'deleting job "{self.name}"')
        log.debug(f"delete options: {options}")
        log.debug(f"job: {self.obj}")

        return self.api_client.delete_namespaced_job(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self) -> None:
        """Refresh the underlying Kubernetes Job resource."""
        self.obj = self.api_client.read_namespaced_job_status(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self) -> bool:
        """Check if the Job is in the ready state.

        Returns:
            True if in the ready state; False otherwise.
        """
        self.refresh()

        # if there is no status, the job is definitely not ready
        status = self.obj.status
        if status is None:
            return False

        # check the status for the start_time
        # it start_time is set then job is 'ready'
        if hasattr(status, 'start_time'):
            return status.start_time is not None
        else:
            return False

    def is_completed(self) -> bool:
        """
        Check if the Job is completed
        :return:
        """
        status = self.status()
        if hasattr(status, 'completion_time'):
            return status.completion_time is not None
        else:
            return False

    def status(self) -> client.V1JobStatus:
        """Get the status of the Job.

        Returns:
            The status of the Job.
        """
        log.info(f'checking status of job "{self.name}"')
        # first, refresh the job state to ensure the latest status
        self.refresh()

        # return the status from the job
        return self.obj.status

    def get_pod_status_counts(self) -> tuple:
        status = self.status()
        active = 0
        if hasattr(status, 'active') and status.active is not None:
            active = status.active

        succeeded = 0
        if hasattr(status, 'succeeded') and status.succeeded is not None:
            succeeded = status.succeeded

        failed = 0
        if hasattr(status, 'failed') and status.failed is not None:
            failed = status.failed

        return active, succeeded, failed

    def get_pods(self) -> List[Pod]:
        """Get the pods for the Job.

        Returns:
            A list of pods that belong to the Job.
        """
        log.info(f'getting pods for job "{self.name}"')

        pods = client.CoreV1Api().list_namespaced_pod(
            namespace=self.namespace,
            label_selector=selector_string({self.klabel_key: self.klabel_uid}),
        )

        pods = [Pod(p) for p in pods.items]
        log.debug(f"pods: {pods}")
        return pods
