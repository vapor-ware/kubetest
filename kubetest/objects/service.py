"""Kubetest wrapper for the Kubernetes ``Service`` API Object."""

import logging

from kubernetes import client

from .api_object import ApiObject

log = logging.getLogger('kubetest')


class Service(ApiObject):
    """Kubetest wrapper around a Kubernetes `Service`_ API Object.

    The actual ``kubernetes.client.V1Service`` instance that this
    wraps can be accessed via the ``obj`` instance member.

    This wrapper provides some convenient functionality around the
    API Object and provides some state management for the `Service`_.

    .. _Service:
        https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.10/#service-v1-core
    """

    obj_type = client.V1Service

    api_clients = {
        'preferred': client.CoreV1Api,
        'v1': client.CoreV1Api,
    }

    def __str__(self):
        return str(self.obj)

    def __repr__(self):
        return self.__str__()

    def create(self, namespace=None):
        """Create the Service under the given namespace.

        Args:
            namespace (str): The namespace to create the Service under.
                If the Service was loaded via the kubetest client, the
                namespace will already be set, so it is not needed here.
                Otherwise, the namespace will need to be provided.
        """
        if namespace is None:
            namespace = self.namespace

        log.info('creating service "%s" in namespace "%s"', self.name, self.namespace)
        log.debug('service: %s', self.obj)

        self.obj = self.api_client.create_namespaced_service(
            namespace=namespace,
            body=self.obj,
        )

    def delete(self, options):
        """Delete the Service.

        This method expects the Service to have been loaded or otherwise
        assigned a namespace already. If it has not, the namespace will need
        to be set manually.

        Args:
            options (client.V1DeleteOptions): Options for Service deletion.

        Returns:
            client.V1Status: The status of the delete operation.
        """
        if options is None:
            options = client.V1DeleteOptions()

        log.info('deleting service "%s"', self.name)
        log.debug('delete options: %s', options)
        log.debug('service: %s', self.obj)

        return self.api_client.delete_namespaced_service(
            name=self.name,
            namespace=self.namespace,
            body=options,
        )

    def refresh(self):
        """Refresh the underlying Kubernetes Service resource."""
        self.obj = self.api_client.read_namespaced_service(
            name=self.name,
            namespace=self.namespace,
        )

    def is_ready(self):
        """Check if the Service is in the ready state.

        The readiness state is not clearly available from the Service
        status, so to see whether or not the Service is ready this
        will check whether the endpoints of the Service are ready.

        This comes with the caveat that in order for a Service to
        have endpoints, there needs to be some backend hooked up to it.
        If there is no backend, the Service will never have endpoints,
        so this will never resolve to True.

        Returns:
            bool: True if in the ready state; False otherwise.
        """
        self.refresh()

        # check the status. if there is no status, the service is
        # definitely not ready.
        if self.obj.status is None:
            return False

        endpoints = self.get_endpoints()

        # if the Service has no endpoints, its not ready.
        if len(endpoints) == 0:
            return False

        # get the service endpoints and check that they are all ready.
        for endpoint in endpoints:
            # if we have an endpoint, but there are no subsets, we
            # consider the endpoint to be not ready.
            if endpoint.subsets is None:
                return False

            for subset in endpoint.subsets:
                # if the endpoint has no addresses setup yet, its not ready
                if subset.addresses is None or len(subset.addresses) == 0:
                    return False

                # if there are still addresses that are not ready, the
                # service is not ready
                not_ready = subset.not_ready_addresses
                if not_ready is not None and len(not_ready) > 0:
                    return False

        # if we got here, then all endpoints are ready, so the service
        # must also be ready
        return True

    def status(self):
        """Get the status of the Service.

        Returns:
            client.V1ServiceStatus: The status of the Service.
        """
        log.info('checking status of service "%s"', self.name)
        # first, refresh the service state to ensure the latest status
        self.refresh()

        # return the status from the service
        return self.obj.status

    def get_endpoints(self):
        """Get the endpoints for the Service.

        This can be useful for checking internal IP addresses used
        in containers, e.g. for container auto-discovery.

        Returns:
            list[client.V1Endpoints]: A list of endpoints associated
            with the Service.
        """
        log.info('getting endpoints for service "%s"', self.name)
        endpoints = self.api_client.list_namespaced_endpoints(
            namespace=self.namespace,
        )

        svc_endpoints = []
        for endpoint in endpoints.items:
            # filter to include only the endpoints with the same
            # name as the service.
            if endpoint.metadata.name == self.name:
                svc_endpoints.append(endpoint)

        log.debug('endpoints: %s', svc_endpoints)
        return svc_endpoints

    def proxy_http_get(self, path):
        """Issue a GET request to proxy of a Service.

        Args:
            path (str): The URI path for the request.

        Returns:
            str: The response data
        """
        return client.CoreV1Api().connect_get_namespaced_service_proxy_with_path(
            name="{}:{}".format(self.name, self.obj.spec.ports[0].port),
            namespace=self.namespace,
            path=path,
        )
