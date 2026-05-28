import psutil
import time
from datetime import datetime


# =====================================================
# BANDWIDTH MONITOR
# =====================================================

def monitor_bandwidth():

    old = psutil.net_io_counters()

    while True:

        # wait 5 sec
        time.sleep(5)

        new = psutil.net_io_counters()

        # =================================================
        # EVENT
        # =================================================

        event = {

            "event_type": "BANDWIDTH_UPDATE",

            "bytes_sent":
                new.bytes_sent - old.bytes_sent,

            "bytes_received":
                new.bytes_recv - old.bytes_recv,

            "timestamp":
                datetime.utcnow().isoformat()
        }

        upload = event["bytes_sent"]

        download = event["bytes_received"]

        # =================================================
        # LIVE LOGS
        # =================================================

        print("\n📶 REAL-TIME BANDWIDTH USAGE")
        print("===================================")

        print(f"⬆ UPLOAD   : {upload} bytes / 5 sec")

        print(f"⬇ DOWNLOAD : {download} bytes / 5 sec")

        if upload > 0 or download > 0:

            print("🟢 INTERNET ACTIVITY DETECTED")

        else:

            print("⚪ NO INTERNET ACTIVITY")

        print(f"🕒 TIME : {event['timestamp']}")

        print("===================================\n")

        # =================================================
        # UPDATE OLD COUNTERS
        # =================================================

        old = new

        # return/send event if needed
        yield event


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print("🔥 BANDWIDTH COLLECTOR STARTED\n")

    for event in monitor_bandwidth():

        print("📦 EVENT GENERATED:")
        print(event)