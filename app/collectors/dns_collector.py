import os
import sys
from datetime import datetime, timezone

from scapy.all import sniff, DNS, IP, get_if_list


# =====================================================
# ROOT PATH
# =====================================================

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


# =====================================================
# IMPORTS
# =====================================================

from app.kafka.producer import send_event
from app.config import TOPIC_DNS


# =====================================================
# INTERFACE DETECTION
# =====================================================

available_interfaces = get_if_list()

print("\n📡 AVAILABLE INTERFACES:\n")

for iface in available_interfaces:
    print(iface)

# auto-select interface
HOTSPOT_INTERFACE = next(

    (
        i for i in available_interfaces

        if i.startswith("\\Device\\NPF_")

        and "Loopback" not in i
    ),

    None
)

if not HOTSPOT_INTERFACE:

    raise SystemExit(
        "❌ No valid Npcap interface found."
    )

print(f"\n✅ USING INTERFACE:\n{HOTSPOT_INTERFACE}")

print("\n🌐 LISTENING FOR REAL DNS TRAFFIC...\n")


# =====================================================
# DUPLICATE FILTER
# =====================================================

seen_domains = set()


# =====================================================
# PACKET PROCESSOR
# =====================================================

def process(packet):

    try:

        # DNS only
        if not packet.haslayer(DNS):
            return

        dns_layer = packet[DNS]

        # query exists?
        if not getattr(dns_layer, 'qd', None):
            return

        # domain
        domain = dns_layer.qd.qname.decode(
            errors="ignore"
        ).rstrip(".")

        # source ip
        src_ip = (
            packet[IP].src
            if packet.haslayer(IP)
            else "unknown"
        )

        # skip localhost
        if src_ip.startswith("127."):
            return

        # hotspot/local network only
        if not (
            src_ip.startswith("192.168.")
            or src_ip.startswith("172.")
        ):
            return

        # duplicate filter
        key = (src_ip, domain)

        if key in seen_domains:
            return

        seen_domains.add(key)

        # =================================================
        # EVENT
        # =================================================

        event = {

            "event_type": "DNS_ACTIVITY",

            "device_ip": src_ip,

            "domain": domain,

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat()
        }

        # =================================================
        # SEND TO KAFKA
        # =================================================

        send_event(TOPIC_DNS, event)

        # =================================================
        # LOGS
        # =================================================

        print("\n🌐 REAL DNS ACTIVITY DETECTED")

        print(f"DEVICE IP : {src_ip}")

        print(f"DOMAIN    : {domain}")

        print(f"TIME      : {event['timestamp']}")

    except Exception as e:

        print("❌ DNS Collector Error:", e)


# =====================================================
# START SNIFFING
# =====================================================

sniff(

    iface=HOTSPOT_INTERFACE,

    filter="port 53",

    prn=process,

    store=0
)