from datetime import datetime


# =====================================================
# ANOMALY DETECTOR
# =====================================================

def detect_anomaly(event):

    # 1 GB Threshold
    threshold = 1 * 1024 * 1024 * 1024

    bytes_used = (
        event.get("bytes_received", 0)
        +
        event.get("bytes_sent", 0)
    )

    # =================================================
    # ANOMALY DETECTED
    # =================================================

    if bytes_used >= threshold:

        anomaly_event = {

            "device_ip": event.get("device_ip"),

            "device_mac": event.get("device_mac"),

            "event_type": "ANOMALY_DETECTED",

            "bytes_used": bytes_used,

            "message": "1GB bandwidth threshold exceeded",

            "timestamp": datetime.utcnow().isoformat()
        }

        print("\n🚨 ANOMALY DETECTED")
        print(anomaly_event)

        return anomaly_event

    # =================================================
    # NORMAL TRAFFIC
    # =================================================

    normal_event = {

        "device_ip": event.get("device_ip"),

        "device_mac": event.get("device_mac"),

        "event_type": "NORMAL_TRAFFIC",

        "bytes_used": bytes_used,

        "message": "Traffic normal",

        "timestamp": datetime.utcnow().isoformat()
    }

    print("\n✅ NORMAL TRAFFIC")
    print(normal_event)

    return normal_event