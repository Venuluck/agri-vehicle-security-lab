import can
import time

from can_protocol import CAN_IDS

# Connect to virtual CAN bus
bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

speed = 20

print("Vehicle Speed ECU started...")
print("Press CTRL+C to stop.")

try:
    while True:

        # Convert speed to 2-byte big-endian value
        speed_data = speed.to_bytes(2, byteorder="big")

        # Create CAN message
        message = can.Message(
            arbitration_id=CAN_IDS["VEHICLE_SPEED"],
            data=speed_data,
            is_extended_id=False
        )

        # Send message
        bus.send(message)

        print(f"Vehicle Speed ECU -> Speed: {speed} km/h")

        # Increase speed
        speed += 5

        # Reset after 120 km/h
        if speed > 120:
            speed = 20

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nVehicle Speed ECU stopped.")

finally:
    bus.shutdown()
