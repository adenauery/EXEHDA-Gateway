#!/bin/bash

. ./random_hash.sh
. ./default_data.sh

GATEWAY=$DEFAULT_GATEWAY
DEVICE=$DEFAULT_DEVICE
IDENTIFIER=$(random_hash)

echo "Gateway:    "$GATEWAY
echo "Device:     "$DEVICE
echo "Identifier: "$IDENTIFIER
echo "Topic:      "$DEFAULT_TOPIC
echo ''

mosquitto_pub -h "$DEFAULT_BROKER_HOST" -u "$DEFAULT_BROKER_USER" -P "$DEFAULT_BROKER_PSWD" -t "$GATEWAY" -m "{\"type\":\"operation\", \"uuid\": \"$DEVICE\", \"identifier\": \"$IDENTIFIER\", \"write\": 1}"
mosquitto_sub -h "$DEFAULT_BROKER_HOST" -u "$DEFAULT_BROKER_USER" -P "$DEFAULT_BROKER_PSWD" -t $DEFAULT_TOPIC
