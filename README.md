# Real-time-hotspot-analytics

Real-time Hotspot Analytics is a Python pipeline for monitoring devices and traffic on a local Windows hotspot/network. It detects device connection changes, tracks bandwidth usage, observes DNS activity, flags high-bandwidth anomalies, and publishes events to Kafka.

## Features

- Detects connected and disconnected hotspot devices from the Windows neighbor table.
- Tracks per-interval upload and download usage with `psutil`.
- Captures DNS lookups with Scapy/Npcap.
- Flags traffic anomalies when usage crosses the configured threshold.
- Publishes structured JSON events to Kafka over SSL.
- Includes pytest coverage for event validation, collectors, anomaly logic, and Kafka error handling.

## Project Structure

```text
app/
  collectors/        Device, bandwidth, DNS, and anomaly collectors
  kafka/             Kafka producer and topic helpers
  schemas/           Pydantic event schemas
  certs/             Kafka SSL certificate files
  config.py          Environment-based configuration
  main.py            Main hotspot device tracking loop
tests/
  test_pipeline.py   Unit tests
.github/workflows/
  ci.yml             GitHub Actions test workflow
```

## Requirements

- Python 3.13
- Windows PowerShell for hotspot device discovery
- Kafka broker reachable over SSL
- Npcap installed if you want to run the DNS collector

Install Python dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root:

```env
KAFKA_HOST=localhost
KAFKA_PORT=9093
KAFKA_TOPIC_CONNECTION=hotspot.connection
KAFKA_TOPIC_BANDWIDTH=hotspot.bandwidth
KAFKA_TOPIC_DNS=hotspot.dns
KAFKA_TOPIC_ANOMALY=hotspot.anomaly
```

Kafka SSL files are expected at:

```text
app/certs/ca.pem
app/certs/service.cert
app/certs/service.key
```

Because the producer currently references certificate paths as `certs/...`, run Kafka-producing scripts from inside the `app` directory unless you adjust the paths in `app/kafka/producer.py`.

## Running

Start the main hotspot device tracker:

```powershell
cd app
python main.py
```

Run the bandwidth collector directly:

```powershell
python collectors\bandwidth_collector.py
```

Run the DNS collector directly:

```powershell
python collectors\dns_collector.py
```

The collectors print live events to the terminal. Kafka publishing is skipped gracefully when the broker is unavailable.

## Event Shape

Events are validated with the `TrafficEvent` schema:

```json
{
  "device_ip": "192.168.1.5",
  "device_mac": "AA:BB:CC:DD:EE:FF",
  "event_type": "DEVICE_CONNECTED",
  "bytes_sent": 1024,
  "bytes_received": 2048,
  "domain": "example.com",
  "timestamp": "2026-05-28T17:10:00"
}
```

Some fields are optional depending on the event type.

## Testing

Run the test suite from the project root:

```powershell
pytest -q
```

The CI workflow also runs `pytest -q` on every push and pull request.

## Notes

- Device discovery uses `Get-NetNeighbor`, so it is Windows-specific.
- DNS capture requires a valid Npcap interface and may need administrator privileges.
- The anomaly detector currently flags traffic at or above 1 GB.
