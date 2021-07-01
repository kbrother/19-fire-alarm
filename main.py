import paho.mqtt.client as mqtt
import sys

# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f"connected wit result code {rc}")
    client.subscribe("/eag/cfd")

# The callback function for when a PUBLISH message is received from the server
def raw_data_callback(client, userdata, msg):
    # matrix_list = json_parser(msg.payload)
    # udpate the stat
    # make new json
    print("end")
    #message_info = client.publish("/eag/cfd/preprocess", payload=msg)

def main(host, port):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.message_callback_add("eag/cfd", raw_data_callback)

    client.connect(host, port)

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    client.loop_forever()

if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))