# Agricultural Vehicle Embedded Cybersecurity Lab

A practical cybersecurity laboratory for simulating and monitoring
Controller Area Network (CAN) communication in an agricultural vehicle
environment.

The project uses Linux SocketCAN and a virtual CAN interface (`vcan0`)
to simulate multiple Electronic Control Units (ECUs), normal vehicle
communication, and cybersecurity attack scenarios.

> ⚠️ This project is a local cybersecurity laboratory. All CAN traffic
> and attack simulations are performed on a virtual CAN interface and
> are not conducted against real vehicles or physical systems.

## Objectives

- Understand CAN communication and message structure
- Simulate multiple vehicle ECUs
- Monitor CAN traffic in real time
- Detect abnormal CAN behavior
- Simulate common CAN attack scenarios
- Develop security monitoring logic using Python
- Build a foundation for an embedded vehicle cybersecurity testing platform

## Architecture

```text
                   Virtual CAN Bus
                       vcan0
                         |
        +----------------+----------------+
        |                |                |
   Engine ECU       Speed ECU        Brake ECU
   CAN ID 0x100     CAN ID 0x200     CAN ID 0x300
        |                |                |
        +----------------+----------------+
                         |
                    GPS ECU
                   CAN ID 0x400
                         |
                         v
                  CAN Security Monitor
                         |
              +----------+----------+
              |          |          |
           Unknown    Replay     Abnormal
             ID       Detection     Values
              |
           Flooding
           Detection
