# 19-fire-alarm

Python codes for the edge-gateway algorithm

## Requirements
* numpy
* paho-mqtt

## Download
git clone https://github.com/kbrother/19-fire-alarm.git

## Execution
```bash
python main_mqtt.py [-h] [--host HOST] [--port PORT] [--window-len WINDOW_LEN]
                    --num-node NUM_NODE [NUM_NODE ...]
                    [--num-sensor NUM_SENSOR] [--num-channel NUM_CHANNEL]

optional arguments:
  -h, --help            show this help message and exit
  --host HOST           host name
  --port PORT           port
  --window-len WINDOW_LEN
                        the length of window
  --num-node NUM_NODE [NUM_NODE ...]
                        the number of node
  --num-sensor NUM_SENSOR
                        the number of sensor
  --num-channel NUM_CHANNEL
                        the number of channel

```
