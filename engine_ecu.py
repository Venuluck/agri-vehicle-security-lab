import can
import time

from can_protocol import CAN_IDS


# ============================================================
# ENGINE ECU SIMULATOR
# ============================================================

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)


# Starting engine RPM
rpm = 1000

# Rolling CAN counter
counter = 0

# RPM direction
# 1  = increasing
# -1 = decreasing
direction = 1

# How much RPM changes per message
RPM_STEP = 100


print("=" * 50)
print(" SECURE ENGINE ECU SIMULATOR")
print("=" * 50)
print("CAN ID : 0x100")
print("RPM range : 1000 - 3000")
print("Press CTRL+C to stop.")
print()


try:

    while True:

        # ----------------------------------------------------
        # Build CAN payload
        # ----------------------------------------------------
        #
        # Bytes 0-1 = RPM
        # Byte 2    = rolling counter
        #

        rpm_data = rpm.to_bytes(
            2,
            byteorder="big"
        )

        counter_data = bytes([counter])

        message = can.Message(
            arbitration_id=CAN_IDS["ENGINE_RPM"],
            data=rpm_data + counter_data,
            is_extended_id=False
        )


        # ----------------------------------------------------
        # Send CAN message
        # ----------------------------------------------------

        bus.send(message)


        print(
            f"Engine ECU -> "
            f"RPM: {rpm} | "
            f"Counter: {counter}"
        )


        # ----------------------------------------------------
        # Update rolling counter
        # ----------------------------------------------------

        counter = (counter + 1) % 256


        # ----------------------------------------------------
        # Smooth RPM movement
        # ----------------------------------------------------

        rpm += RPM_STEP * direction


        # Reverse direction at limits
        if rpm >= 3000:

            rpm = 3000
            direction = -1

        elif rpm <= 1000:

            rpm = 1000
            direction = 1


        # Send every 0.5 seconds
        time.sleep(0.5)


except KeyboardInterrupt:

    print("\nEngine ECU stopped.")


finally:

    bus.shutdown()
