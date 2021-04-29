#!/bin/bash

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

if [[ $1 == "--create" ]]
then

	mosquitto_pub -h "$DEFAULT_BROKER_HOST" -u "$DEFAULT_BROKER_USER" -P "$DEFAULT_BROKER_PSWD" -t "$GATEWAY" -m "{\"type\":\"scheduling\", \"schedules\": [{\"type\":\"create\", \"identifier\": \"$IDENTIFIER\", \"uuid\": \"$DEVICE\", \"timestamp\": $TIMESTAMP, \"write\": 1}]}"
elif [[ $1 == "--read" ]]
then
	mosquitto_pub -h "$DEFAULT_BROKER_HOST" -u "$DEFAULT_BROKER_USER" -P "$DEFAULT_BROKER_PSWD" -t "$GATEWAY" -m "{\"type\":\"scheduling\", \"schedules\": [{\"type\":\"read\", \"identifier\": \"$IDENTIFIER\"]}"
elif [[ $1 == "--update" ]]
then
	mosquitto_pub -h "$DEFAULT_BROKER_HOST" -u "$DEFAULT_BROKER_USER" -P "$DEFAULT_BROKER_PSWD" -t "$GATEWAY" -m "{\"type\":\"scheduling\", \"schedules\": [{\"type\":\"update\", \"identifier\": \"$2\", \"data\": {\"write\": 0}]}"
elif [[ $1 == "--delete" ]]
then
	mosquitto_pub -h "$DEFAULT_BROKER_HOST" -u "$DEFAULT_BROKER_USER" -P "$DEFAULT_BROKER_PSWD" -t "$GATEWAY" -m "{\"type\":\"scheduling\", \"schedules\": [{\"type\":\"delete\", \"identifier\": \"$2\"]}"
fi

mosquitto_sub -h "$DEFAULT_BROKER_HOST" -u "$DEFAULT_BROKER_USER" -P "$DEFAULT_BROKER_PSWD" -t $DEFAULT_TOPIC
