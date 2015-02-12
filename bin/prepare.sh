#!/bin/bash -xe

TOP_DIR=$(cd $(dirname "$0") && pwd)
source ${TOP_DIR}/functions.sh

NETWORK_NAME=${NETWORK_NAME:-net04}
CLOUD_IMAGE_NAME="shaker-cloud-image"
IMAGE_NAME="shaker-image"
FLAVOR_NAME="shaker-flavor"

UBUNTU_CLOUD_IMAGE_URL="https://cloud-images.ubuntu.com/releases/14.04.1/release/ubuntu-14.04-server-cloudimg-amd64-disk1.img"

setup_image() {
    message "Installing Shaker image, will take some time"

    if [ -z "$(glance image-show ${CLOUD_IMAGE_NAME})" ]; then
        message "Downloading Ubuntu cloud image"
        glance image-create --name ${CLOUD_IMAGE_NAME} --disk-format qcow2 --container-format bare --is-public True --copy-from ${UBUNTU_CLOUD_IMAGE_URL}

        until [ -n "$(glance image-show ${CLOUD_IMAGE_NAME} | grep status | grep active)" ]; do
            sleep 5
        done
    fi

    UUID=$(cat /proc/sys/kernel/random/uuid)

    message "Creating security group"
    SEC_GROUP="shaker-access-${UUID}"
    nova secgroup-create ${SEC_GROUP} "Security Group for Shaker"
    nova secgroup-add-rule ${SEC_GROUP} icmp -1 -1 0.0.0.0/0
    nova secgroup-add-rule ${SEC_GROUP} tcp 1 65535 0.0.0.0/0
    nova secgroup-add-rule ${SEC_GROUP} udp 1 65535 0.0.0.0/0

    message "Creating flavor"
    if [ -n "$(nova flavor-list | grep ${FLAVOR_NAME})" ]; then
        nova flavor-delete ${FLAVOR_NAME}
    fi
    nova flavor-create --is-public true ${FLAVOR_NAME} auto 1024 3 1

    message "Creating key pair"
    KEY_NAME="shaker-key-${UUID}"
    KEY="`mktemp`"
    nova keypair-add ${KEY_NAME} > ${KEY}
    chmod og-rw ${KEY}

    message "Booting VM"
    NETWORK_ID=`neutron net-show ${NETWORK_NAME} -f value -c id`
    VM="shaker-template-${UUID}"
    nova boot --poll --flavor ${FLAVOR_NAME} --image ${CLOUD_IMAGE_NAME} --key_name ${KEY_NAME} --nic net-id=${NETWORK_ID} --security-groups ${SEC_GROUP} ${VM}

    message "Associating a floating IP with VM"
    FLOATING_IP=`neutron floatingip-create -f value -c floating_ip_address net04_ext | tail -1`
    nova floating-ip-associate ${VM} ${FLOATING_IP}

    message "Waiting for VM to boot up"
    until remote_shell ${FLOATING_IP} ${KEY} "echo"; do
        sleep 10
    done

    message "Installing packages into VM"
    remote_shell ${FLOATING_IP} ${KEY} "sudo apt-add-repository \"deb http://nova.clouds.archive.ubuntu.com/ubuntu/ trusty multiverse\""
    remote_shell ${FLOATING_IP} ${KEY} "sudo apt-get update"
    remote_shell ${FLOATING_IP} ${KEY} "sudo apt-get -y install iperf netperf git python-dev libzmq-dev screen"
    remote_shell ${FLOATING_IP} ${KEY} "wget -O get-pip.py https://bootstrap.pypa.io/get-pip.py && sudo python get-pip.py"
    remote_shell ${FLOATING_IP} ${KEY} "sudo pip install pbr netperf-wrapper"
    remote_shell ${FLOATING_IP} ${KEY} "git clone git://github.com/Mirantis/shaker && cd shaker && sudo pip install -r requirements.txt && sudo python setup.py develop"
    remote_shell ${FLOATING_IP} ${KEY} "sudo shutdown -P -f now"
    sleep 10

    message "Making VM snapshot"
    nova image-create --poll ${VM} ${IMAGE_NAME}
    glance image-update --is-public True ${IMAGE_NAME}

    message "Destroy VM"
    nova delete ${VM}

    message "Waiting for VM to die"
    until [ -z "$(nova list | grep ${VM})" ]; do
        sleep 5
    done

    message "Cleaning up resources"
    FP_ID=`neutron floatingip-list -f csv -c id -c floating_ip_address --quote none | grep ${FLOATING_IP} | awk -F "," '{print $1}'`
    neutron floatingip-delete ${FP_ID}

    nova secgroup-delete ${SEC_GROUP}
    nova keypair-delete ${KEY_NAME}
}

main() {
    if [ -z "$(glance image-show ${IMAGE_NAME})" ]; then
        setup_image
    else
        message "Image ${IMAGE_NAME} already exists."
    fi
}

main "$@"
