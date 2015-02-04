#!/bin/bash

error() {
    printf "\e[31mError: %s\e[0m\n" "${*}" >&2
    exit 1
}

message() {
    printf "\e[33m%s\e[0m\n" "${1}"
}

remote_shell() {
    host=$1
    key=$2
    command=$3
    ssh -i ${key} -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o ConnectTimeout=10 ubuntu@${host} "$command"
}
