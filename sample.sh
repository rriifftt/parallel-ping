#!/bin/sh

# this is a sample script that suppose to using pacemaker
# https://github.com/ClusterLabs/pacemaker/blob/master/extra/resources/ping

ping_check() {
    pping="python ./parallel_ping.py"
    targets=$(echo " $OCF_RESKEY_host_list" | sed "s/ / --target /g")

    active=$($pping $targets \
        --timeout $OCF_RESKEY_timeout \
        --count $OCF_RESKEY_attempts\
        --output active-count)

    echo $active
}

OCF_RESKEY_host_list='192.168.1.1 192.168.1.2 192.168.1.3'
OCF_RESKEY_timeout='10'
OCF_RESKEY_attempts='3'

ping_check