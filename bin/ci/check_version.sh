#!/usr/bin/env bash

pkg_version="${PKG_VERSION}"
circle_tag="${CIRCLE_TAG}"


if [ ! "${pkg_version}" ] && [ ! "${circle_tag}" ]; then
    echo "No version or tag specified."
    exit 1
fi

if [ "${pkg_version}" != "${circle_tag}" ]; then
    echo "Versions do not match: pkg@${pkg_version} tag@${circle_tag}"
    exit 1
fi

echo "Versions match: pkg@${pkg_version} tag@${circle_tag}"