"""Unit tests for the kubetest.objects.api_object module."""

import os

import pytest

from kubetest.objects import ConfigMap, Deployment, Service


class TestApiObject:

    def test_load_obj_from_manifest_one_definition(self, manifest_dir):
        """Load an object from a manifest file which only defines the definition
        for the object.
        """

        obj = Deployment.load(
            os.path.join(manifest_dir, 'simple-deployment.yaml'),
        )

        assert isinstance(obj, Deployment)
        assert obj.name == 'nginx-deployment'

    def test_load_obj_from_manifest_many_definitions(self, manifest_dir):
        """Load an object from a manifest file which defines multiple objects.

        In this case, the manifest only contains a single object definition for
        the type that we are trying to load.
        """

        obj = Deployment.load(
            os.path.join(manifest_dir, 'multi-obj-manifest.yaml'),
        )

        assert isinstance(obj, Deployment)
        assert obj.name == 'kubetest-test-app'

    def test_load_obj_from_manifest_many_definitions_no_identifier(self, manifest_dir):
        """Load an object from a manifest file which defines multiple objects.

        In this case, the manifest contains multiple object definitions for
        the type that we are trying to load and no identifier is passed to the
        load function.
        """

        with pytest.raises(ValueError):
            Service.load(
                os.path.join(manifest_dir, 'multi-obj-manifest.yaml'),
            )

    def test_load_obj_from_manifest_many_definitions_with_identifier(self, manifest_dir):
        """Load an object from a manifest file which defines multiple objects.

        In this case, the manifest contains multiple object definitions for
        the type that we are trying to load and a valid identifier is passed to the
        load function.
        """

        obj = Service.load(
            os.path.join(manifest_dir, 'multi-obj-manifest.yaml'),
            name='service-b',
        )

        assert isinstance(obj, Service)
        assert obj.name == 'service-b'

    def test_load_obj_from_manifest_many_definitions_no_match(self, manifest_dir):
        """Load an object from a manifest file which defines multiple objects.

        In this case, the manifest contains multiple objects, all of which do not match
        the type of object we are trying to load.
        """

        with pytest.raises(ValueError):
            ConfigMap.load(
                os.path.join(manifest_dir, 'multi-obj-manifest.yaml'),
            )

    def test_load_obj_from_manifest_many_definitions_name_no_match(self, manifest_dir):
        """Load an object from a manifest file which defines multiple objects.

        In this case, the manifest contains multiple object definitions for
        the type that we are trying to load and an identifier which does not match
        any of the objects is passed to the load function.
        """

        with pytest.raises(ValueError):
            Service.load(
                os.path.join(manifest_dir, 'multi-obj-manifest.yaml'),
                name='service-c'
            )
