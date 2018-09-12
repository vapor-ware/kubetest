"""
"""

import os

import pytest
from kubernetes import client


@pytest.fixture()
def manifest_dir():
    """Get the path to the test manifest directory."""
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data')


@pytest.fixture()
def simple_deployment():
    """Return the Kubernetes config matching the simple-deployment.yaml manifest."""
    return client.V1Deployment(
        api_version='apps/v1',
        kind='Deployment',
        metadata=client.V1ObjectMeta(
            name='nginx-deployment',
            labels={
                'app': 'nginx'
            }
        ),
        spec=client.V1DeploymentSpec(
            replicas=3,
            selector=client.V1LabelSelector(
                match_labels={
                    'app': 'nginx'
                }
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={
                        'app': 'nginx'
                    }
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name='nginx',
                            image='nginx:1.7.9',
                            ports=[
                                client.V1ContainerPort(
                                    container_port=80
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )


@pytest.fixture()
def simple_service():
    """Return the Kubernetes config matching the simple-service.yaml manifest."""
    return client.V1Service(
        api_version='v1',
        kind='Service',
        metadata=client.V1ObjectMeta(
            name='my-service'
        ),
        spec=client.V1ServiceSpec(
            selector={
                'app': 'MyApp'
            },
            ports=[
                client.V1ServicePort(
                    protocol='TCP',
                    port=80,
                    target_port=9376
                )
            ]
        )
    )
