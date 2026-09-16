import can
import time

from can_protocol import CAN_IDS

# Connect to virtual CAN bus
bus = can.Bus(
    interface="socketcan",
    channel="vcan0"
)

gps_status = 1

print("GPS/Telemetry ECU started...")
print("Press CTRL+C to stop.")

try:
    while True:

        # 0 = GPS unavailable
        # 1 = GPS available
        gps_data = bytes([gps_status])

        message = can.Message(
            arbitration_id=CAN_IDS["GPS_STATUS"],
            data=gps_data,
            is_extended_id=False
        )

        bus.send(message)

        if gps_status == 1:
            print("GPS ECU -> GPS AVAILABLE")
        else:
            print("GPS ECU -> GPS UNAVAILABLE")

        # Alternate status
        gps_status = 1 - gps_status

        time.sleep(3)

except KeyboardInterrupt:
    print("\nGPS/Telemetry ECU stopped.")

finally:
    bus.shutdown()
