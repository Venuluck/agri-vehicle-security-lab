import can
import time

from can_protocol import CAN_IDS

# Connect to virtual CAN bus
bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

brake_status = 0

print("Brake ECU started...")
print("Press CTRL+C to stop.")

try:
    while True:

        # 0 = released, 1 = applied
        brake_data = bytes([brake_status])

        message = can.Message(
            arbitration_id=CAN_IDS["BRAKE_STATUS"],
            data=brake_data,
            is_extended_id=False
        )

        bus.send(message)

        if brake_status == 0:
            print("Brake ECU -> RELEASED")
        else:
            print("Brake ECU -> APPLIED")

        # Change brake state
        brake_status = 1 - brake_status

        time.sleep(2)

except KeyboardInterrupt:
    print("\nBrake ECU stopped.")

finally:
    bus.shutdown()
