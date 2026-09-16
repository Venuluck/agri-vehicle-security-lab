import can
import time

from can_protocol import CAN_IDS


# ============================================================
# CAN MONITOR / INTRUSION DETECTION SYSTEM
# ============================================================

INTERFACE = "socketcan"
CHANNEL = "vcan0"

# Maximum expected messages per second for one CAN ID
RATE_LIMIT = 10

# Maximum legitimate RPM change between two consecutive
# Engine ECU messages
MAX_RPM_CHANGE = 500


# ============================================================
# CAN MESSAGE DEFINITIONS
# ============================================================

EXPECTED_LENGTH = {
    CAN_IDS["ENGINE_RPM"]: 3,       # 2 bytes RPM + 1 byte counter
    CAN_IDS["VEHICLE_SPEED"]: 2,    # 2 bytes speed
    CAN_IDS["BRAKE_STATUS"]: 1,     # 1 byte status
    CAN_IDS["GPS_STATUS"]: 1,       # 1 byte status
}


ID_TO_SIGNAL = {
    CAN_IDS["ENGINE_RPM"]: "ENGINE_RPM",
    CAN_IDS["VEHICLE_SPEED"]: "VEHICLE_SPEED",
    CAN_IDS["BRAKE_STATUS"]: "BRAKE_STATUS",
    CAN_IDS["GPS_STATUS"]: "GPS_STATUS",
}


# ============================================================
# MONITOR STATE
# ============================================================

# Number of messages received for each CAN ID
message_counts = {}

# Last rolling counter received for each CAN ID
last_counters = {}

# Last known RPM received from each Engine CAN ID
last_rpm = {}

# Start of the current rate-monitoring window
window_start = time.time()


# ============================================================
# CAN PAYLOAD DECODER
# ============================================================

def decode_value(can_id, data):
    """
    Decode CAN payload according to the project protocol.
    """

    # --------------------------------------------------------
    # Engine RPM
    # --------------------------------------------------------

    if can_id == CAN_IDS["ENGINE_RPM"]:

        rpm = int.from_bytes(
            data[0:2],
            byteorder="big"
        )

        counter = data[2]

        return rpm, counter


    # --------------------------------------------------------
    # Vehicle Speed
    # --------------------------------------------------------

    elif can_id == CAN_IDS["VEHICLE_SPEED"]:

        speed = int.from_bytes(
            data[0:2],
            byteorder="big"
        )

        return speed


    # --------------------------------------------------------
    # Brake Status
    # --------------------------------------------------------

    elif can_id == CAN_IDS["BRAKE_STATUS"]:

        return data[0]


    # --------------------------------------------------------
    # GPS Status
    # --------------------------------------------------------

    elif can_id == CAN_IDS["GPS_STATUS"]:

        return data[0]


    return None


# ============================================================
# RATE MONITOR RESET
# ============================================================

def reset_rate_window():
    """
    Reset message counters after each monitoring window.
    """

    global message_counts
    global window_start

    message_counts = {}

    window_start = time.time()


# ============================================================
# FRAME ANALYSIS
# ============================================================

def analyze_frame(message):
    """
    Analyze one CAN frame for suspicious activity.
    """

    can_id = message.arbitration_id

    data = message.data


    # ========================================================
    # 1. CAN RATE / FLOODING DETECTION
    # ========================================================

    message_counts[can_id] = (
        message_counts.get(can_id, 0) + 1
    )

    elapsed = time.time() - window_start

    if elapsed >= 1.0:

        for monitored_id, count in message_counts.items():

            rate = count / elapsed

            if rate > RATE_LIMIT:

                print(
                    f"[ALERT] CAN flooding suspected | "
                    f"ID=0x{monitored_id:03X} | "
                    f"Rate={rate:.0f} msg/s"
                )

        reset_rate_window()


    # ========================================================
    # 2. UNKNOWN CAN ID
    # ========================================================

    if can_id not in ID_TO_SIGNAL:

        print(
            f"[ALERT] Unknown CAN ID | "
            f"ID=0x{can_id:03X}"
        )

        return


    signal_name = ID_TO_SIGNAL[can_id]


    # ========================================================
    # 3. DATA LENGTH VALIDATION
    # ========================================================

    expected_length = EXPECTED_LENGTH[can_id]

    if len(data) != expected_length:

        print(
            f"[ALERT] Invalid data length | "
            f"ID=0x{can_id:03X} | "
            f"Expected={expected_length} | "
            f"Received={len(data)}"
        )

        return


    # ========================================================
    # 4. DECODE MESSAGE
    # ========================================================

    decoded = decode_value(
        can_id,
        data
    )


    # ========================================================
    # ENGINE RPM
    # ========================================================

    if can_id == CAN_IDS["ENGINE_RPM"]:

        rpm, counter = decoded


        # ----------------------------------------------------
        # 4A. REPLAY / COUNTER VALIDATION
        # ----------------------------------------------------

        if can_id in last_counters:

            last_counter = last_counters[can_id]

            # Difference calculated modulo 256.
            #
            # This correctly handles:
            #
            # 254 -> 255
            # 255 -> 0
            # 0   -> 1

            counter_difference = (
                counter - last_counter
            ) % 256


            # Same counter received again
            #
            # Example:
            #
            # 10 -> 10

            if counter_difference == 0:

                print(
                    f"[ALERT] Possible replay attack | "
                    f"ID=0x{can_id:03X} | "
                    f"Counter={counter} | "
                    f"Last Counter={last_counter}"
                )

                return


            # Large backwards jump
            #
            # Example:
            #
            # 100 -> 50
            #
            # This can indicate an old/stale frame.

            if counter_difference > 128:

                print(
                    f"[ALERT] Stale/out-of-order counter | "
                    f"ID=0x{can_id:03X} | "
                    f"Counter={counter} | "
                    f"Last Counter={last_counter}"
                )

                return


        # Save latest counter

        last_counters[can_id] = counter


        # ----------------------------------------------------
        # 4B. RPM RANGE VALIDATION
        # ----------------------------------------------------

        if rpm > 3000:

            print(
                f"[ALERT] Invalid Engine RPM | "
                f"RPM={rpm}"
            )

            return


        # ----------------------------------------------------
        # 4C. RPM BEHAVIOR / SPOOFING DETECTION
        # ----------------------------------------------------

        if can_id in last_rpm:

            previous_rpm = last_rpm[can_id]

            rpm_change = abs(
                rpm - previous_rpm
            )


            if rpm_change > MAX_RPM_CHANGE:

                print(
                    f"[ALERT] Possible spoofing attack | "
                    f"ID=0x{can_id:03X} | "
                    f"Previous RPM={previous_rpm} | "
                    f"Current RPM={rpm} | "
                    f"Change={rpm_change}"
                )

                return


        # Save current RPM

        last_rpm[can_id] = rpm


        # ----------------------------------------------------
        # 4D. NORMAL ENGINE MESSAGE
        # ----------------------------------------------------

        print(
            f"[OK] Engine RPM: {rpm} | "
            f"Counter: {counter}"
        )


    # ========================================================
    # VEHICLE SPEED
    # ========================================================

    elif can_id == CAN_IDS["VEHICLE_SPEED"]:

        speed = decoded


        if speed > 120:

            print(
                f"[ALERT] Invalid vehicle speed | "
                f"Speed={speed} km/h"
            )

            return


        print(
            f"[OK] Vehicle Speed: "
            f"{speed} km/h"
        )


    # ========================================================
    # BRAKE STATUS
    # ========================================================

    elif can_id == CAN_IDS["BRAKE_STATUS"]:

        brake_status = decoded


        if brake_status not in (0, 1):

            print(
                f"[ALERT] Invalid brake status | "
                f"Value={brake_status}"
            )

            return


        if brake_status == 1:

            print(
                "[OK] Brake Status: APPLIED"
            )

        else:

            print(
                "[OK] Brake Status: RELEASED"
            )


    # ========================================================
    # GPS STATUS
    # ========================================================

    elif can_id == CAN_IDS["GPS_STATUS"]:

        gps_status = decoded


        if gps_status not in (0, 1):

            print(
                f"[ALERT] Invalid GPS status | "
                f"Value={gps_status}"
            )

            return


        if gps_status == 1:

            print(
                "[OK] GPS Status: AVAILABLE"
            )

        else:

            print(
                "[OK] GPS Status: UNAVAILABLE"
            )


# ============================================================
# MAIN MONITOR
# ============================================================

def main():

    print("=" * 60)
    print(" AGRICULTURAL VEHICLE CAN SECURITY MONITOR")
    print("=" * 60)

    print(
        f"Interface : {INTERFACE}"
    )

    print(
        f"Channel   : {CHANNEL}"
    )

    print()

    print("Security checks:")
    print("  [1] CAN flooding")
    print("  [2] Unknown CAN IDs")
    print("  [3] Invalid data length")
    print("  [4] Replay attacks")
    print("  [5] Stale/out-of-order frames")
    print("  [6] Engine RPM validation")
    print("  [7] RPM spoofing detection")
    print("  [8] Vehicle speed validation")
    print("  [9] Brake status validation")
    print(" [10] GPS status validation")

    print()

    print("Press CTRL+C to stop.")
    print("=" * 60)
    print()


    # ========================================================
    # OPEN CAN BUS
    # ========================================================

    try:

        bus = can.Bus(
            interface=INTERFACE,
            channel=CHANNEL
        )

    except Exception as error:

        print(
            f"[ERROR] Could not open CAN interface: {error}"
        )

        return


    # ========================================================
    # RECEIVE CAN FRAMES
    # ========================================================

    try:

        while True:

            message = bus.recv(
                timeout=1.0
            )


            if message is None:

                continue


            analyze_frame(message)


    except KeyboardInterrupt:

        print()
        print("CAN monitor stopped.")


    finally:

        bus.shutdown()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
