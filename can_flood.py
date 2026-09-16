import can
import time

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

print("CAN flood simulation started.")
print("Target: local vcan0")
print("Press CTRL+C to stop.")

try:

    while True:

        message = can.Message(
            arbitration_id=0x100,
            data=bytes([0x03, 0xE8]),
            is_extended_id=False
        )

        bus.send(message)

        time.sleep(0.001)

except KeyboardInterrupt:

    print("\nFlood simulation stopped.")

finally:

    bus.shutdown()
