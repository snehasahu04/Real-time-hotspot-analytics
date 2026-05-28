import subprocess
import re
from datetime import datetime

previous_devices = {}

def get_arp_devices():

    output = subprocess.check_output(
        "arp -a",
        shell=True
    ).decode(errors="ignore")

    devices = {}

    pattern = r"(\d+\.\d+\.\d+\.\d+)\s+([0-9A-Fa-f\-]{17})"
    matches = re.findall(pattern, output)

    for ip, mac in matches:
        devices[mac] = ip
        print(f"{datetime.utcnow().isoformat()} | ARP DEVICE: {ip} {mac}")

    return devices


if __name__ == "__main__":
    print("🔥 ARP TRACKER STARTED")
    get_arp_devices()