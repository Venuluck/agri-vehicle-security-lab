import can
import time

from can_protocol import CAN_IDS

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

rpm = 1000
counter = 0

print("Secure Engine ECU started...")
print("Press CTRL+C to stop.")

try:
    while True:

        # RPM = 2 bytes + rolling counter = 1 byte
        rpm_data = rpm.to_bytes(2, byteorder="big")
        counter_data = bytes([counter])

        message = can.Message(
            arbitration_id=CAN_IDS["ENGINE_RPM"],
            data=rpm_data + counter_data,
            is_extended_id=False
        )

        bus.send(message)

        print(
            f"Engine ECU -> RPM: {rpm} | "
            f"Counter: {counter}"
        )

        counter = (counter + 1) % 256

        rpm += 100

        if rpm > 3000:
            rpm = 1000

        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nEngine ECU stopped.")

finally:
    bus.shutdown()
