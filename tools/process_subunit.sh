#!/bin/bash

LOGDIR=$1

SUBUNIT_FILE="${LOGDIR}/job.subunit"
HTML_FILE="${LOGDIR}/job.html"

ls ${LOGDIR}/*.subunit | xargs cat > ${SUBUNIT_FILE}

subunit2html ${SUBUNIT_FILE} ${HTML_FILE}

cat ${SUBUNIT_FILE} | subunit-stats
