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


def test_rpm_spoofing_detection():
    reset_gateway_state()

    legitimate = make_message(
        0x100,
        [0x05, 0xDC, 0x10]
    )

    spoofed = make_message(
        0x100,
        [0x0B, 0xB8, 0x11]
    )

    assert validate_frame(legitimate) is True
    assert validate_frame(spoofed) is False


def test_replay_detection():
    reset_gateway_state()

    frame = make_message(
        0x100,
        [0x03, 0xE8, 0x20]
    )

    assert validate_frame(frame) is True
    assert validate_frame(frame) is False


def test_rate_limiting():
    reset_gateway_state()

    for counter in range(10):
        frame = make_message(
            0x100,
            [
                0x03,
                0xE8,
                counter
            ]
        )

        assert validate_frame(frame) is True

    flood_frame = make_message(
        0x100,
        [0x03, 0xE8, 10]
    )

    assert validate_frame(flood_frame) is False
