import os
import sys
import time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if SCRIPT_DIR in sys.path:
    sys.path.remove(SCRIPT_DIR)

from app.collectors.connection_collector import get_hotspot_devices
from app.kafka.producer import send_event
from app.config import TOPIC_CONNECTION


def main():

    print("\n🔥 HOTSPOT REAL DEVICE TRACKER STARTED\n")

    while True:

        try:
            events = get_hotspot_devices()

            if events:

                for e in events:

                    send_event(TOPIC_CONNECTION, e)

                
                    print("🔥 REAL HOTSPOT EVENT DETECTED")

                    print(f"🕒 TIME : {e['timestamp']}")
                    print(f"📌 EVENT: {e['event_type']}")
                    print(f"🌐 IP   : {e['device_ip']}")
                    print(f"💻 MAC  : {e['device_mac']}")


            else:
                print(
    f"\n⚪ [{datetime.utcnow().isoformat()}] "
    f"No hotspot device changes..."
)
            time.sleep(5)

        except KeyboardInterrupt:
            print("\n🛑 Stopped by user")
            break

        except Exception as e:
            print("Error:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()
