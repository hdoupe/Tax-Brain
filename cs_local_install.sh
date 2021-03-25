#!/bin/bash
conda create -y -n taxbrain-cs-env pip jupyter && \
	source activate taxbrain-cs-env && \
	pip install "cs-kit>=1.16.4" pyyaml && \
	csk build-env && \
	pip install --no-deps -e . && \
	pip install --no-deps -e ./cs-config && \
	bash ./cs-config/install.sh
