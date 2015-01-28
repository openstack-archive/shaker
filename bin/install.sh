#!/bin/bash -xe

TOP_DIR=$(cd $(dirname "$0") && pwd)
source ${TOP_DIR}/functions.sh

IMAGE_NAME="shaker-image"
UBUNTU_CLOUD_IMAGE_URL="https://cloud-images.ubuntu.com/releases/14.04.1/release/ubuntu-14.04-server-cloudimg-amd64-disk1.img"

setup_image() {
    message "Installing Shaker image, will take some time"

    message "Downloading Ubuntu cloud image"
    IMG_FILE="ubuntu-cloud.img"
    wget -O ${IMG_FILE} ${UBUNTU_CLOUD_IMAGE_URL}
    glance image-create --name ${IMG_FILE} --disk-format qcow2 --container-format bare --is-public True --file ${IMG_FILE}

    message "Creating security group"
    SEC_GROUP="shaker-access"
    nova secgroup-create ${SEC_GROUP} "Security Group for Shaker"
    nova secgroup-add-rule ${SEC_GROUP} icmp -1 -1 0.0.0.0/0
    nova secgroup-add-rule ${SEC_GROUP} tcp 1 65535 0.0.0.0/0
    nova secgroup-add-rule ${SEC_GROUP} udp 1 65535 0.0.0.0/0

    message "Creating flavor"
    nova flavor-create --is-public true m1.mini 6 1024 10 1

    message "Creating key pair"
    KEY="shaker-key"
    nova keypair-add ${KEY} > ${KEY}.pem
    chmod og-rw ${KEY}.pem

    message "Booting VM"
    NETWORK_ID=`neutron net-show net04 -f value -c id`
    VM="shaker-template"
    nova boot --poll --flavor m1.mini --image ${IMG_FILE} --key_name ${KEY} --nic net-id=${NETWORK_ID} --security-groups ${SEC_GROUP} ${VM}

    message "Associating a floating IP with VM"
    FLOATING_IP=`neutron floatingip-create -f value -c floating_ip_address net04_ext | tail -1`
    FLOATING_IP="172.18.161.251"
    nova floating-ip-associate ${VM} ${FLOATING_IP}

    message "Installing packages into VM"
    ssh -i ${KEY}.pem ubuntu@${FLOATING_IP} "sudo apt-add-repository \"deb http://nova.clouds.archive.ubuntu.com/ubuntu/ trusty multiverse\""
    ssh -i ${KEY}.pem ubuntu@${FLOATING_IP} "sudo apt-get update"
    ssh -i ${KEY}.pem ubuntu@${FLOATING_IP} "sudo apt-get -y install iperf netperf python-pip"
    ssh -i ${KEY}.pem ubuntu@${FLOATING_IP} "sudo pip install netperf-wrapper"

    message "Making VM snapshot"
    nova image-create --poll ${VM} ${IMAGE_NAME}
}

main() {
    CHECK_IMAGE="`glance image-show ${IMAGE_NAME} || true`"
    echo "-- ${CHECK_IMAGE} --"
    if [ "${CHECK_IMAGE}" == "" ]; then
        setup_image
    fi
}

main "$@"
