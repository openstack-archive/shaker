#!/bin/bash -xe

find doc/source/ -name *svg | sed "s/\.svg$//" | xargs -I% cairosvg "%.svg" -o "%.png"
