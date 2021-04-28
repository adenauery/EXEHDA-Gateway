#!/bin/sh

. ./default_data.sh

GATEWAY=$DEFAULT_GATEWAY

echo "Gateway:    "$GATEWAY
echo "Topic:      "$DEFAULT_TOPIC
echo ''

mosquitto_pub -t "GW_031da950-3c9c-4507-8a84-ad88ae8442a3" -m "{\"type\":\"acknowledgement\"}"
mosquitto_sub -t $DEFAULT_TOPIC
