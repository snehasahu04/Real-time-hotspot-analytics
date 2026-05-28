from datetime import datetime
import subprocess
import re
import time

previous_devices = {}


# =====================================================
# CHECK INTERNET ACTIVITY
# =====================================================

def has_real_connection(ip):

    try:

        output = subprocess.check_output(
            f'netstat -n | findstr {ip}',
            shell=True
        ).decode(errors="ignore")

        return bool(output.strip())

    except Exception as e:

        print("Connection check error:", e)
        return False


# =====================================================
# GET HOTSPOT DEVICES
# =====================================================

def get_hotspot_devices():

    global previous_devices

    try:

        cmd = (
            "Get-NetNeighbor -AddressFamily IPv4 | "
            "Where-Object {$_.State -ne 'Unreachable'}"
        )

        output = subprocess.check_output(
            ["powershell", "-Command", cmd],
            text=True,
            encoding="utf-8",
            errors="ignore",
            timeout=5
        )

        # DEBUG OUTPUT
        print("\n=========== RAW OUTPUT ===========")
        print(output)

        current_devices = {}
        events = []

        # IP + MAC
        pattern = r"(\d+\.\d+\.\d+\.\d+)\s+([0-9a-fA-F:-]{17})"

        matches = re.findall(pattern, output)

        print("\nMATCHES:", matches)

        # =================================================
        # CONNECTED DEVICES
        # =================================================

        for ip, mac in matches:

            # skip localhost only
            if ip.startswith("127."):
                continue

            current_devices[mac] = ip

            # NEW DEVICE CONNECTED
            if mac not in previous_devices:

                print("\n🟢 REAL DEVICE CONNECTED")
                print(f"IP  : {ip}")
                print(f"MAC : {mac}")

                events.append({

                    "device_ip": ip,
                    "device_mac": mac,
                    "event_type": "DEVICE_CONNECTED",
                    "timestamp": datetime.utcnow().isoformat()

                })

            # INTERNET ACTIVITY
            if has_real_connection(ip):

                print("\n📶 REAL INTERNET ACTIVITY DETECTED")
                print(f"DEVICE IP  : {ip}")
                print(f"DEVICE MAC : {mac}")

        # =================================================
        # DISCONNECTED DEVICES
        # =================================================

        for mac, ip in previous_devices.items():

            if mac not in current_devices:

                print("\n🔴 REAL DEVICE DISCONNECTED")
                print(f"IP  : {ip}")
                print(f"MAC : {mac}")

                events.append({

                    "device_ip": ip,
                    "device_mac": mac,
                    "event_type": "DEVICE_DISCONNECTED",
                    "timestamp": datetime.utcnow().isoformat()

                })

        previous_devices = current_devices

        return events

    except subprocess.TimeoutExpired:

        print("⚠ PowerShell command timeout")
        return []

    except Exception as e:

        print("❌ Collector Error:", e)
        return []


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print("🔥 REAL HOTSPOT DEVICE TRACKER STARTED\n")

    while True:

        events = get_hotspot_devices()

        if events:

            print("\n📦 EVENTS GENERATED:")
            print(events)

        time.sleep(5)