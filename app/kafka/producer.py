import json
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from app.config import BOOTSTRAP_SERVER

producer = None


def get_producer():
    global producer
    if producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=BOOTSTRAP_SERVER,

                security_protocol="SSL",

                ssl_cafile="certs/ca.pem",
                ssl_certfile="certs/service.cert",
                ssl_keyfile="certs/service.key",

                value_serializer=lambda v: json.dumps(v).encode("utf-8")
            )
            print("✅ Kafka producer initialized")
        except NoBrokersAvailable as e:
            print("⚠ Kafka broker unavailable:", e)
            return None
        except Exception as e:
            print("⚠ Kafka producer init error:", e)
            return None
    return producer


def send_event(topic, event):
    producer_instance = get_producer()
    if producer_instance is None:
        print(f"⚠ Skipping send for {topic}, Kafka producer unavailable")
        return

    try:
        producer_instance.send(topic, event)
        producer_instance.flush()
        print(f"Sent to {topic}: {event}")
    except NoBrokersAvailable as e:
        print("⚠ Kafka broker unavailable during send:", e)
    except Exception as e:
        print("⚠ Kafka send error:", e)