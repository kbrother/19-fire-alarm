'''
    Code that print the one day result
'''
from data import data
from model import model
from tqdm import tqdm
import numpy as np

file_name = 'input_data/20210608_문창시장1.csv'
num_node, num_sensor = 10, 7
initial_data = 60  # window_len
print_node = 3 # node ID to be printed

data_stream = data(file_name, num_node, num_sensor, initial_data)
test_model = model(num_node, num_sensor, 5, 1e7, 1e-4)
# Initialize matrix
normed_mat = data_stream.normalize_matrix(data_stream.curr_mat)
test_model.GD_initialize(normed_mat, 100)

pbar = tqdm(total=data_stream.num_line)
pbar.update(data_stream.curr_line)
with open('result/문창시장1_결과_normalize_node' + str(print_node) + '.csv', 'w') as f:
    while data_stream.curr_line < data_stream.num_line - num_node:
        # Update the factor matrix
        data_stream.update_window()
        pbar.update(data_stream.num_node)
        curr_time = (data_stream.curr_line - 1) /data_stream.num_node
        normed_mat = data_stream.normalize_matrix(data_stream.curr_mat)
        test_model.run(normed_mat)

        # Write the result
        print_str = f'{curr_time}, '
        X_tilde = data_stream.denormalize_matrix(np.matmul(test_model.P, test_model.Q.transpose()))
        for i in range(test_model.num_sensor):
            print_str = print_str + f'{data_stream.curr_mat[print_node, i]}, {X_tilde[print_node, i]},'
        print_str = print_str + "\n"
        f.write(print_str)