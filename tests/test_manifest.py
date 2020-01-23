"""Unit tests for the kubetest.manifest package."""

import os

import pytest
import yaml
from kubernetes import client

from kubetest import manifest


class TestCastValue:
    """Tests for kubetest.manifest.cast_value"""

    @pytest.mark.parametrize(
        'value,t,expected', [
            # builtin types
            (11, 'int', int(11)),
            ('11', 'int', int(11)),
            (11.0, 'int', int(11)),
            (11, 'float', float(11)),
            (11, 'str', '11'),

            # casting to object should result in no change
            (11, 'object', 11),
            ('11', 'object', '11'),

            # kubernetes types
            (
                {'apiVersion': 'apps/v1', 'kind': 'Namespace'},
                'V1Namespace',
                client.V1Namespace(kind='Namespace', api_version='apps/v1')),
            (
                {'fieldRef': {'apiVersion': 'apps/v1beta1', 'fieldPath': 'foobar'}},
                'V1EnvVarSource',
                client.V1EnvVarSource(field_ref=client.V1ObjectFieldSelector(
                    api_version='apps/v1beta1', field_path='foobar'
                ))),
            (
                {'finalizers': ['a', 'b', 'c']},
                'V1ObjectMeta',
                client.V1ObjectMeta(finalizers=['a', 'b', 'c'])),
        ]
    )
    def test_ok(self, value, t, expected):
        """Test casting values to the specified type successfully."""

        actual = manifest.cast_value(value, t)
        assert type(actual) == type(expected)
        assert actual == expected

    @pytest.mark.parametrize(
        'value,t,error', [
            # builtin types
            ({'foo': 'bar'}, 'int', TypeError),
            ([1, 3, 5], 'float', TypeError),
            (1.0, 'set', TypeError),

            # kubernetes types
            (11, 'V1Namespace', AttributeError),
            ('foo', 'V1Deployment', AttributeError),
            (['a', 'b', 'c'], 'V1Service', AttributeError),
            ({1, 2, 3, 4}, 'V1Pod', AttributeError),

            # unknown type
            (11, 'NotARealType', ValueError),
        ]
    )
    def test_error(self, value, t, error):
        """Test casting values to the specified type unsuccessfully."""

        with pytest.raises(error):
            manifest.cast_value(value, t)


class TestNewObject:
    """Tests for kubetest.manifest.new_object"""

    # TODO - a lot of this is tested implicitly in TestLoadType. Once we have
    # test coverage set up, can add tests based on whats missing.


class TestLoadType:
    """Tests for kubetest.manifest.load_type"""

    def test_simple_deployment_ok(self, manifest_dir, simple_deployment):
        """Test loading the simple deployment successfully."""
        obj = manifest.load_type(
            client.V1Deployment,
            os.path.join(manifest_dir, 'simple-deployment.yaml')
        )
        assert obj == simple_deployment

    def test_simple_deployment_wrong_type(self, manifest_dir):
        """Test loading the simple deployment to the wrong type."""
        with pytest.raises(ValueError):
            # The V1Container requires a name -- since the manifest has no name,
            # it will cause V1Container construction to fail with ValueError.
            manifest.load_type(
                client.V1Container,
                os.path.join(manifest_dir, 'simple-deployment.yaml')
            )

    def test_simple_statefulset_ok(self, manifest_dir, simple_statefulset):
        """Test loading the simple statefulset successfully."""
        obj = manifest.load_type(
            client.V1StatefulSet,
            os.path.join(manifest_dir, 'simple-statefulset.yaml')
        )
        assert obj == simple_statefulset

    def test_simple_statefulset_wrong_type(self, manifest_dir):
        """Test loading the simple statefulset to the wrong type."""
        with pytest.raises(ValueError):
            # The V1Container requires a name -- since the manifest has no name,
            # it will cause V1Container construction to fail with ValueError.
            manifest.load_type(
                client.V1Container,
                os.path.join(manifest_dir, 'simple-statefulset.yaml')
            )

    def test_simple_daemonset_ok(self, manifest_dir, simple_daemonset):
        """Test loading the simple daemonset successfully."""
        obj = manifest.load_type(
            client.V1DaemonSet,
            os.path.join(manifest_dir, 'simple-daemonset.yaml')
        )
        assert obj == simple_daemonset

    def test_simple_daemonset_wrong_type(self, manifest_dir):
        """Test loading the simple daemonset to the wrong type."""
        with pytest.raises(ValueError):
            # The V1Container requires a name -- since the manifest has no name,
            # it will cause V1Container construction to fail with ValueError.
            manifest.load_type(
                client.V1Container,
                os.path.join(manifest_dir, 'simple-daemonset.yaml')
            )

    def test_simple_service_ok(self, manifest_dir, simple_service):
        """Test loading the simple service successfully."""
        obj = manifest.load_type(
            client.V1Service,
            os.path.join(manifest_dir, 'simple-service.yaml')
        )
        assert obj == simple_service

    def test_simple_service_wrong_type(self, manifest_dir):
        """Test loading the simple service to the wrong type."""
        with pytest.raises(ValueError):
            # The V1Container requires a name -- since the manifest has no name,
            # it will cause V1Container construction to fail with ValueError.
            manifest.load_type(
                client.V1Container,
                os.path.join(manifest_dir, 'simple-service.yaml')
            )

    def test_simple_persistentvolumeclaim_ok(
        self,
        manifest_dir,
        simple_persistentvolumeclaim
    ):
        """Test loading the simple persistentvolumeclaim successfully."""
        obj = manifest.load_type(
            client.V1PersistentVolumeClaim,
            os.path.join(manifest_dir, 'simple-persistentvolumeclaim.yaml')
        )
        assert obj == simple_persistentvolumeclaim

    def test_simple_persistentvolumeclaim_wrong_type(self, manifest_dir):
        """Test loading the simple persistentvolumeclaim to the wrong type."""
        with pytest.raises(ValueError):
            # The V1Container requires a name -- since the manifest has no name,
            # it will cause V1Container construction to fail with ValueError.
            manifest.load_type(
                client.V1Container,
                os.path.join(manifest_dir, 'simple-persistentvolumeclaim.yaml')
            )

    def test_bad_path(self, manifest_dir):
        """Test specifying an invalid manifest path."""
        with pytest.raises(FileNotFoundError):
            manifest.load_type(
                client.V1Container,
                os.path.join(manifest_dir, 'foo', 'bar', 'baz.yaml')
            )

    def test_bad_yaml(self, manifest_dir):
        """Test specifying a file that is not valid YAML."""
        with pytest.raises(yaml.YAMLError):
            manifest.load_type(
                client.V1Container,
                os.path.join(manifest_dir, 'invalid.yaml')
            )


class TestGetType:
    """Tests for kubetest.manifest.get_type"""

    @pytest.mark.parametrize(
        'data,expected', [
            (
                {'apiVersion': 'v1', 'kind': 'Secret'},
                client.V1Secret
            ),
            (
                {'apiVersion': 'v1', 'kind': 'Deployment'},
                client.V1Deployment
            ),
            (
                {'apiVersion': 'apps/v1', 'kind': 'Deployment'},
                client.V1Deployment
            ),
            (
                {'apiVersion': 'apps/v1beta1', 'kind': 'Deployment'},
                client.AppsV1beta1Deployment
            ),
            (
                {'apiVersion': 'apps/v1beta2', 'kind': 'Deployment'},
                client.V1beta2Deployment
            ),
            (
                {'apiVersion': 'extensions/v1beta1', 'kind': 'Deployment'},
                client.ExtensionsV1beta1Deployment
            ),
            (
                {
                    'apiVersion': 'rbac.authorization.k8s.io/v1',
                    'kind': 'ClusterRoleBinding'
                },
                client.V1ClusterRoleBinding
            ),
            (
                {
                    'apiVersion': 'rbac.authorization.k8s.io/v1beta1',
                    'kind': 'ClusterRoleBinding'
                },
                client.V1beta1ClusterRoleBinding
            ),
        ]
    )
    def test_ok(self, data, expected):
        """Test getting Kubernetes object types correctly."""

        actual = manifest.get_type(data)
        assert actual == expected

    def test_nonexistent_type(self):
        """Test getting a type that Kubernetes does not have."""

        t = manifest.get_type({
            'apiVersion': 'v1',
            'kind': 'foobar'
        })
        assert t is None

    def test_no_version(self):
        """Test getting a type when no version is given."""

        with pytest.raises(ValueError):
            manifest.get_type({'kind': 'Deployment'})

    def test_no_kind(self):
        """Test getting a type when no kind is given."""

        with pytest.raises(ValueError):
            manifest.get_type({'version': 'v1'})


class TestLoadPath:
    """Tests for kubetest.manifest.load_path"""

    def test_ok(self, manifest_dir):
        """Test loading the manifests into API objects successfully."""

        objs = manifest.load_path(os.path.join(manifest_dir, 'manifests'))
        assert len(objs) == 3

        for obj in objs:
            assert obj.kind in ['Deployment', 'ConfigMap', 'Service']

    def test_no_dir(self):
        """Test loading manifests when the specified path is not a directory."""

        with pytest.raises(ValueError):
            manifest.load_path('foobar')

    def test_empty_dir(self, tmpdir):
        """Test loading manifests from an empty directory."""

        d = tmpdir.mkdir('foo')
        objs = manifest.load_path(d)
        assert len(objs) == 0

    def test_invalid_yaml(self, manifest_dir):
        """Test loading manifests when one of the files has invalid YAML."""

        with pytest.raises(yaml.YAMLError):
            manifest.load_path(manifest_dir)
