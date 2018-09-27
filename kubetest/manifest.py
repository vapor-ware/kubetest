"""Utility functions for loading Kubernetes manifest files and constructing
the corresponding Kubernetes API models.
"""

import builtins
import os
import re

import kubernetes
import yaml
from kubernetes.client import models


def load_file(path, obj_type=None):
    """Load an individual Kubernetes manifest YAML file.

    Args:
        path (str): The fully qualified path to the file.
        obj_type: The type of the object to load. If not specified,
            this will attempt to auto-detect the type.

    Returns:
        The Kubernetes API object for the manifest file.
    """
    with open(path, 'r') as f:
        manifest = yaml.load(f)

    if obj_type is None:
        obj_type = get_type(manifest)
        if obj_type is None:
            raise ValueError(
                'Unable to determine object type for manifest: {}'.format(manifest)
            )

    return new_object(obj_type, manifest)


def load_path(path):
    """Load all of the Kubernetes YAML manifest files found in the
    specified directory path.

    Args:
        path (str): The path to the directory of manifest files.

    Returns:
        list: A list of all the Kubernetes objects loaded from
            manifest file.

    Raises:
        ValueError: The provided path is not a directory.
    """
    if not os.path.isdir(path):
        raise ValueError('{} is not a directory'.format(path))

    objs = []
    for f in os.listdir(path):
        if os.path.splitext(f)[1].lower() in ['.yaml', '.yml']:
            obj = load_file(os.path.join(path, f))
            objs.append(obj)
    return objs


def get_type(manifest):
    """Get the Kubernetes object type from the manifest kind and
    version.

    There is no easy way for determining the internal model that a
    manifest should use. What this tries to do is use the version
    info and the kind info to create a potential internal object
    name for the pair and look that up in the kubernetes package
    locals.

    Args:
        manifest (dict): The manifest file, loaded into a dictionary.

    Returns:
        object: The Kubernetes API object for the manifest.
        None: No Kubernetes API object type could be determined.

    Raises:
        ValueError: The manifest dictionary does not have a
            `version` or `kind` specified.
    """
    version = manifest.get('apiVersion')
    if version is None:
        raise ValueError('manifest has no "version" field specified')

    kind = manifest.get('kind')
    if kind is None:
        raise ValueError('manifest has no "kind" field specified')

    # create a map of the kubernetes client model locals where the key is the
    # lower cased name (so we don't have to mess with getting the capitalization
    # of components correct) and the value is the correctly cased name.
    lookup = {k.lower(): k for k in models.__dict__.keys()}

    # if the version has a '/' (e.g. apps/v1, extensions/v1beta1), remove it.

    # there are generally two possibilities - we include the version minus
    # the slash (e.g. extensions/v1beta1 -> extensionsv1beta1), or we do not
    # use the prefix (e.g. apps/v1 -> v1). By default we will always try with
    # the prefix first and only try the secondary check if the first check
    # yields nothing.
    possibilities = [
        # add the default case
        version.replace('/', '').replace('.', '') + kind
    ]

    # if the prefix exists, add the non-prefixed version as a secondary check
    if version.count('/') == 1:
        possibilities.append(version.split('/')[1] + kind)

    for to_check in possibilities:
        type_name = lookup.get(to_check.lower())
        if type_name is None:
            continue
        return models.__dict__.get(type_name)
    return None


def load_type(obj_type, path):
    """Load a Kubernetes YAML manifest file for the specified type.

    While Kubernetes manifests can contain multiple object definitions
    in a single file (delimited with the YAML separator '---'), this
    does not currently support those files. This function expects a
    single object definition in the specified manifest file.

    Args:
        path (str): The path the manifest YAML to load.
        obj_type: The Kubernetes API object type that the YAML
            contents should be loaded into.

    Returns:
        A Kubernetes API object populated with the YAML contents.

    Raises:
        FileNotFoundError: The specified file was not found.
    """
    with open(path, 'r') as f:
        manifest = yaml.load(f)

    return new_object(obj_type, manifest)


def new_object(root_type, config):
    """Create a new Kubernetes API object and recursively populate it with
    the provided manifest configuration.

    The recursive population utilizes the swagger_types and attribute_map
    members of the Kubernetes API object class to determine which config
    fields correspond to which input parameter, and to cast them to their
    expected type.

    This is all based on the premise that the Python Kubernetes client will
    continue to be based off of an auto-generated Swagger spec and that these
    fields will be available for all API objects.

    Args:
        root_type: The Kubernetes API object type that will be populated
            with the manifest configuration. This is expected to be known
            ahead of time by the caller.
        config: The manifest configuration for the API object.

    Returns:
        A Kubernetes API object recursively populated with the YAML contents.
    """

    # The arguments that will be passed to the root_type to create a new
    # recursively populated instance of that type.
    constructor_args = {}

    # The attribute map maps the argument name (e.g. api_version) to the name
    # of the corresponding configuration field (e.g. apiVersion). Iterate over
    # each of these to pick up all the possible configuration options from the
    # provided manifest.
    for k, v in root_type.attribute_map.items():
        cfg_value = config.get(v)
        if cfg_value is not None:

            # The config value matches an expected key in the attribute dict.
            # Now, we want to cast that config to the appropriate type based
            # on the contents of the 'swagger_types' dict.
            t = root_type.swagger_types[k]

            # There are two classes of types we will want to check against:
            # 'base types' (like: str, int, etc) and 'collection types'
            # (like: list, dict). Collection types can contain base types,
            # so we will want to apply the same base type checks to each
            # element within a collection type. First we will check for the
            # collection types. If it is neither, we assume that the type is
            # a base type.

            # Check if the type is a list of some other type.
            # This should match to something like: 'list[str]', where the
            # element type (in this case 'str') will be isolated as a group.
            list_match = re.match(r'^list\[(.*)\]$', t)
            if list_match is not None:
                element_type = list_match.group(1)
                list_value = [cast_value(i, element_type) for i in cfg_value]
                constructor_args[k] = list_value
                continue

            # Check if the type is a dict composed of other types.
            # This should match to something lint: 'dict(str, str)', where
            # the element types (in this case, both 'str') will be isolated
            # as separate groups.
            dict_match = re.match(r'^dict\((.*), (.*)\)$', t)
            if dict_match is not None:
                key_type = dict_match.group(1)
                val_type = dict_match.group(2)
                dict_value = {
                    cast_value(k, key_type): cast_value(v, val_type)
                    for k, v in cfg_value.items()
                }
                constructor_args[k] = dict_value
                continue

            # If it is not a collection type, it must be a base type.
            constructor_args[k] = cast_value(cfg_value, t)

    return root_type(**constructor_args)


def cast_value(value, t):
    """Cast the given value to the specified type.

    There are two general cases for possible casts:
      - A cast to a builtin type (int, str, etc.)
      - A cast to a Kubernetes object (V1ObjectMeta, etc)

    In either case, check to see if the specified type exists in the
    correct type pool. If so, cast to that type, otherwise fail.

    Args:
        value: The value to cast.
        t (str): The type to cast the value to. This can be a builtin
            type or a Kubernetes API object type.

    Returns:
        The value, casted to the appropriate type.

    Raises:
        ValueError: Unable to cast the value to the specified type.
        TypeError: Unable to cast the given value to the specified type.
        AttributeError: The value is an invalid Kubernetes type.
    """

    # The config value should be cast to a built-in type
    builtin_type = builtins.__dict__.get(t)
    if builtin_type == object:
        return value
    if builtin_type is not None:
        return builtin_type(value)

    # The config value should be cast to a Kubernetes type
    k_type = kubernetes.client.__dict__.get(t)
    if k_type is not None:
        return new_object(k_type, value)

    raise ValueError('Unable to determine cast type behavior: {}'.format(t))
