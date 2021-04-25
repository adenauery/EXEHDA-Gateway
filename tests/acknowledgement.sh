#!/bin/sh

GATEWAY=GW_031da950-3c9c-4507-8a84-ad88ae8442a3

echo "Gateway:    "$GATEWAY
echo ''

mosquitto_pub -t "GW_031da950-3c9c-4507-8a84-ad88ae8442a3" -m "{\"type\":\"acknowledgement\"}"
mosquitto_sub -t i2wac
