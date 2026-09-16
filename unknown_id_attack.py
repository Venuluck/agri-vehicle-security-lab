import can
import time


ATTACK_CAN_ID = 0x666

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)


print("=" * 60)
print(" UNKNOWN CAN ID ATTACK SIMULATOR")
print("=" * 60)
print()
print("Attack CAN ID : 0x666")
print("Interface     : vcan0")
print()
print("Press CTRL+C to stop.")
print("=" * 60)
print()


try:

    while True:

        message = can.Message(
            arbitration_id=ATTACK_CAN_ID,
            data=[0xDE, 0xAD, 0xBE, 0xEF],
            is_extended_id=False
        )

        bus.send(message)

        print(
            f"ATTACK -> ID=0x{ATTACK_CAN_ID:03X} "
            f"DATA={message.data.hex(' ')}"
        )

        time.sleep(1)

except KeyboardInterrupt:

    print()
    print("Unknown CAN ID attack stopped.")

finally:

    bus.shutdown()
