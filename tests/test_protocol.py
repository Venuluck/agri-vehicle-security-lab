from can_protocol import CAN_IDS, LIMITS


def test_can_ids_are_defined():
    assert CAN_IDS["ENGINE_RPM"] == 0x100
    assert CAN_IDS["VEHICLE_SPEED"] == 0x200
    assert CAN_IDS["BRAKE_STATUS"] == 0x300
    assert CAN_IDS["GPS_STATUS"] == 0x400


def test_engine_rpm_limit():
    assert LIMITS["ENGINE_RPM"] == 3000


def test_vehicle_speed_limit():
    assert LIMITS["VEHICLE_SPEED"] == 120
