from pydantic import BaseModel
from typing import Optional

class TrafficEvent(BaseModel):

    device_ip: str

    device_mac: Optional[str]

    event_type: str

    bytes_sent: Optional[int]

    bytes_received: Optional[int]

    domain: Optional[str]

    timestamp: str