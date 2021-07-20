import paho.mqtt.client as mqtt
import sys
import json
import argparse
from data_mqtt import data
from model import model
import numpy as np

# The callback function of connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print(f"connection success")
    client.subscribe("/eag/cfd")

# The callback function for when a PUBLISH message is received from the server
def raw_data_callback(client, userdata, msg):
   # print(msg.payload)
    curr_dict = json.loads(msg.payload)
#    print(f'{user_data["curr_idx"]} start'
    output_dict = {"cfd": []}
    if userdata['curr_idx'] % 3 == 0:
        template_dict = {"ch": 0, "id": [], "temp": [], "hum": [], "pm1": [],
                         "pm2": [], "pm10": [], "co2": [], "co": [],
                         "err": [], "sw_v": [], "tm": []}
        for i in range(len(curr_dict["cfd"]) - 1):                   
            curr_template = template_dict.copy()
            if userdata['curr_idx']/3 < userdata['window_len']:
                userdata['data_stream_list'][i].build_window(curr_dict["cfd"][i])
                if userdata['curr_idx']/3 == userdata['window_len']-1:
                    normed_mat = userdata['data_stream_list'][i].normalize_matrix(userdata['data_stream_list'][i].curr_mat)
                    userdata['mat_model_list'][i].GD_initialize(normed_mat, 100)
            else:
                userdata['data_stream_list'][i].update_window(curr_dict["cfd"][i])
                normed_mat = userdata['data_stream_list'][i].normalize_matrix(userdata['data_stream_list'][i].curr_mat)
                userdata['mat_model_list'][i].run(normed_mat)
                X_tilde = userdata['data_stream_list'][i].denormalize_matrix(np.matmul(userdata['mat_model_list'][i].P, userdata['mat_model_list'][i].Q.transpose()))
                curr_template["ch"] = i + 1

                num_id = len(curr_dict["cfd"][i]["id"])
                curr_template["ch"] = i + 1
                for j in range(num_id):
                    curr_template["id"].append(j + 1)
                    curr_template["temp"].append(X_tilde[j, 0])
                    curr_template["hum"].append(X_tilde[j, 1])
                    curr_template["pm1"].append(X_tilde[j, 2])
                    curr_template["pm2"].append(X_tilde[j, 3])
                    curr_template["pm10"].append(X_tilde[j, 4])
                    curr_template["co2"].append(X_tilde[j, 5])
                    curr_template["co"].append(X_tilde[j, 6])

                curr_template["err"] = curr_dict["cfd"][i]["err"].copy()
                curr_template["sw_v"] = curr_dict["cfd"][i]["sw_v"].copy()
                curr_template["tm"] = curr_dict["cfd"][i]["tm"].copy()

                output_dict["cfd"].append(curr_template)
            
            print(template_dict)
            '''
                print_str = f''
                for j in range(userdata['mat_model_list'][i].num_sensor):
                    print_str = print_str + f'real data: {userdata["data_stream_list"][i].curr_mat[userdata["print_node"], j]}, our data: {X_tilde[userdata["print_node"], j]},\t'
                print(print_str)
        
            '''
        template_dict["ch"] = len(curr_dict["cfd"])
        output_dict["cfd"].append(template_dict.copy())

    if userdata["curr_idx"] == 0:
        print('intialization start')
 
    if userdata["curr_idx"] % 3 == 0:
        # Publish data
        if userdata['curr_idx'] / 3 < userdata['window_len']:
            output_json = msg.payload
            client.publish("/eag/preprocess", msg.payload)
        else:
            output_json = json.dumps(output_dict)
            client.publish("/eag/preprocess", json.dumps(output_dict))
#        print(output_json)
        client.publish("/eag/preprocess", output_json)

        if userdata['curr_idx']/3 == userdata['window_len']-1:
            print(f'{user_data["curr_idx"] + 1} seconds passed')
            print(f'initialization finished\n')
        else:            
            print(f'{user_data["curr_idx"] + 1} seconds passed\n')
    
    userdata["curr_idx"] += 1
    client.user_data_set(userdata)
    # matrix_list = json_parser(msg.payload)
    # udpate the stat
    # make new json
    #message_info = client.publish("/eag/cfd/preprocess", payload=msg)

def main(host, port, user_data):
    client = mqtt.Client(userdata=user_data)
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
    parser.add_argument('--window-len', type=int, default=5, help='the length ofi window')
    parser.add_argument('--num-node', type=int, default=2, help="the number of node")
    parser.add_argument('--num-sensor', type=int, default=7, help="the number of sensor")
    parser.add_argument('--num-channel', type=int, default=1, help="the number of channel")
    args = parser.parse_args()

    user_data = {'curr_idx': 0, 'print_node': 0, 'window_len': args.window_len}
    user_data['mat_model_list'] = [model(args.num_node, args.num_sensor, 5, 1e7, 1e-4) for _ in range(args.num_channel)]
    user_data['data_stream_list'] = [data(args.num_node, args.num_sensor, args.window_len) for _ in range(args.num_channel)]
    main(args.host, args.port, user_data)
