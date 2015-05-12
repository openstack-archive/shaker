#!/bin/bash

TEMP_DIR="$(mktemp -d)"
cp -r shaker ${TEMP_DIR}/
cp -r .git ${TEMP_DIR}/
cp requirements-agent.txt ${TEMP_DIR}/requirements.txt
cp setup-agent.cfg ${TEMP_DIR}/setup.cfg
cp setup.py ${TEMP_DIR}/
cp README.rst ${TEMP_DIR}/
cp LICENSE ${TEMP_DIR}/

export PBR_VERSION="$(git describe --exact-match)"

cd ${TEMP_DIR}
echo "Building pyshaker-agent version ${PBR_VERSION}"
python setup.py sdist
twine upload -s dist/*

cd -
rm -rf ${TEMP_DIR}
