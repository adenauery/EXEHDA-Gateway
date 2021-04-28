#!/bin/sh

. ./random_hash.sh
. ./default_data.sh

GATEWAY=$DEFAULT_GATEWAY
DEVICE=$DEFAULT_DEVICE
IDENTIFIER=$(random_hash)
TIMESTAMP=$(date -d "+2 minutes" +%s)

echo "Gateway:    "$GATEWAY
echo "Device:     "$DEVICE
echo "Identifier: "$IDENTIFIER
echo "Topic:      "$DEFAULT_TOPIC
echo "Timestamp:  "$TIMESTAMP
echo ''

mosquitto_pub -t "$GATEWAY" -m "{\"type\":\"scheduling\", \"schedules\": [{\"type\":\"create\", \"identifier\": \"$IDENTIFIER\", \"uuid\": \"$DEVICE\", \"timestamp\": $TIMESTAMP, \"write\": 1}]}"
mosquitto_sub -t $DEFAULT_TOPIC
