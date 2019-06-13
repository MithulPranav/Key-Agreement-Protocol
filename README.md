# Key-Agreement-Protocol
Establishment of key agreement protocol in an IoT Framework

Devices : Raspberry Pi 3B+ or Computer

Files:

SensorA.py and SensorB.py - The sensors has its predeployment, registration and athentication phase. In the authentication phase the sensor agrees on a key with another sensor for communication between them using the gateway. This way both the sensors end up having the same key.

Gateway.py - The node to which all the sensors are connected. This acts as an intermediate between the two sensors and helps the two sensors agree on a key
