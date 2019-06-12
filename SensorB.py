import time
import json
import paho.mqtt.client as mqtt

ip = "m16.cloudmqtt.com"
port = 13462
User = "iorvidyl"
Pass = "KPnhDWt1-_nG"

SID=6
r=10
XGWNS=22
Sf=0
U=0
K = 7
R=0
R2=0

def hash(a="",b="",c=""):
	t=int(str(str(a)+str(b)+str(c)))
	t=t^10
	return t

def senRegistration(data):
	SX = hash(MP,XGWNS)
	print ("SX: "+str(SX))
	global Sf
	Sf = data["Se"] ^ SX
	print ("Sf: "+str(Sf))
	SZ1 = hash(Sf,data["Se"],XGWNS)
	print ("SZ1: "+str(SZ1))
	
	if data["SZ"] == SZ1:
		print ("True")
	else:
		print ("False")
	
def senAuthentication(data):
	global U
	global R
	R = data["R"]
	U = R ^ K
	print ("U: "+str(U))

def nodeToNode(data):
	global R2
	R2 = data["R"]
	K2 = data["X"] ^ hash(U) ^ data["SID"]
	print ("K2: "+str(K2))
	if R2 ^ K2 == R ^ K:
		print ("Node to Node Communication Successful")
	else:
		print ("Node to Node Communication Unsuccessful")
		return
	SK = hash(K^K2)
	print ("SK: "+str(SK))

def on_connect(client,userdata,flags,rc):
    if rc == 0:
        print ("Connected")

def on_message(client, userdata, message):
	data=json.loads(message.payload.decode("utf-8"))
	print ("Data Received: "+str(data))
	if message.topic == "SenReg":
		senRegistration(data)
	if message.topic == "SenAuth":
		senAuthentication(data)
	if message.topic == "SensorB":
		nodeToNode(data)

def publish_data(topic,data):
	client.publish(topic,data)

def subscribeNode():
	client.loop_start()
	client.subscribe("SensorB")
	time.sleep(10)
	client.loop_stop()

print ("Connecting to cloudMQTT .....")
client=mqtt.Client("SensorB")
client.username_pw_set(User,Pass)
client.on_connect=on_connect
client.on_message=on_message
client.connect(ip,port)

# Starting Pre-Deployment
print ("Starting Pre-Deployment Phase .....")
data = { "SID" : SID , "XGWNS" : XGWNS }
data = json.dumps(data)
topic = "SenPreDep"
publish_data(topic,data)
print ("Pre-Deployment Phase Completed")

# Registration Phase
print ("Starting Registration Phase .....")
global MP
MP = hash(XGWNS,r,SID)
print ("MP: "+str(MP))
MN = r^XGWNS
print ("MN: "+str(MN))
RMP = MP^MN
print ("RMP: "+str(RMP))
data= { "SID" : SID , "RMP" : RMP , "MN" : MN }
data=json.dumps(data)

print ("Sending data to Gateway ....." + str(data))
topic="GateReg"
publish_data(topic,data)
print("Data sent")

client.loop_start()
client.subscribe("SenReg")
time.sleep(5)
client.loop_stop()
client.unsubscribe("SenReg")
print ("Registration Phase Completed")

# Activation Phase
print ("Starting Activation Phase .....")
SA = hash(MP,XGWNS) ^ K
SB = hash(SA,K,Sf)
data = { "SID" : SID , "SA" : SA , "SB" : SB }
data = json.dumps(data)
topic="GateAuth"
print ("Sending data to Gateway ..... "+str(data))
publish_data(topic,data)
client.loop_start()
client.subscribe("SenAuth")
time.sleep(5)
client.loop_stop()
client.unsubscribe("SenAuth")
print ("Activation Phase Completed")

# Node to Node Communication
ip = raw_input("Start node to node communication? Yes/No: ")
if ip == "Yes":
	X = hash(U) ^ K ^ SID
	print ("X: "+str(X))
	data = { "SID" : SID , "X" : X , "R" : R }
	data = json.dumps(data)
	topic = raw_input("Enter the Sensor Name you want to communicate with: ")
	time.sleep(2)
	publish_data(topic,data)
	client.loop_start()
	client.subscribe("SensorB")
	time.sleep(5)
	client.loop_stop()
	client.unsubscribe("SensorB")
	