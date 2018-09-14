#
# kubetest
#

PKG_NAME    := kubetest
PKG_VERSION := $(shell python -c "import kubetest ; print(kubetest.__version__)")

HAS_PIP_COMPILE := $(shell which pip-compile)


.PHONY: clean
clean:  ## Clean up build artifacts
	rm -rf build/ dist/ *.egg-info htmlcov/ .coverage* .pytest_cache/ \
		kubetest/__pycache__ tests/__pycache__

.PHONY: deps
deps:  ## Update the frozen pip dependencies (requirements.txt)
ifndef HAS_PIP_COMPILE
	pip install pip-tools
endif
	pip-compile --output-file requirements.txt setup.py

.PHONY: example-tests
example-tests:  ## Run the example tests using kubetest
	tox -e examples

.PHONY: fmt
fmt:  ## Run formatting checks on the project source code
	tox -e format

.PHONY: test
test:  ## Run the project unit tests
	tox

.PHONY: version
version:  ## Print the version of the project
	@echo "$(PKG_VERSION)"

.PHONY: help
help:  ## Print Make usage information
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

.DEFAULT_GOAL := help
