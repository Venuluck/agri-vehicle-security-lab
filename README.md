


# Agricultural Vehicle Embedded Cybersecurity Lab

A hands-on **automotive/embedded cybersecurity laboratory** that simulates Controller Area Network (CAN) communication inside an agricultural vehicle environment.

The project models multiple Electronic Control Units (ECUs), generates legitimate CAN traffic, simulates common CAN attacks, monitors suspicious activity, and implements a **secure CAN gateway** that validates and blocks malicious or malformed frames.

The entire laboratory runs locally using **Linux SocketCAN and virtual CAN interfaces (`vcan0` / `vcan1`)**, so no physical vehicle or automotive hardware is required.

> ⚠️ **Safety:** This is an isolated cybersecurity laboratory. All CAN traffic and attack simulations are performed against virtual CAN interfaces and are not intended for use against real vehicles or physical systems.

---

## 🎯 Project Objectives

This project was developed to explore practical security controls for CAN-based embedded vehicle systems.

Key objectives:

* Understand CAN message structures and communication
* Simulate multiple vehicle ECUs
* Monitor CAN traffic in real time
* Detect abnormal and potentially malicious CAN frames
* Simulate common CAN attack techniques
* Validate CAN message structure and signal values
* Detect replay and spoofing behavior
* Implement CAN ID allowlisting
* Implement message-rate limiting
* Build a security gateway that blocks invalid traffic
* Automate security testing with GitHub Actions

---

## 🏗️ Architecture

```text
                         AGRICULTURAL VEHICLE
                              CAN NETWORK

                                vcan0
                                  |
        +-------------------------+-------------------------+
        |                         |                         |
   +----------+              +----------+              +----------+
   | Engine   |              |  Speed   |              |  Brake   |
   |   ECU    |              |   ECU    |              |   ECU    |
   | 0x100    |              | 0x200    |              | 0x300    |
   +----------+              +----------+              +----------+
        |                         |                         |
        +-------------------------+-------------------------+
                                  |
                              +-------+
                              |  GPS  |
                              |  ECU  |
                              | 0x400 |
                              +-------+
                                  |
                                  v
                       +----------------------+
                       |   CAN Security       |
                       |      Monitor         |
                       +----------------------+
                                  |
              +-------------------+-------------------+
              |                   |                   |
              v                   v                   v
        Unknown ID          Replay / Counter      Abnormal
        Detection             Detection            Values
                                  |
                                  v
                         +----------------------+
                         |   Secure CAN         |
                         |      Gateway         |
                         +----------------------+
                                  |
                           Validation / Filtering
                                  |
                                  v
                                vcan1
                           Trusted CAN Network
```

---

## 🚗 Simulated ECUs

The laboratory defines four primary CAN signals:

| ECU / Signal  |  CAN ID | Payload               |
| ------------- | ------: | --------------------- |
| Engine RPM    | `0x100` | RPM + rolling counter |
| Vehicle Speed | `0x200` | Speed                 |
| Brake Status  | `0x300` | Brake state           |
| GPS Status    | `0x400` | GPS state             |

CAN protocol definitions and signal limits are centralized in `can_protocol.py`.

---

## 🔐 Security Monitoring

The CAN monitoring component analyzes incoming frames and checks for multiple types of suspicious behavior.

### 1. CAN Flooding Detection

The monitor tracks the number of messages received for each CAN ID.

If a CAN ID exceeds the configured threshold of:

```text
10 messages/second
```

the monitor generates a flooding alert.

Example:

```text
[ALERT] CAN flooding suspected | ID=0x100 | Rate=...
```

---

### 2. Unknown CAN ID Detection

Only known CAN IDs are accepted by the protocol definition.

An unexpected ID such as:

```text
0x666
```

is reported as suspicious.

Example:

```text
[ALERT] Unknown CAN ID | ID=0x666
```

---

### 3. CAN Data-Length Validation

Each CAN ID has an expected payload length.

For example:

```text
Engine RPM   → 3 bytes
Vehicle Speed → 2 bytes
Brake Status → 1 byte
GPS Status   → 1 byte
```

Frames with unexpected payload lengths are rejected by the security logic.

---

### 4. Replay Detection

Engine RPM frames contain a one-byte rolling counter.

The monitor checks whether the counter progresses correctly.

Repeated counters can indicate replayed frames.

Example:

```text
[ALERT] Possible replay attack
```

The counter logic also handles the normal wraparound:

```text
254 → 255 → 0 → 1
```

---

### 5. Stale / Out-of-Order Detection

Large backwards jumps in the rolling counter are treated as potentially stale or out-of-order frames.

This helps identify previously captured frames that are being injected again.

---

### 6. Engine RPM Validation

The simulated engine has a maximum RPM of:

```text
3000 RPM
```

Values above this limit trigger an alert.

---

### 7. RPM Spoofing Detection

The monitor compares consecutive RPM values.

A change greater than:

```text
500 RPM
```

between consecutive Engine ECU frames is treated as potentially suspicious.

Example:

```text
Previous RPM = 1200
Current RPM  = 3000

[ALERT] Possible spoofing attack
```

---

### 8. Vehicle Speed Validation

Vehicle speed is checked against the configured simulation limit:

```text
120 km/h
```

Values above this threshold generate an alert.

---

### 9. Brake Status Validation

The brake signal accepts only:

```text
0 = Released
1 = Applied
```

Other values are treated as invalid.

---

### 10. GPS Status Validation

The GPS signal accepts:

```text
0 = Unavailable
1 = Available
```

Unexpected values are rejected.

---

# 🛡️ Secure CAN Gateway

In addition to monitoring, the project implements a **security gateway** that separates an untrusted CAN interface from a trusted CAN interface.

```text
        UNTRUSTED CAN
             |
           vcan0
             |
             v
     +----------------+
     | Secure Gateway |
     +----------------+
             |
       Validation
             |
      +------+------+ 
      |             |
   VALID          INVALID
      |             |
      v             v
   FORWARD         DROP
      |             |
      v             X
    vcan1
```

The gateway performs:

* CAN ID allowlisting
* Message rate limiting
* Data-length validation
* Engine RPM range validation
* Rolling-counter validation
* Replay detection
* Out-of-order detection
* RPM change validation
* Vehicle speed validation
* Brake status validation
* GPS status validation

Valid frames are forwarded to `vcan1`.

Invalid or suspicious frames are dropped.

Example:

```text
[BLOCK] Unknown CAN ID | ID=0x666
[DROP] ID=0x666
```

---

# 🧪 Attack Simulations

The laboratory includes several controlled CAN attack simulations.

## CAN Flooding

`flood_attack.py`

Generates a high rate of CAN frames against the Engine ECU CAN ID.

```text
Target: 0x100
Rate: approximately 1000 frames/second
```

Used to test rate-based flooding detection.

---

## Replay Attack

`replay_attack.py`

Repeatedly transmits a previously captured Engine ECU frame:

```text
CAN ID : 0x100
RPM    : 1000
Counter: 0
```

The rolling-counter validation can identify repeated frames.

---

## RPM Spoofing

`spoof_attack.py`

Observes legitimate Engine ECU messages and injects a fake RPM value using the next counter value.

This tests whether the monitoring and gateway logic can identify an abnormal RPM change.

---

## Unknown CAN ID Attack

`unknown_id_attack.py`

Generates traffic using an unauthorized CAN identifier:

```text
0x666
```

The security gateway's CAN ID allowlist blocks the frame.

---

## Invalid Message Attacks

The project also contains dedicated invalid-input simulations:

```text
invalid_brake_attack.py
invalid_gps_attack.py
invalid_length_attack.py
invalid_rpm_attack.py
invalid_speed_attack.py
```

These are used to test validation of malformed or out-of-range signal values.

---

# 🧪 Automated Security Testing

The project includes automated tests using **pytest**.

Test categories include:

```text
tests/
├── test_protocol.py
├── test_security_controls.py
└── test_validation.py
```

Current test result:

```text
14 passed
```

GitHub Actions automatically executes the test suite when changes are pushed to the repository or submitted through a pull request.

### CI Pipeline

```text
Git Push / Pull Request
          |
          v
   GitHub Actions
          |
          v
   Python 3.12 Setup
          |
          v
 Install Dependencies
          |
          v
     pytest -q
          |
          v
    14/14 Tests Pass
```

---

# 🛠️ Technologies

| Technology           | Purpose                             |
| -------------------- | ----------------------------------- |
| Python               | Security tooling and ECU simulation |
| python-can           | CAN communication                   |
| Linux SocketCAN      | CAN networking                      |
| Virtual CAN (`vcan`) | Isolated CAN laboratory             |
| pytest               | Automated security testing          |
| GitHub Actions       | CI automation                       |
| Git                  | Version control                     |

---

# 📁 Project Structure

```text
agri-vehicle-security-lab/
│
├── brake_ecu.py
├── engine_ecu.py
├── speed_ecu.py
├── gps_ecu.py
│
├── can_protocol.py
├── can_monitor.py
├── secure_gateway.py
│
├── can_flood.py
├── flood_attack.py
├── replay_attack.py
├── replay_attack_gateway.py
├── spoof_attack.py
├── unknown_id_attack.py
│
├── invalid_brake_attack.py
├── invalid_gps_attack.py
├── invalid_length_attack.py
├── invalid_rpm_attack.py
├── invalid_speed_attack.py
│
├── tests/
│   ├── test_protocol.py
│   ├── test_security_controls.py
│   └── test_validation.py
│
├── pytest.ini
├── requirements.txt
└── README.md
```

---

# 🚀 Running the Laboratory

## 1. Clone the repository

```bash
git clone https://github.com/Venuluck/agri-vehicle-security-lab.git
cd agri-vehicle-security-lab
```

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

## 4. Run the tests

```bash
pytest -q
```

Expected result:

```text
14 passed
```

---

# 🖥️ Virtual CAN Setup

The project is designed around Linux SocketCAN virtual interfaces.

Create the virtual CAN interfaces:

```bash
sudo modprobe vcan

sudo ip link add dev vcan0 type vcan
sudo ip link set up vcan0

sudo ip link add dev vcan1 type vcan
sudo ip link set up vcan1
```

Verify:

```bash
ip link show vcan0
ip link show vcan1
```

---

# ▶️ Example Components

Start the CAN security monitor:

```bash
python3 can_monitor.py
```

Start the secure gateway:

```bash
python3 secure_gateway.py
```

Then run individual ECU simulations or attack simulations in separate terminals.

For example:

```bash
python3 engine_ecu.py
```

and:

```bash
python3 flood_attack.py
```

The monitor/gateway can then observe and analyze the generated CAN traffic.

---

# 🎓 Security Concepts Demonstrated

This project provides practical experience with:

* CAN bus security
* Embedded systems security
* Automotive cybersecurity
* ECU communication
* Network intrusion detection
* Protocol validation
* Input validation
* Replay attack detection
* Spoofing detection
* Flooding / denial-of-service detection
* Allowlisting
* Rate limiting
* Security gateways
* Defensive filtering
* Automated security testing
* CI/CD security testing

---

# 🔭 Future Improvements

Potential extensions include:

* CAN authentication / message integrity mechanisms
* Cryptographic MACs for CAN messages
* CAN-FD support
* More advanced anomaly detection
* Statistical traffic profiling
* Machine-learning-based CAN intrusion detection
* Logging to a SIEM platform
* Wazuh / Elastic integration
* Suricata-style alerting
* ECU authentication
* Security event dashboards
* Containerized laboratory deployment
* Integration with automotive security standards such as ISO/SAE 21434

---

# ⚠️ Disclaimer

This project is intended strictly for **educational cybersecurity research and defensive testing**.

All attack simulations operate against virtual CAN interfaces in an isolated laboratory environment.

No real vehicle, ECU, agricultural machine, or physical CAN network is targeted.

---

## 👤 Author

**Venu Pydala**

M.Sc. Cybersecurity — EPITA

GitHub: [@Venuluck](https://github.com/Venuluck)

---

## 📌 Project Highlights

```text
CAN Security Monitoring       ✓
Secure CAN Gateway            ✓
Replay Detection              ✓
Spoofing Detection            ✓
Flooding Detection            ✓
Unknown ID Detection          ✓
Input Validation              ✓
Rate Limiting                 ✓
Automated Security Tests      ✓
GitHub Actions CI             ✓
14/14 Tests Passing           ✓
```

































