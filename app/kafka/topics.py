from kafka.admin import KafkaAdminClient, NewTopic
from app.config import *

admin_client = KafkaAdminClient(

    bootstrap_servers=BOOTSTRAP_SERVER,

    security_protocol="SSL",

    ssl_cafile="app/certs/ca.pem",

    ssl_certfile="app/certs/service.cert",

    ssl_keyfile="app/certs/service.key",

    api_version=(2,8,1),

    client_id="hotspot-admin"
)

topics = [

    NewTopic(
        name="connection_events",
        num_partitions=3,
        replication_factor=1
    ),

    NewTopic(
        name="bandwidth_events",
        num_partitions=3,
        replication_factor=1
    ),

    NewTopic(
        name="dns_events",
        num_partitions=3,
        replication_factor=1
    ),

    NewTopic(
        name="anomaly_events",
        num_partitions=3,
        replication_factor=1
    )
]

try:

    admin_client.create_topics(
        new_topics=topics
    )

    print("Topics created successfully")

except Exception as e:

    print(e)

finally:

    admin_client.close()