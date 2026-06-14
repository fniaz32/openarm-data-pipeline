#!/usr/bin/env bash
set -e
echo "Configuring OpenArm CAN FD interfaces..."
echo "Configuring can0..."
openarm-can-cli -i can0 can_configure
echo "Configuring can1..."
openarm-can-cli -i can1 can_configure
echo "Setting zero position on can0..."
openarm-can-cli -i can0 set_zero
echo "Setting zero position on can1..."
openarm-can-cli -i can1 set_zero
echo "Done."
echo
echo "Current CAN interfaces:"
ip link show can0
ip link show can1