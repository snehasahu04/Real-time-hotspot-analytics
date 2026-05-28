import subprocess

from app.collectors import connection_collector, anomaly_detector
from app.kafka import producer as kafka_producer
from app.schemas.event_schema import TrafficEvent
from kafka.errors import NoBrokersAvailable


def test_traffic_event_schema_valid():
    event = {
        "device_ip": "192.168.12.5",
        "device_mac": "A8:6B:AD:63:F6:1D",
        "event_type": "BANDWIDTH_UPDATE",
        "bytes_sent": 102938,
        "bytes_received": 223819,
        "domain": "youtube.com",
        "timestamp": "2026-05-11T17:10:00"
    }

    parsed = TrafficEvent(**event)

    assert parsed.device_ip == "192.168.12.5"
    assert parsed.domain == "youtube.com"
    assert parsed.bytes_sent == 102938


def test_connection_collector_parses_device_events(monkeypatch):
    sample_output = (
        "192.168.1.2    00-11-22-33-44-55    Reachable\n"
        "192.168.1.3    66-77-88-99-AA-BB    Reachable\n"
    )

    def fake_check_output(cmd, shell=False, text=None, encoding=None, errors=None, timeout=None):
        if isinstance(cmd, list) and cmd[0] == "powershell":
            return sample_output
        if shell:
            return ""
        raise AssertionError(f"Unexpected subprocess call: {cmd}")

    monkeypatch.setattr(subprocess, "check_output", fake_check_output)
    monkeypatch.setattr(connection_collector, "previous_devices", {})

    events = connection_collector.get_hotspot_devices()

    assert any(event["event_type"] == "DEVICE_CONNECTED" for event in events)
    assert any(event["device_mac"] == "00-11-22-33-44-55" for event in events)


def test_anomaly_detector_returns_normal_event():
    event = {"bytes_sent": 100, "bytes_received": 200, "device_ip": "192.168.1.2", "device_mac": "AA:BB:CC:DD:EE:FF"}
    result = anomaly_detector.detect_anomaly(event)

    assert result["event_type"] == "NORMAL_TRAFFIC"
    assert result["bytes_used"] == 300


def test_anomaly_detector_returns_anomaly_event():
    event = {"bytes_sent": 2 * 1024 * 1024 * 1024, "bytes_received": 0, "device_ip": "192.168.1.2", "device_mac": "AA:BB:CC:DD:EE:FF"}
    result = anomaly_detector.detect_anomaly(event)

    assert result["event_type"] == "ANOMALY_DETECTED"
    assert result["bytes_used"] >= 1024 * 1024 * 1024


def test_kafka_send_event_handles_no_brokers(monkeypatch, capsys):
    class FakeProducer:
        def __init__(self, *args, **kwargs):
            raise NoBrokersAvailable("broker unavailable")

    monkeypatch.setattr(kafka_producer, "KafkaProducer", FakeProducer)
    monkeypatch.setattr(kafka_producer, "producer", None)

    kafka_producer.send_event("test_topic", {"event_type": "TEST_EVENT"})

    captured = capsys.readouterr()
    assert "Kafka broker unavailable" in captured.out
