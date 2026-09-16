import can
import secure_gateway

from secure_gateway import validate_frame


def make_message(can_id, data):
    return can.Message(
        arbitration_id=can_id,
        data=data,
        is_extended_id=False
    )


def reset_gateway_state():
    secure_gateway.message_counts = {}
    secure_gateway.window_start = secure_gateway.time.time()
    secure_gateway.last_counters = {}
    secure_gateway.last_rpm = {}


def test_valid_engine_rpm():
    reset_gateway_state()

    message = make_message(
        0x100,
        [0x03, 0xE8, 0x00]
    )

    assert validate_frame(message) is True


def test_invalid_engine_rpm():
    reset_gateway_state()

    message = make_message(
        0x100,
        [0x13, 0x88, 0x01]
    )

    assert validate_frame(message) is False


def test_valid_vehicle_speed():
    reset_gateway_state()

    message = make_message(
        0x200,
        [0x00, 0x78]
    )

    assert validate_frame(message) is True


def test_invalid_vehicle_speed():
    reset_gateway_state()

    message = make_message(
        0x200,
        [0x00, 0xFA]
    )

    assert validate_frame(message) is False


def test_invalid_brake_status():
    reset_gateway_state()

    message = make_message(
        0x300,
        [0x05]
    )

    assert validate_frame(message) is False


def test_invalid_gps_status():
    reset_gateway_state()

    message = make_message(
        0x400,
        [0x07]
    )

    assert validate_frame(message) is False


def test_unknown_can_id():
    reset_gateway_state()

    message = make_message(
        0x666,
        [0xDE, 0xAD, 0xBE, 0xEF]
    )

    assert validate_frame(message) is False


def test_invalid_data_length():
    reset_gateway_state()

    message = make_message(
        0x100,
        [0x03, 0xE8, 0x00, 0xFF]
    )

    assert validate_frame(message) is False
