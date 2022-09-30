import paho.mqtt.client as mqtt
import gpiozero
import json

PIN = gpiozero.DigitalOutputDevice("BOARD33")

def on_message(_client, _userdata, msg):
   state = msg.payload == b"ON"
   PIN.value = state

   # Always publish the state after changing it so that HA
   # interface shows it correctly
   client.publish("pool/pump/state",
                  "ON" if state else "OFF")

def on_connect(client, _userdata, _flags, _rc):
   client.subscribe(f"pool/pump/set")

   # Autodiscovery
   client.publish(
     f"homeassistant/switch/pool/pump/config",
     json.dumps({
       "~": f"pool/pump",
       "command_topic": "~/set",
       "state_topic": "~/state",
       "unique_id": "pool_pump",
       "name": "pool_pump",
       "icon": "mdi:water-pump"
     })
    )

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("ada.lan", 1883, 60)
client.loop_forever()
