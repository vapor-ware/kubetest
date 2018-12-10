#!/usr/bin/env bash

#
# generate_changelog.sh
#
# Automatically generate a changelog for a release that highlights the
# issues, PRs, etc. since the last release.
#
# $GITHUB_USER, $GITHUB_REPONAME, and $GITHUB_TOKEN are environment variables
# defined in the CI build environment.
#

# TODO: instead of using a docker image to do all of this, see about
# just installing the tooling directly onto the CI build servers. That
# will simplify some of this, in particular the file juggling.


prev_tag=$(git describe --abbrev=0 --tags `git rev-list --tags --skip=1 --max-count=1` || true)
since_flag=$(if [[ "${prev_tag}" ]]; then echo "--since-tag ${prev_tag}"; fi)

docker pull timfallmk/github-changelog-generator
docker run --name changelog timfallmk/github-changelog-generator \
  -u ${GITHUB_USER} \
  -p ${GITHUB_REPONAME} \
  -t ${GITHUB_TOKEN} \
  ${since_flag}
docker cp changelog:/usr/local/src/your-app/CHANGELOG.md ./
docker rm changelog