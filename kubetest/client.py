"""The test client for managing Kubernetes resources within test cases.

An instance of the ``TestClient`` defined in this module is automatically
created for each test case that uses the ``kube`` fixture. The ``kube``
fixture provides the ``TestClient`` instance to the test case.
"""

import logging
from typing import Dict, Optional, Union

from kubernetes import client

from kubetest import objects, utils
from kubetest.condition import Condition, Policy, check_and_sort

log = logging.getLogger('kubetest')


class TestClient:
    """Test client for managing Kubernetes resources for a test case.

    The ``namespace`` for the TestClient will be automatically generated and
    provided to the TestClient during the test setup process.

    Args:
        namespace: The namespace associated with the test client. Each test
            case will have its own namespace assigned.
    """

    def __init__(self, namespace: str) -> None:
        self.namespace = namespace
        self.pre_registered = []

    # ****** Generic Helpers on ApiObjects ******

    def create(self, obj: objects.ApiObject) -> None:
        """Create the provided ApiObject on the Kubernetes cluster.

        If the object does not already have a namespace assigned to it, the client's
        generated test case namespace will be used.

        Args:
            obj: A kubetest API Object wrapper.
        """
        if obj.namespace is None:
            obj.namespace = self.namespace

        obj.create()

    def delete(self, obj: objects.ApiObject, options: client.V1DeleteOptions = None) -> None:
        """Delete the provided ApiObject from the Kubernetes cluster.

        If the object does not already have a namespace assigned to it, the client's
        generated test case namespace will be used.

        Args:
            obj: A kubetest API Object wrapper.
            options: Additional options for deleting the resource from the cluster.
        """
        if obj.namespace is None:
            obj.namespace = self.namespace

        obj.delete(options=options)

    @staticmethod
    def refresh(obj: objects.ApiObject) -> None:
        """Refresh the underlying Kubernetes resource status and state.

        Args:
            obj: A kubetest API Object wrapper.
        """
        obj.refresh()

    # ****** Manifest Loaders ******

    @staticmethod
    def load_clusterrolebinding(
            path: str,
            name: Optional[str] = None,
    ) -> objects.ClusterRoleBinding:
        """Load a manifest YAML into a ClusterRoleBinding object.

        Args:
            path: The path to the ClusterRoleBinding manifest.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The ClusterRoleBinding for the specified manifest.
        """
        log.info(f'loading clusterrolebinding from path: {path}')
        return objects.ClusterRoleBinding.load(path, name=name)

    def load_configmap(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.ConfigMap:
        """Load a manifest YAML into a ConfigMap object.

        By default, this will augment the ConfigMap object with the generated
        test case namespace. This behavior can be disabled with the
        ``set_namespace`` flag.

        Args:
            path: The path to the ConfigMap manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                ConfigMap namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The ConfigMap for the specified manifest.
        """
        log.info(f'loading configmap from path: {path}')
        configmap = objects.ConfigMap.load(path, name=name)
        if set_namespace:
            configmap.namespace = self.namespace
        return configmap

    def load_daemonset(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.DaemonSet:
        """Load a manifest YAML into a DaemonSet object.

        By default, this will augment the DaemonSet object with the generated test
        case namespace. This behavior can be disabled with the ``set_namespace`` flag.

        Args:
            path: The path to the DaemonSet manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                DaemonSet namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The DaemonSet for the specified manifest.
        """
        log.info(f'loading daemonset from path: {path}')
        daemonset = objects.DaemonSet.load(path, name=name)
        if set_namespace:
            daemonset.namespace = self.namespace
        return daemonset

    def load_deployment(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.Deployment:
        """Load a manifest YAML into a Deployment object.

        By default, this will augment the Deployment object with the generated
        test case namespace. This behavior can be disabled with the
        ``set_namespace`` flag.

        Args:
            path: The path to the Deployment manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                Deployment namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The Deployment for the specified manifest.
        """
        log.info(f'loading deployment from path: {path}')
        deployment = objects.Deployment.load(path, name=name)
        if set_namespace:
            deployment.namespace = self.namespace
        return deployment

    def load_pod(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.Pod:
        """Load a manifest YAML into a Pod object.

        By default, this will augment the Pod object with the generated test case
        namespace. This behavior can be disabled with the ``set_namespace`` flag.

        Args:
            path: The path to the Pod manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                Pod namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The Pod for the specified manifest.
        """
        log.info(f'loading pod from path: {path}')
        pod = objects.Pod.load(path, name=name)
        if set_namespace:
            pod.namespace = self.namespace
        return pod

    def load_rolebinding(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.RoleBinding:
        """Load a manifest YAML into a RoleBinding object.

        By default, this will augment the RoleBinding object with the generated
        test case namespace. This behavior can be disabled with the
        ``set_namespace`` flag.

        Args:
            path: The path to the RoleBinding manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                RoleBinding namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The RoleBinding for the specified manifest.
        """
        log.info(f'loading rolebinding from path: {path}')
        rolebinding = objects.RoleBinding.load(path, name=name)
        if set_namespace:
            rolebinding.namespace = self.namespace
        return rolebinding

    def load_secret(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.Secret:
        """Load a manifest YAML into a Secret object.

        By default, this will augment the Secret object with the generated
        test case namespace. This behavior can be disabled with the
        ``set_namespace`` flag.

        Args:
            path: The path to the Secret manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                Secret namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The Secret for the specified manifest.
        """
        log.info(f'loading secret from path: {path}')
        secret = objects.Secret.load(path, name=name)
        if set_namespace:
            secret.namespace = self.namespace
        return secret

    def load_service(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.Service:
        """Load a manifest YAML into a Service object.

        By default, this will augment the Service object with the generated
        test case namespace. This behavior can be disabled with the
        ``set_namespace`` flag.

        Args:
            path: The path to the Service manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                Service namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The Service for the specified manifest.
        """
        log.info(f'loading service from path: {path}')
        service = objects.Service.load(path, name=name)
        if set_namespace:
            service.namespace = self.namespace
        return service

    def load_persistentvolumeclaim(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.PersistentVolumeClaim:
        """Load a manifest YAML into a PersistentVolumeClaim object.

        By default, this will augment the PersistentVolumeClaim object with
        the generated test case namespace. This behavior can be
        disabled with the ``set_namespace`` flag.

        Args:
            path (str): The path to the PersistentVolumeClaim manifest.
            set_namespace (bool): Enable/disable the automatic
                augmentation of the PersistentVolumeClaim namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            objects.PersistentVolumeClaim: The PersistentVolumeClaim for the specified
            manifest.
        """
        log.info('loading persistentvolumeclaim from path: %s', path)
        persistentvolumeclaim = objects.PersistentVolumeClaim.load(path, name=name)
        if set_namespace:
            persistentvolumeclaim.namespace = self.namespace
        return persistentvolumeclaim

    def load_ingress(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.Ingress:
        """Load a manifest YAML into a Ingress object.

        By default, this will augment the Ingress object with
        the generated test case namespace. This behavior can be
        disabled with the ``set_namespace`` flag.

        Args:
            path (str): The path to the Ingress manifest.
            set_namespace (bool): Enable/disable the automatic
                augmentation of the Ingress namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            objects.Ingress: The ingress for the specified manifest.
        """
        log.info('loading ingress from path: %s', path)
        ingress = objects.Ingress.load(path, name=name)
        if set_namespace:
            ingress.namespace = self.namespace
        return ingress

    def load_replicaset(
            self, path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.ReplicaSet:
        """Load a manifest YAML into a ReplicaSet object.

        By default, this will augment the ReplicaSet object with the generated
        test case namespace. This behavior can be disabled with the
        ``set_namespace`` flag.

        Args:
            path: The path to the ReplicaSet manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                ReplicaSet namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The ReplicaSet for the specified manifest.
        """
        log.info(f'loading replicaset from path: {path}')
        replicaset = objects.ReplicaSet.load(path, name=name)
        if set_namespace:
            replicaset.namespace = self.namespace
        return replicaset

    def load_statefulset(
            self, path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.StatefulSet:
        """Load a manifest YAML into a StatefulSet object.

        By default, this will augment the StatefulSet object with the generated
        test case namespace. This behavior can be disabled with the
        ``set_namespace`` flag.

        Args:
            path: The path to the StatefulSet manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                StatefulSet namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The StatefulSet for the specified manifest.
        """
        log.info(f'loading statefulset from path: {path}')
        statefulset = objects.StatefulSet.load(path, name=name)
        if set_namespace:
            statefulset.namespace = self.namespace
        return statefulset

    def load_serviceaccount(
            self,
            path: str,
            set_namespace: bool = True,
            name: Optional[str] = None,
    ) -> objects.ServiceAccount:
        """Load a manifest YAML into a ServiceAccount object.

        By default, this will augment the ServiceAccount object with the generated
        test case namespace. This behavior can be disabled with the
        ``set_namespace`` flag.

        Args:
            path: The path to the ServiceAccount manifest.
            set_namespace: Enable/disable the automatic augmentation of the
                ServiceAccount namespace.
            name: The name of the resource to load. If the manifest file
                contains a single object definition for the type being
                loaded, it is not necessary to specify the name. If the
                manifest has multiple definitions containing the same
                type, a name is required to differentiate between them.
                If no name is specified in such case, an error is raised.

        Returns:
            The ServiceAccount for the specified manifest.
        """
        log.info(f'loading serviceaccount from path: {path}')
        serviceaccount = objects.ServiceAccount.load(path, name=name)
        if set_namespace:
            serviceaccount.namespace = self.namespace
        return serviceaccount

    # ****** General Helpers ******

    def get_configmaps(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.ConfigMap]:
        """Get ConfigMaps from the cluster.

        Args:
            namespace: The namespace to get the ConfigMaps from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of ConfigMaps to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of ConfigMaps to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the ConfigMap name and the value is the
            ConfigMap itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.ConfigMap.preferred_client().list_namespaced_config_map(
            namespace=namespace,
            **selectors,
        )

        configmaps = {}
        for obj in results.items:
            cm = objects.ConfigMap(obj)
            configmaps[cm.name] = cm

        return configmaps

    def get_daemonsets(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.DaemonSet]:
        """Get DaemonSets from the cluster.

        Args:
            namespace: The namespace to get the DaemonSets from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of DaemonSets to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of DaemonSets to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the DaemonSet name and the value is the
            DaemonSet itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.DaemonSet.preferred_client().list_namespaced_daemon_set(
            namespace=namespace,
            **selectors,
        )

        daemonsets = {}
        for obj in results.items:
            daemonset = objects.DaemonSet(obj)
            daemonsets[daemonset.name] = daemonset

        return daemonsets

    def get_deployments(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.Deployment]:
        """Get Deployments from the cluster.

        Args:
            namespace: The namespace to get the Deployments from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of Deployments to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of Deployments to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the Deployment name and the value is the
            Deployment itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.Deployment.preferred_client().list_namespaced_deployment(
            namespace=namespace,
            **selectors,
        )

        deployments = {}
        for obj in results.items:
            deployment = objects.Deployment(obj)
            deployments[deployment.name] = deployment

        return deployments

    def get_endpoints(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.Endpoints]:
        """Get Endpoints from the cluster.

        Args:
            namespace: The namespace to get the Endpoints from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of Endpoints to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of Endpoints to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the Endpoint name and the value is the
            Endpoint itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.Endpoints.preferred_client().list_namespaced_endpoints(
            namespace=namespace,
            **selectors,
        )

        endpoints = {}
        for obj in results.items:
            endpoint = objects.Endpoints(obj)
            endpoints[endpoint.name] = endpoint

        return endpoints

    def get_events(
            self,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
            all_namespaces: bool = False,
    ) -> Dict[str, objects.Event]:
        """Get the latest Events that occurred in the cluster.

        Args:
            fields: A dictionary of fields used to restrict the returned collection
                of Events to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of Events to only those which match these label selectors. By
                default, no restricting is done.
            all_namespaces: If True, get the events across all namespaces.

        Returns:
            A dictionary where the key is the Event name and the value is the
            Event itself.
        """
        selectors = utils.selector_kwargs(fields, labels)

        if all_namespaces:
            results = client.CoreV1Api().list_event_for_all_namespaces(
                **selectors
            )
        else:
            results = client.CoreV1Api().list_namespaced_event(
                namespace=self.namespace,
                **selectors
            )

        events = {}
        for obj in results.items:
            event = objects.Event(obj)
            events[event.name] = event

        return events

    def get_namespaces(
            self,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.Namespace]:
        """Get Namespaces from the cluster.

        Args:
            fields: A dictionary of fields used to restrict the returned collection
                of Namespaces to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of Namespaces to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the Namespace name and the value is the
            Namespace itself.
        """
        selectors = utils.selector_kwargs(fields, labels)

        results = objects.Namespace.preferred_client().list_namespace(
            **selectors,
        )

        namespaces = {}
        for obj in results.items:
            namespace = objects.Namespace(obj)
            namespaces[namespace.name] = namespace

        return namespaces

    @staticmethod
    def get_nodes(
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.Node]:
        """Get the Nodes that make up the cluster.

        Args:
            fields: A dictionary of fields used to restrict the returned collection
                of Nodes to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of Nodes to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the Node name and the value is the
            Node itself.
        """
        selectors = utils.selector_kwargs(fields, labels)

        results = client.CoreV1Api().list_node(
            **selectors,
        )

        nodes = {}
        for obj in results.items:
            node = objects.Node(obj)
            nodes[node.name] = node

        return nodes

    def get_pods(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.Pod]:
        """Get Pods from the cluster.

        Args:
            namespace: The namespace to get the Pods from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of Pods to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of Pods to only those which match these label selectors. By default,
                no restricting is done.

        Returns:
            A dictionary where the key is the Pod name and the value is the
            Pod itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.Pod.preferred_client().list_namespaced_pod(
            namespace=namespace,
            **selectors,
        )

        pods = {}
        for obj in results.items:
            pod = objects.Pod(obj)
            pods[pod.name] = pod

        return pods

    def get_secrets(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.Secret]:
        """Get Secrets from the cluster.

        Args:
            namespace: The namespace to get the Secrets from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of Secrets to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of Secrets to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the Secret name and the value is the
            Secret itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.Secret.preferred_client().list_namespaced_secret(
            namespace=namespace,
            **selectors,
        )

        secrets = {}
        for obj in results.items:
            secret = objects.Secret(obj)
            secrets[secret.name] = secret

        return secrets

    def get_services(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.Service]:
        """Get Services under the test case namespace.

        Args:
            namespace: The namespace to get the Services from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of Services to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of Services to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the Service name and the value is the
            Service itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.Service.preferred_client().list_namespaced_service(
            namespace=namespace,
            **selectors,
        )

        services = {}
        for obj in results.items:
            service = objects.Service(obj)
            services[service.name] = service

        return services

    def get_persistentvolumeclaims(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.PersistentVolumeClaim]:
        """Get PersistentVolumeClaims from the cluster.

        Args:
            namespace: The namespace to get the PersistentVolumeClaim from. If not
                specified, it will use the auto-generated test case namespace
                by default.
            fields: A dictionary of fields used to restrict the returned collection
                of PersistentVolumeClaim to only those which match these field
                selectors. By default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of PersistentVolumeClaim to only those which match these label
                selectors. By default, no restricting is done.

        Returns:
            A dictionary where the key is the PersistentVolumeClaim name and the
            value is the PersistentVolumeClaim itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        c = objects.PersistentVolumeClaim.preferred_client()
        results = c.list_namespaced_persistent_volume_claim(
            namespace=namespace,
            **selectors,
        )

        persistentvolumeclaims = {}
        for obj in results.items:
            persistentvolumeclaim = objects.PersistentVolumeClaim(obj)
            persistentvolumeclaims[persistentvolumeclaim.name] = persistentvolumeclaim

        return persistentvolumeclaims

    def get_ingresses(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.Ingress]:
        """Get Ingresses from the cluster.

        Args:
            namespace: The namespace to get the Ingress from. If not
                specified, it will use the auto-generated test case namespace
                by default.
            fields: A dictionary of fields used to restrict the returned collection
                of Ingress to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of Ingress to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the Ingress name and the value
            is the Ingress itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.Ingress.preferred_client().list_namespaced_ingress(
            namespace=namespace,
            **selectors,
        )

        ingresses = {}
        for obj in results.items:
            ingress = objects.Ingress(obj)
            ingresses[ingress.name] = ingress

        return ingresses

    def get_replicasets(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.ReplicaSet]:
        """Get ReplicaSets from the cluster.

        Args:
            namespace: The namespace to get the ReplicaSets from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of ReplicaSets to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of ReplicaSets to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the ReplicaSet name and the value is the
            ReplicaSet itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.ReplicaSet.preferred_client().list_namespaced_replica_set(
            namespace=namespace,
            **selectors,
        )

        replicasets = {}
        for obj in results.items:
            rs = objects.ReplicaSet(obj)
            replicasets[replicasets.name] = rs

        return replicasets

    def get_statefulsets(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.StatefulSet]:
        """Get StatefulSets from the cluster.

        Args:
            namespace: The namespace to get the StatefulSets from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of StatefulSets to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of StatefulSets to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the StatefulSet name and the value is the
            StatefulSet itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.StatefulSet.preferred_client().list_namespaced_stateful_set(
            namespace=namespace,
            **selectors,
        )

        statefulsets = {}
        for obj in results.items:
            statefulset = objects.StatefulSet(obj)
            statefulsets[statefulset.name] = statefulset

        return statefulsets

    def get_serviceaccounts(
            self,
            namespace: str = None,
            fields: Dict[str, str] = None,
            labels: Dict[str, str] = None,
    ) -> Dict[str, objects.ServiceAccount]:
        """Get ServiceAccounts from the cluster.

        Args:
            namespace: The namespace to get the ServiceAccount from. If not specified,
                it will use the auto-generated test case namespace by default.
            fields: A dictionary of fields used to restrict the returned collection
                of ServiceAccount to only those which match these field selectors. By
                default, no restricting is done.
            labels: A dictionary of labels used to restrict the returned collection
                of ServiceAccount to only those which match these label selectors. By
                default, no restricting is done.

        Returns:
            A dictionary where the key is the ServiceAccount name and the value is the
            ServiceAccount itself.
        """
        if namespace is None:
            namespace = self.namespace

        selectors = utils.selector_kwargs(fields, labels)

        results = objects.ServiceAccount.preferred_client().list_namespaced_service_account(
            namespace=namespace,
            **selectors,
        )

        serviceaccount = {}
        for obj in results.items:
            cm = objects.ServiceAccount(obj)
            serviceaccount[cm.name] = cm

        return serviceaccount

    # ****** Test Helpers ******

    @staticmethod
    def wait_for_conditions(
            *args: Condition,
            timeout: int = None,
            interval: Union[float, int] = 1,
            policy: Policy = Policy.ONCE,
            fail_on_api_error: bool = True,
    ) -> None:
        """Wait for all of the provided Conditions to be met.

        All Conditions must be met for this to unblock. If no Conditions are
        provided, this method will do nothing.

        Args:
            *args: Conditions to check.
            timeout: The maximum time to wait, in seconds, for the provided
                Conditions to be met. If all of the Conditions are not met within
                the given timeout, this will raise a TimeoutError. By default,
                there is no timeout so this will wait indefinitely.
            interval: The time, in seconds, to sleep before re-evaluating the
                conditions. Default: 1s
            policy: The condition checking policy that defines the checking
                behavior. Default: ONCE
            fail_on_api_error: Fail the condition checks if a Kubernetes API error
                is incurred. An API error can be raised for a number of reasons,
                including a Pod being restarted and temporarily unavailable.
                Disabling this will cause those errors to be ignored, allowing
                the check to continue until timeout or resolution. (default: True).

        Raises:
            TimeoutError: The Conditions were not met within the specified
                timeout period.
            ValueError: Not all arguments are a Condition.
        """
        # If no Conditions were given, there is nothing to do.
        if not args:
            return

        # If something was given, make sure they are all Conditions
        if not all(map(lambda c: isinstance(c, Condition), args)):
            raise ValueError('All arguments must be a Condition')

        # make a copy of the conditions
        to_check = list(args)

        def condition_checker(conditions):
            # check that the conditions were met according to the
            # condition checking policy
            met, unmet = check_and_sort(*conditions)
            if policy == Policy.ONCE:
                log.info(f'check met: {met}')
                conditions[:] = unmet
                return len(unmet) == 0

            elif policy == Policy.SIMULTANEOUS:
                return len(unmet) == 0 and len(met) == len(args)

            else:
                raise ValueError(
                    f'Invalid condition policy specified: {policy}',
                )

        wait_condition = Condition(
            'wait for conditions',
            condition_checker,
            to_check,
        )

        try:
            utils.wait_for_condition(
                condition=wait_condition,
                timeout=timeout,
                interval=interval,
                fail_on_api_error=fail_on_api_error,
            )
        except TimeoutError:
            # If we time out here, we want to show all the conditions
            # that we weren't able to resolve in the error message, not
            # the 'wait for conditions' wrapper.
            raise TimeoutError(
                f'timed out wile waiting for conditions to be met: {to_check}',
            )

    def wait_for_ready_nodes(
            self,
            count: int,
            timeout: int = None,
            interval: Union[int, float] = 1,
    ) -> None:
        """Wait until there are at least ``count`` number of nodes available
        in the cluster.

        Notes:
            This should only be used for clusters that auto-scale the
            nodes. This will not create/delete nodes on its own.

        Args:
            count: The number of nodes to wait for.
            timeout: The maximum time to wait, in seconds.
            interval: The time, in seconds, to sleep before re-checking the
                number of nodes.
        """
        def node_count_match(node_count):
            nodes = self.get_nodes()
            return [n.is_ready() for n in nodes.values()].count(True) >= node_count

        wait_condition = Condition(
            f'wait for {count} nodes',
            node_count_match,
            count,
        )

        utils.wait_for_condition(
            condition=wait_condition,
            timeout=timeout,
            interval=interval,
        )

    def wait_for_registered(self, timeout: int = None, interval: Union[int, float] = 1) -> None:
        """Wait for all of the pre-registered objects to be ready on the cluster.

        An object is pre-registered with the test client if it is specified
        to the test via the ``applymanifests`` pytest marker. The marker will load
        the manifest and add the object to the cluster, and register it with
        the test client. This method waits until all such loaded manifest objects
        are in the ready state simultaneously.

        Args:
            timeout: The maximum time to wait, in seconds.
            interval: The time, in seconds, to sleep before re-checking the ready
                state for pre-registered objects.
        """
        def check_registered():
            for obj in self.pre_registered:
                if not obj.is_ready():
                    return False
            return True

        wait_condition = Condition(
            'wait for pre-registered objects to be ready',
            check_registered,
        )

        utils.wait_for_condition(
            condition=wait_condition,
            timeout=timeout,
            interval=interval,
        )

    @staticmethod
    def wait_until_created(
            obj: objects.ApiObject,
            timeout: int = None,
            interval: Union[int, float] = 1,
    ) -> None:
        """Wait until the specified object has been created.

        Here, creation is judged on whether or not refreshing the object (e.g.
        getting it) returns an object (created) or an error (not yet created).

        Args:
            obj: The ApiObject to wait on.
            timeout: The maximum time to wait, in seconds.
            interval: The time, in seconds, to sleep before re-checking the
                created state of the object.
        """
        def check_ready(api_obj):
            try:
                api_obj.refresh()
            except:  # noqa
                return False
            return True

        wait_condition = Condition(
            f'wait for {type(obj).__name__}:{obj.name} to be created',
            check_ready,
            obj,
        )

        utils.wait_for_condition(
            condition=wait_condition,
            timeout=timeout,
            interval=interval
        )
