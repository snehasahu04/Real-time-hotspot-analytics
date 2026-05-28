from dotenv import load_dotenv
import os

load_dotenv()

KAFKA_HOST = os.getenv("KAFKA_HOST")
KAFKA_PORT = os.getenv("KAFKA_PORT")

BOOTSTRAP_SERVER = f"{KAFKA_HOST}:{KAFKA_PORT}"

TOPIC_CONNECTION = os.getenv("KAFKA_TOPIC_CONNECTION")
TOPIC_BANDWIDTH = os.getenv("KAFKA_TOPIC_BANDWIDTH")
TOPIC_DNS = os.getenv("KAFKA_TOPIC_DNS")
TOPIC_ANOMALY = os.getenv("KAFKA_TOPIC_ANOMALY")