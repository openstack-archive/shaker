#!/bin/bash

# this file location is taken from Zuul
SUBUNIT_FILE="./testrepository.subunit"

ls $1/*.subunit | xargs cat > ${SUBUNIT_FILE}
cat ${SUBUNIT_FILE} | subunit-stats
