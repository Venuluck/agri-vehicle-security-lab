import can
import time

from can_protocol import CAN_IDS, LIMITS


# Map CAN ID -> signal name
ID_TO_SIGNAL = {
    value: key
    for key, value in CAN_IDS.items()
}


# Expected payload length for each CAN message
EXPECTED_LENGTH = {
    CAN_IDS["ENGINE_RPM"]: 3,       # RPM (2 bytes) + counter (1 byte)
    CAN_IDS["VEHICLE_SPEED"]: 2,
    CAN_IDS["BRAKE_STATUS"]: 1,
    CAN_IDS["GPS_STATUS"]: 1,
}


# Maximum messages allowed per second for each CAN ID
RATE_LIMIT = 10


# Store message counts for rate monitoring
message_counts = {}


# Store the latest rolling counter for each CAN ID
last_counters = {}


# Start of rate measurement window
window_start = time.time()


def decode_value(message):
    """
    Decode the CAN payload according to our protocol.
    """

    signal = ID_TO_SIGNAL[message.arbitration_id]

    if signal == "ENGINE_RPM":

        # First two bytes = RPM
        rpm = int.from_bytes(
            message.data[:2],
            byteorder="big"
        )

        # Third byte = rolling counter
        counter = message.data[2]

        return rpm, counter

    if signal == "VEHICLE_SPEED":

        return int.from_bytes(
            message.data,
            byteorder="big"
        )

    if signal == "BRAKE_STATUS":

        return message.data[0]

    if signal == "GPS_STATUS":

        return message.data[0]


def analyze_frame(message):
    """
    Analyze one CAN frame and detect suspicious behavior.
    """

    global window_start
    global message_counts

    can_id = message.arbitration_id


    # =========================================================
    # 1. MESSAGE RATE MONITORING
    # =========================================================

    message_counts[can_id] = (
        message_counts.get(can_id, 0) + 1
    )

    current_time = time.time()

    if current_time - window_start >= 1:

        for monitored_id, count in message_counts.items():

            if count > RATE_LIMIT:

                print(
                    f"[ALERT] CAN flooding suspected | "
                    f"ID=0x{monitored_id:03X} | "
                    f"Rate={count} msg/s"
                )

        # Reset counters
        message_counts = {}

        window_start = current_time


    # =========================================================
    # 2. CHECK WHETHER CAN ID IS KNOWN
    # =========================================================

    if can_id not in ID_TO_SIGNAL:

        print(
            f"[ALERT] Unknown CAN ID: "
            f"0x{can_id:03X} | "
            f"Data={message.data.hex(' ')}"
        )

        return


    signal = ID_TO_SIGNAL[can_id]


    # =========================================================
    # 3. CHECK DATA LENGTH
    # =========================================================

    expected_length = EXPECTED_LENGTH[can_id]

    if len(message.data) != expected_length:

        print(
            f"[ALERT] Invalid length | "
            f"ID=0x{can_id:03X} | "
            f"Signal={signal} | "
            f"Expected={expected_length} | "
            f"Received={len(message.data)}"
        )

        return


    # =========================================================
    # 4. DECODE MESSAGE
    # =========================================================

    value = decode_value(message)


    # =========================================================
    # 5. ENGINE RPM
    # =========================================================

    if signal == "ENGINE_RPM":

        rpm, counter = value


        # -----------------------------------------------------
        # Replay / stale message detection
        # -----------------------------------------------------

        if can_id in last_counters:

            last_counter = last_counters[can_id]

            if counter <= last_counter:

                print(
                    f"[ALERT] Possible replay attack | "
                    f"ID=0x{can_id:03X} | "
                    f"Counter={counter} | "
                    f"Last Counter={last_counter}"
                )

                return


        # Store newest counter
        last_counters[can_id] = counter


        # -----------------------------------------------------
        # RPM validation
        # -----------------------------------------------------

        if rpm > LIMITS["ENGINE_RPM"]:

            print(
                f"[ALERT] Abnormal RPM: {rpm}"
            )

            return


        print(
            f"[OK] Engine RPM: {rpm} | "
            f"Counter: {counter}"
        )


    # =========================================================
    # 6. VEHICLE SPEED
    # =========================================================

    elif signal == "VEHICLE_SPEED":

        speed = value

        if speed > LIMITS["VEHICLE_SPEED"]:

            print(
                f"[ALERT] Abnormal vehicle speed: "
                f"{speed} km/h"
            )

            return


        print(
            f"[OK] Vehicle Speed: "
            f"{speed} km/h"
        )


    # =========================================================
    # 7. BRAKE STATUS
    # =========================================================

    elif signal == "BRAKE_STATUS":

        brake_status = value

        if brake_status not in (0, 1):

            print(
                f"[ALERT] Invalid brake status: "
                f"{brake_status}"
            )

            return


        status = (
            "APPLIED"
            if brake_status == 1
            else "RELEASED"
        )


        print(
            f"[OK] Brake: {status}"
        )


    # =========================================================
    # 8. GPS STATUS
    # =========================================================

    elif signal == "GPS_STATUS":

        gps_status = value

        if gps_status not in (0, 1):

            print(
                f"[ALERT] Invalid GPS status: "
                f"{gps_status}"
            )

            return


        status = (
            "AVAILABLE"
            if gps_status == 1
            else "UNAVAILABLE"
        )


        print(
            f"[OK] GPS: {status}"
        )


def main():

    # =========================================================
    # CONNECT TO VIRTUAL CAN BUS
    # =========================================================

    bus = can.Bus(
        interface="socketcan",
        channel="vcan0"
    )


    print("=" * 60)
    print(" CAN SECURITY MONITOR")
    print("=" * 60)

    print("Listening on vcan0...")

    print(
        f"Rate limit: "
        f"{RATE_LIMIT} messages/sec"
    )

    print(
        "Replay detection: ENABLED"
    )

    print(
        "Unknown CAN ID detection: ENABLED"
    )

    print(
        "Value validation: ENABLED"
    )

    print(
        "Press CTRL+C to stop."
    )

    print()


    # =========================================================
    # MAIN MONITORING LOOP
    # =========================================================

    try:

        while True:

            message = bus.recv()

            if message is not None:

                analyze_frame(message)


    except KeyboardInterrupt:

        print(
            "\nMonitor stopped."
        )


    finally:

        bus.shutdown()


# =============================================================
# PROGRAM ENTRY POINT
# =============================================================

if __name__ == "__main__":

    main()
