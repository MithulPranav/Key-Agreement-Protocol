import json
import paho.mqtt.client as mqtt

ip = "m16.cloudmqtt.com"
port = 13462
User = "iorvidyl"
Pass = "KPnhDWt1-_nG"

XGWN = 17
XGWNS = 0
U = 9
MP=0

def hash(a="", b="", c=""):
	t=int(str(str(a)+str(b)+str(c)))
	t=t^10
	return t

def publish_data(topic,data):
	client.publish(topic,data)

def sensorPreDep(data):
	global XGWNS
	XGWNS = data["XGWNS"]
	print ("XGWNS: "+str(XGWNS))

def sensorRegistration(data):
	global MP
	MP = data["RMP"] ^ data["MN"]
	print ("MP: "+str(MP))
	r = data["MN"] ^ XGWNS
	print("r: "+str(r))
	MP1 = hash(XGWNS,r,data["SID"])
	print ("MP1: "+str(MP1))

	if MP == MP1:
		print ("True")
	else:
		print ("False")
		return
	
	Sf = hash(data["SID"],XGWN)
	print ("Sf: "+str(Sf))
	SX = hash(MP,XGWNS)
	print ("SX: "+str(SX))
	Se = Sf ^ SX
	print ("Se: "+str(Se))
	SZ = hash(Sf,Se,XGWNS)
	print ("SZ: "+str(SZ))
	toSen = { "Se" : Se , "SZ" : SZ }
	toSen = json.dumps(toSen)
	topic = "SenReg"
	print ("Sending data to Sensor ....."+str(toSen))
	publish_data(topic,toSen)

def sensorActivation(data):
	K = hash(MP,XGWNS) ^ data["SA"]
	print ("K: "+str(K))
	Sf = hash(data["SID"],XGWN)
	print ("Sf: "+str(Sf))
	SB1 = hash(data["SA"],K,Sf)
	print ("SB1: "+str(SB1))

	if SB1 == data["SB"]:
		print ("True")
	else:
		print ("False")
		return

	R = U ^ K
	print ("R: "+str(R))
	data = {"R" : R}
	data=json.dumps(data)
	topic = "SenAuth"
	print ("Sending data to Sensor ....."+str(data))
	publish_data(topic,data)

def on_connect(client,userdata,flags,rc):
    if rc == 0:
        print ("Connected")

def on_message(client, userdata, message):
	data=json.loads(message.payload.decode("utf-8"))
	print ("Data Received: "+str(data))
	if message.topic == "SenPreDep":
		print ("Starting Sensor Pre-Deployment .....")
		sensorPreDep(data)
		print ("Sensor Pre-Deployment Completed")
	if message.topic == "GateReg":
		print ("Starting Sensor Registration .....")
		sensorRegistration(data)
		print ("Sensor Registration Completed")
	if message.topic == "GateAuth":
		print ("Starting Sensor Activation .....")
		sensorActivation(data)
		print ("Sensor Activation Completed")

print ("Connecting to cloudMQTT .....")
client=mqtt.Client("Gateway")
client.username_pw_set(User,Pass)
client.on_connect=on_connect
client.on_message=on_message
client.connect(ip,port)
print ("Subscribing .....")
client.subscribe("SenPreDep")
client.subscribe("GateReg")
client.subscribe("GateAuth")
client.loop_forever()