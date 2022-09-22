"""Test fixtures for kubetest unit tests."""

import os

import pytest
from kubernetes import client


@pytest.fixture()
def manifest_dir():
    """Get the path to the test manifest directory."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")


@pytest.fixture()
def simple_deployment():
    """Return the Kubernetes config matching the simple-deployment.yaml manifest."""
    return client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="nginx-deployment", labels={"app": "nginx"}),
        spec=client.V1DeploymentSpec(
            replicas=3,
            selector=client.V1LabelSelector(match_labels={"app": "nginx"}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "nginx"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="nginx",
                            image="nginx:1.7.9",
                            ports=[client.V1ContainerPort(container_port=80)],
                        )
                    ]
                ),
            ),
        ),
    )


@pytest.fixture()
def simple_statefulset():
    """Return the Kubernetes config matching the simple-statefulset.yaml manifest."""
    return client.V1StatefulSet(
        api_version="apps/v1",
        kind="StatefulSet",
        metadata=client.V1ObjectMeta(
            name="postgres-statefulset", labels={"app": "postgres"}
        ),
        spec=client.V1StatefulSetSpec(
            replicas=3,
            selector=client.V1LabelSelector(match_labels={"app": "postgres"}),
            service_name="simple-service",
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "postgres"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="postgres",
                            image="postgres:9.6",
                            ports=[client.V1ContainerPort(container_port=5432)],
                        )
                    ]
                ),
            ),
        ),
    )


@pytest.fixture()
def simple_daemonset():
    """Return the Kubernetes config matching the simple-daemonset.yaml manifest."""
    return client.V1DaemonSet(
        api_version="apps/v1",
        kind="DaemonSet",
        metadata=client.V1ObjectMeta(name="canal-daemonset", labels={"app": "canal"}),
        spec=client.V1DaemonSetSpec(
            selector=client.V1LabelSelector(match_labels={"app": "canal"}),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(labels={"app": "canal"}),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="canal",
                            image="canal:3.7.2",
                            ports=[client.V1ContainerPort(container_port=9099)],
                        )
                    ]
                ),
            ),
        ),
    )


@pytest.fixture()
def simple_service():
    """Return the Kubernetes config matching the simple-service.yaml manifest."""
    return client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(name="my-service"),
        spec=client.V1ServiceSpec(
            selector={"app": "MyApp"},
            ports=[client.V1ServicePort(protocol="TCP", port=80, target_port=9376)],
        ),
    )


@pytest.fixture()
def simple_persistentvolumeclaim():
    """Return the Kubernetes config matching the simple-persistentvolumeclaim.yaml manifest."""
    return client.V1PersistentVolumeClaim(
        api_version="v1",
        kind="PersistentVolumeClaim",
        metadata=client.V1ObjectMeta(name="my-pvc"),
        spec=client.V1PersistentVolumeClaimSpec(
            access_modes=["ReadWriteMany"],
            resources=client.V1ResourceRequirements(requests={"storage": "16Mi"}),
        ),
    )


@pytest.fixture()
def simple_ingress():
    """Return the Kubernetes config matching the simple-ingress.yaml manifest."""
    return client.V1Ingress(
        api_version="networking.k8s.io/v1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(name="my-ingress"),
        spec=client.V1IngressSpec(
            rules=[client.V1IngressRule(
                host='my-host.com',
                http=client.V1HTTPIngressRuleValue(
                    paths=[client.V1HTTPIngressPath(
                        backend=client.V1IngressBackend(
                            service=client.V1IngressServiceBackend(
                                port=client.V1ServiceBackendPort(
                                    number=80,
                                ),
                                name="my-service")
                        ),
                        path="/",
                        path_type="Exact"
                    )]
                )
            )
            ]
        )
    )


@pytest.fixture()
def simple_replicaset():
    """Return the Kubernetes config matching the simple-replicaset.yaml manifest."""
    return client.V1ReplicaSet(
        api_version="apps/v1",
        kind="ReplicaSet",
        metadata=client.V1ObjectMeta(
            name="frontend",
            labels={
                "app": "guestbook",
                "tier": "frontend",
            },
        ),
        spec=client.V1ReplicaSetSpec(
            replicas=3,
            selector=client.V1LabelSelector(
                match_labels={
                    "tier": "frontend",
                },
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={
                        "tier": "frontend",
                    },
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="php-redis",
                            image="gcr.io/google_samples/gb-frontend:v3",
                        ),
                    ],
                ),
            ),
        ),
    )


@pytest.fixture()
def simple_serviceaccount():
    """Return the Kubernetes config matching the simple-serviceaccount.yaml manifest."""
    return client.V1ServiceAccount(
        api_version="v1",
        kind="ServiceAccount",
        metadata=client.V1ObjectMeta(name="build-robot"),
    )


@pytest.fixture()
def simple_networkpolicy():
    """Return the Kubernetes config matching the simple-networkpolicy.yaml manifest."""
    return client.V1NetworkPolicy(
        api_version="networking.k8s.io/v1",
        kind="NetworkPolicy",
        metadata=client.V1ObjectMeta(name="default-deny"),
        spec=client.V1NetworkPolicySpec(
            pod_selector=client.V1LabelSelector(),
            policy_types=["Egress", "Ingress"],
        ),
    )
