#!/bin/sh

. ./random_hash.sh

GATEWAY=GW_031da950-3c9c-4507-8a84-ad88ae8442a3
DEVICE=eec4484e-3b56-4c9e-8c94-26b8c5dce72b
IDENTIFIER=$(random_hash)

echo "Gateway:    "$GATEWAY
echo "Device:     "$DEVICE
echo "Identifier: "$IDENTIFIER
echo ''

mosquitto_pub -t "$GATEWAY" -m "{\"type\":\"operation\", \"uuid\": \"$DEVICE\", \"identifier\": \"$IDENTIFIER\"}"
mosquitto_sub -t i2wac
