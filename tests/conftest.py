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
def simple_statefulset():
    """Return the Kubernetes config matching the simple-statefulset.yaml manifest."""
    return client.V1StatefulSet(
        api_version='apps/v1',
        kind='StatefulSet',
        metadata=client.V1ObjectMeta(
            name='postgres-statefulset',
            labels={
                'app': 'postgres'
            }
        ),
        spec=client.V1StatefulSetSpec(
            replicas=3,
            selector=client.V1LabelSelector(
                match_labels={
                    'app': 'postgres'
                }
            ),
            service_name='simple-service',
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={
                        'app': 'postgres'
                    }
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name='postgres',
                            image='postgres:9.6',
                            ports=[
                                client.V1ContainerPort(
                                    container_port=5432
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )


@pytest.fixture()
def simple_daemonset():
    """Return the Kubernetes config matching the simple-daemonset.yaml manifest."""
    return client.V1DaemonSet(
        api_version='apps/v1',
        kind='DaemonSet',
        metadata=client.V1ObjectMeta(
            name='canal-daemonset',
            labels={
                'app': 'canal'
            }
        ),
        spec=client.V1DaemonSetSpec(
            selector=client.V1LabelSelector(
                match_labels={
                    'app': 'canal'
                }
            ),
            template=client.V1PodTemplateSpec(
                metadata=client.V1ObjectMeta(
                    labels={
                        'app': 'canal'
                    }
                ),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name='canal',
                            image='canal:3.7.2',
                            ports=[
                                client.V1ContainerPort(
                                    container_port=9099
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


@pytest.fixture()
def simple_persistentvolume():
    """Return the Kubernetes config matching the simple-persistentvolume.yaml manifest."""
    return client.V1PersistentVolume(
        api_version='v1',
        kind='PersistentVolume',
        metadata=client.V1ObjectMeta(
            name='my-pv'
        ),
        spec=client.V1PersistentVolumeSpec(
            capacity={
                'storage': '16Mi'
            },
            access_modes=[
                'ReadWriteMany'
            ],
            local=client.V1LocalVolumeSource(
                path='/tmp/vol1'
            ),
            persistent_volume_reclaim_policy='Recycle',
            node_affinity=client.V1VolumeNodeAffinity(
                required=client.V1NodeSelector(
                    node_selector_terms=[
                        client.V1NodeSelectorTerm(
                            match_expressions=[
                                client.V1NodeSelectorRequirement(
                                    key='kubernetes.io/hostname',
                                    operator='In',
                                    values=[
                                        'my-node'
                                    ]
                                )
                            ]
                        )
                    ]
                )
            )
        )
    )
