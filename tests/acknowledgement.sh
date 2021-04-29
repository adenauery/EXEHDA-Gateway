#!/bin/bash

. ./default_data.sh

GATEWAY=$DEFAULT_GATEWAY

echo "Gateway:    "$GATEWAY
echo "Topic:      "$DEFAULT_TOPIC
echo ''

mosquitto_pub -h "$DEFAULT_BROKER_HOST" -u "$DEFAULT_BROKER_USER" -P "$DEFAULT_BROKER_PSWD" -t "GW_031da950-3c9c-4507-8a84-ad88ae8442a3" -m "{\"type\":\"acknowledgement\"}"
mosquitto_sub -h "$DEFAULT_BROKER_HOST" -u "$DEFAULT_BROKER_USER" -P "$DEFAULT_BROKER_PSWD" -t $DEFAULT_TOPIC
