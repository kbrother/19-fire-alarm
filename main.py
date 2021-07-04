import paho.mqtt.client as mqtt
import sys
import json
import argparse
from data import data
from model import model
import numpy as np

# The callback function of connection
def on_connect(client, userdata, flags, rc):
    print(f"connected wit result code {rc}")
    client.subscribe("/eag/cfd")

# The callback function for when a PUBLISH message is received from the server
def raw_data_callback(client, userdata, msg):
    print(msg.payload)
    curr_dict = json.loads(msg.payload)
    if curr_idx % 3 == 0:
        for i in range(len(curr_dict["cfd"]) - 1):
            if curr_idx < window_len:
                data_stream_list[i].build_window(curr_dict)
                if curr_idx == window_len-1:
                    normed_mat = data_stream_list[i].normalize_matrix(data_stream_list[i].curr_mat)
                    mat_model_list[i].GD_initialize(normed_mat, 100)
            else:
                data_stream_list[i].update_window(curr_dict)
                normed_mat = data_stream_list[i].normalize_matrix(data_stream_list[i].curr_mat)
                mat_model_list[i].run(normed_mat)
                X_tilde = data_stream_list[i].denormalize_matrix(np.matmul(mat_model_list[i].P, mat_model_list[i].Q.transpose()))

                print_str = f'{curr_time}, '
                for i in range(mat_model_list[i].num_sensor):
                    print_str = print_str + f'{data_stream_list[i].curr_mat[print_node, i]}, {X_tilde[print_node, i]},'
                print_str = print_str + "\n"

    curr_idx += 1
    # matrix_list = json_parser(msg.payload)
    # udpate the stat
    # make new json
    #message_info = client.publish("/eag/cfd/preprocess", payload=msg)

def main(host, port):
    client = mqtt.Client()
    client.on_connect = on_connect
    client.message_callback_add("/eag/cfd", raw_data_callback)
    client.connect(host, port)

    # Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
    client.loop_forever()

'''
    python main.py Host Port window_len num_node num_sensor num_channel
'''
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', type=str, default='127.0.0.1', help='host name')
    parser.add_argument('--port', type=int, default=1883, help='port')
    parser.add_argument('--window-len', type=int, default=15, help='the length ofi window')
    parser.add_argument('--num-node', type=int, default=2, help="the number of node")
    parser.add_argument('--num-sensor', type=int, default=7, help="the number of sensor")
    parser.add_argument('--num-channel', type=int, default=1, help="the number of channel")
    args = parser.parse_args()

    curr_idx, print_node = 0, 0
    mat_model_list = [model(args.num_node, args.num_sensor, 5, 1e7, 1e-4) for _ in range(args.num_channel)]
    data_stream_list = [data(args.num_node, args.num_sensor, args.window_len) for _ in range(args.window_len)]
    main(args.host, args.port)
