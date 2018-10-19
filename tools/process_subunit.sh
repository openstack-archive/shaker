#!/bin/bash

ls $1/*.subunit | xargs cat | subunit-stats