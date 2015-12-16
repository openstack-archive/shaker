#!/bin/bash

for f in doc/source/images/*svg; do cairosvg ${f} -o ${f/\.svg/\.png} ; done
