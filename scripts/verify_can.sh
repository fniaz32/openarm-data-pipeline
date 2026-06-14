#!/usr/bin/env bash
set -e
# quick sanity check after setup
echo "Checking CAN interfaces..."
ip link show can0
ip link show can1
echo
# confirms bus is up and device is responsive
echo "Discovering motors on can0..."
openarm-can-cli -i can0 discover || true
echo
echo "Discovering motors on can1..."
openarm-can-cli -i can1 discover || true
echo
# confirms live CAN messages are coming
echo "Monitoring can0 briefly..."
openarm-can-cli -i can0 monitor -d 3000 -t 100 || true
echo
echo "Monitoring can1 briefly..."
openarm-can-cli -i can1 monitor -d 3000 -t 100 || true
