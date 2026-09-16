import can
import time

from can_protocol import CAN_IDS


# ============================================================
# SECURE CAN GATEWAY CONFIGURATION
# ============================================================

INPUT_CHANNEL = "vcan0"
OUTPUT_CHANNEL = "vcan1"

RATE_LIMIT = 10
MAX_RPM = 3000
MAX_RPM_CHANGE = 500
MAX_SPEED = 120


# ============================================================
# ALLOWED CAN IDs
# ============================================================

ALLOWED_CAN_IDS = {
    CAN_IDS["ENGINE_RPM"],
    CAN_IDS["VEHICLE_SPEED"],
    CAN_IDS["BRAKE_STATUS"],
    CAN_IDS["GPS_STATUS"],
}


# ============================================================
# EXPECTED DATA LENGTH
# ============================================================

EXPECTED_LENGTH = {
    CAN_IDS["ENGINE_RPM"]: 3,
    CAN_IDS["VEHICLE_SPEED"]: 2,
    CAN_IDS["BRAKE_STATUS"]: 1,
    CAN_IDS["GPS_STATUS"]: 1,
}


# ============================================================
# SECURITY STATE
# ============================================================

message_counts = {}
window_start = time.time()

last_counters = {}
last_rpm = {}


# ============================================================
# RATE LIMITING
# ============================================================

def check_rate(can_id):

    global message_counts
    global window_start

    now = time.time()

    # Start a new one-second window
    if now - window_start >= 1.0:
        message_counts = {}
        window_start = now

    message_counts[can_id] = message_counts.get(can_id, 0) + 1

    if message_counts[can_id] > RATE_LIMIT:
        return False

    return True


# ============================================================
# DATA LENGTH VALIDATION
# ============================================================

def check_length(can_id, data):

    expected = EXPECTED_LENGTH[can_id]

    if len(data) != expected:

        print(
            f"[BLOCK] Invalid data length | "
            f"ID=0x{can_id:03X} | "
            f"Expected={expected} | "
            f"Received={len(data)}"
        )

        return False

    return True


# ============================================================
# ENGINE RPM VALIDATION
# ============================================================

def validate_engine_rpm(data):

    rpm = int.from_bytes(
        data[0:2],
        byteorder="big"
    )

    counter = data[2]

    # --------------------------------------------------------
    # 1. RPM RANGE VALIDATION
    # --------------------------------------------------------

    if rpm > MAX_RPM:

        print(
            f"[BLOCK] Invalid Engine RPM | "
            f"RPM={rpm}"
        )

        return False

    # --------------------------------------------------------
    # 2. COUNTER VALIDATION
    # --------------------------------------------------------

    if CAN_IDS["ENGINE_RPM"] in last_counters:

        previous_counter = last_counters[
            CAN_IDS["ENGINE_RPM"]
        ]

        counter_difference = (
            counter - previous_counter
        ) % 256

        # Same counter = replay
        if counter_difference == 0:

            print(
                f"[BLOCK] Replay detected | "
                f"Counter={counter}"
            )

            return False

        # Large backwards jump = stale/out-of-order
        if counter_difference > 128:

            print(
                f"[BLOCK] Out-of-order counter | "
                f"Previous={previous_counter} | "
                f"Current={counter}"
            )

            return False

    # --------------------------------------------------------
    # 3. RPM CHANGE VALIDATION
    # --------------------------------------------------------

    if CAN_IDS["ENGINE_RPM"] in last_rpm:

        previous_rpm = last_rpm[
            CAN_IDS["ENGINE_RPM"]
        ]

        rpm_change = abs(
            rpm - previous_rpm
        )

        if rpm_change > MAX_RPM_CHANGE:

            print(
                f"[BLOCK] Possible RPM spoofing | "
                f"Previous={previous_rpm} | "
                f"Current={rpm} | "
                f"Change={rpm_change}"
            )

            return False

    # --------------------------------------------------------
    # UPDATE TRUSTED STATE
    # --------------------------------------------------------

    last_counters[
        CAN_IDS["ENGINE_RPM"]
    ] = counter

    last_rpm[
        CAN_IDS["ENGINE_RPM"]
    ] = rpm

    return True


# ============================================================
# VEHICLE SPEED VALIDATION
# ============================================================

def validate_vehicle_speed(data):

    speed = int.from_bytes(
        data[0:2],
        byteorder="big"
    )

    if speed > MAX_SPEED:

        print(
            f"[BLOCK] Invalid vehicle speed | "
            f"Speed={speed} km/h"
        )

        return False

    return True


# ============================================================
# BRAKE STATUS VALIDATION
# ============================================================

def validate_brake(data):

    brake_status = data[0]

    if brake_status not in (0, 1):

        print(
            f"[BLOCK] Invalid brake status | "
            f"Value={brake_status}"
        )

        return False

    return True


# ============================================================
# GPS STATUS VALIDATION
# ============================================================

def validate_gps(data):

    gps_status = data[0]

    if gps_status not in (0, 1):

        print(
            f"[BLOCK] Invalid GPS status | "
            f"Value={gps_status}"
        )

        return False

    return True


# ============================================================
# COMPLETE FRAME VALIDATION
# ============================================================

def validate_frame(message):

    can_id = message.arbitration_id
    data = message.data

    # --------------------------------------------------------
    # 1. CAN ID ALLOWLIST
    # --------------------------------------------------------

    if can_id not in ALLOWED_CAN_IDS:

        print(
            f"[BLOCK] Unknown CAN ID | "
            f"ID=0x{can_id:03X}"
        )

        return False

    # --------------------------------------------------------
    # 2. RATE LIMITING
    # --------------------------------------------------------

    if not check_rate(can_id):

        print(
            f"[BLOCK] CAN flooding detected | "
            f"ID=0x{can_id:03X}"
        )

        return False

    # --------------------------------------------------------
    # 3. DATA LENGTH
    # --------------------------------------------------------

    if not check_length(can_id, data):

        return False

    # --------------------------------------------------------
    # 4. SIGNAL-SPECIFIC VALIDATION
    # --------------------------------------------------------

    if can_id == CAN_IDS["ENGINE_RPM"]:

        if not validate_engine_rpm(data):

            return False

    elif can_id == CAN_IDS["VEHICLE_SPEED"]:

        if not validate_vehicle_speed(data):

            return False

    elif can_id == CAN_IDS["BRAKE_STATUS"]:

        if not validate_brake(data):

            return False

    elif can_id == CAN_IDS["GPS_STATUS"]:

        if not validate_gps(data):

            return False

    return True


# ============================================================
# MAIN GATEWAY
# ============================================================

def main():

    print("=" * 70)
    print("              SECURE CAN GATEWAY")
    print("=" * 70)

    print()
    print(f" INPUT  : {INPUT_CHANNEL} (UNTRUSTED)")
    print(f" OUTPUT : {OUTPUT_CHANNEL} (TRUSTED)")

    print()
    print("Security controls:")
    print("  [1] CAN ID allowlist")
    print("  [2] Rate limiting")
    print("  [3] Data length validation")
    print("  [4] Engine RPM range validation")
    print("  [5] Counter validation")
    print("  [6] RPM change / spoofing detection")
    print("  [7] Vehicle speed validation")
    print("  [8] Brake status validation")
    print("  [9] GPS status validation")

    print()
    print("Press CTRL+C to stop.")
    print("=" * 70)
    print()

    # --------------------------------------------------------
    # OPEN INPUT CAN BUS
    # --------------------------------------------------------

    try:

        input_bus = can.Bus(
            interface="socketcan",
            channel=INPUT_CHANNEL
        )

        # ----------------------------------------------------
        # OPEN OUTPUT CAN BUS
        # ----------------------------------------------------

        output_bus = can.Bus(
            interface="socketcan",
            channel=OUTPUT_CHANNEL
        )

    except Exception as error:

        print(
            f"[ERROR] Could not open CAN interfaces: {error}"
        )

        return

    # --------------------------------------------------------
    # RECEIVE AND VALIDATE FRAMES
    # --------------------------------------------------------

    try:

        while True:

            message = input_bus.recv(
                timeout=1.0
            )

            if message is None:
                continue

            # ------------------------------------------------
            # SECURITY VALIDATION
            # ------------------------------------------------

            if validate_frame(message):

                # --------------------------------------------
                # FORWARD ONLY VALIDATED FRAMES
                # --------------------------------------------

                output_bus.send(message)

                print(
                    f"[FORWARD] "
                    f"ID=0x{message.arbitration_id:03X} "
                    f"DATA={message.data.hex(' ')}"
                )

            else:

                # --------------------------------------------
                # BLOCK MALICIOUS / INVALID FRAME
                # --------------------------------------------

                print(
                    f"[DROP] "
                    f"ID=0x{message.arbitration_id:03X}"
                )

    except KeyboardInterrupt:

        print()
        print("Secure gateway stopped.")

    finally:

        input_bus.shutdown()
        output_bus.shutdown()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
