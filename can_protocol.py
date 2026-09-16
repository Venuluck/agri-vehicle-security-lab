# CAN protocol definition for our agricultural vehicle simulation

CAN_IDS = {
    "ENGINE_RPM": 0x100,
    "VEHICLE_SPEED": 0x200,
    "BRAKE_STATUS": 0x300,
    "GPS_STATUS": 0x400,
}

# Maximum realistic values for our simulation
LIMITS = {
    "ENGINE_RPM": 3000,
    "VEHICLE_SPEED": 120,
}
