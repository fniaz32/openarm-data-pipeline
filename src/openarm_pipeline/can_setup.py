# central place for CAN interface
CAN_INTERFACES = ["can0", "can1"]

# shown through API/dashboard so present even though no hardware
def setup_commands() -> list[str]:
    commands = []
    for interface in CAN_INTERFACES:
        commands.append(f"openarm-can-cli -i {interface} can_configure")
        commands.append(f"openarm-can-cli -i {interface} set_zero")
        commands.append(f"ip link show {interface}")
    return commands