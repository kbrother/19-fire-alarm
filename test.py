from data import data
from model import model
from tqdm import tqdm

file_name = '20210608_문창시장1.csv'
num_node, num_sensor = 10, 7
initial_data = 1800
print_node = 9

data_stream = data(file_name, num_node, num_sensor, initial_data)
test_model = model(num_node, num_sensor, 5, 300, 1e-4)
test_model.GD_initialize(data_stream.curr_mat, 100)

pbar = tqdm(total=data_stream.num_line)
pbar.update(data_stream.curr_line)
with open('문창시장1_결과_node' + str(print_node) + '.csv', 'w') as f:
    while data_stream.curr_line < data_stream.num_line - num_node:
        curr_time = (data_stream.curr_line - 1) /data_stream.num_node
        test_model.run(data_stream, curr_time, print_node, f)
        data_stream.update_window()
        pbar.update(data_stream.num_node)