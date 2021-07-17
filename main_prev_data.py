'''
    Code that print the one day result
'''
from data_prev import data
from model import model
from tqdm import tqdm
import numpy as np
import argparse
import os

def main(input_file, output_file, num_node, num_sensor, num_window, set_idx, rank):
    data_stream = data(input_file, num_node, num_sensor, num_window, set_idx)
    test_model = model(num_node, num_sensor, rank, 1e7, 1e-4)
    # Initialize matrix
    normed_mat = data_stream.normalize_matrix(data_stream.curr_mat)
    test_model.GD_initialize(normed_mat, 100)

    with open(output_file, 'w') as f:
        f.write(data_stream.lines[0] + "\n")
        # Write the result
        X_tilde = data_stream.denormalize_matrix(np.matmul(test_model.P, test_model.Q.transpose()))
        if set_idx == 1:
            print_str = ''
            for i in range(num_node):
                print_str = print_str + f'{data_stream.curr_time},'
                for j in range(num_sensor):
                    print_str = print_str + f'{X_tilde[i, j]},'

            print_str = print_str + "\n"
            f.write(print_str)
        elif set_idx == 2:
            print_str = data_stream.curr_time + ","
            for i in range(num_node):
                for j in range(num_sensor):
                    print_str = print_str + f'{X_tilde[i, j]},'

            print_str = print_str + str(data_stream.curr_flag) + "\n"
            f.write(print_str)

        elif set_idx == 3:
            print_str = data_stream.curr_time + ","
            for i in range(num_sensor):
                print_str = print_str + f'{X_tilde[0, i]},'
            print_str = print_str + '\n'
            f.write(print_str)

        elif set_idx == 4:
            print_str = data_stream.curr_reg_dat + ","
            for i in range(num_node):
                print_str = print_str + f'{data_stream.curr_time[i]},'
                for j in range(num_sensor):
                    print_str = print_str + f'{X_tilde[i, j]},'
                print_str = print_str + data_stream.curr_comm_stat[i]
            print_str = print_str + '\n'
            f.write(print_str)
        elif set_idx == 5:
            print_str = data_stream.curr_time + ","
            for i in range(num_sensor):
                print_str = print_str + f'{X_tilde[0, i]},'
            print_str = print_str + str(data_stream.curr_flag) + "\n"
            f.write(print_str)

        while data_stream.curr_line < data_stream.num_line - 1:
            # Update the factor matrix
            data_stream.update_window()
            normed_mat = data_stream.normalize_matrix(data_stream.curr_mat)
            test_model.run(normed_mat)

            # Write the result
            X_tilde = data_stream.denormalize_matrix(np.matmul(test_model.P, test_model.Q.transpose()))
            if set_idx == 1:
                print_str = ''
                for i in range(num_node):
                    print_str = print_str + f'{data_stream.curr_time},'
                    for j in range(num_sensor):
                        print_str = print_str + f'{X_tilde[i, j]},'

                print_str = print_str + "\n"
                f.write(print_str)
            elif set_idx == 2:
                print_str = data_stream.curr_time + ","
                for i in range(num_node):
                    for j in range(num_sensor):
                        print_str = print_str + f'{X_tilde[i, j]},'

                print_str = print_str + str(data_stream.curr_flag) + "\n"
                f.write(print_str)

            elif set_idx == 3:
                print_str = data_stream.curr_time + ","
                for i in range(num_sensor):
                    print_str = print_str + f'{X_tilde[0, i]},'
                print_str = print_str + '\n'
                f.write(print_str)

            elif set_idx == 4:
                print_str = data_stream.curr_reg_dat + ","
                for i in range(num_node):
                    print_str = print_str + f'{data_stream.curr_time[i]},'
                    for j in range(num_sensor):
                        print_str = print_str + f'{X_tilde[i, j]},'
                    print_str = print_str + data_stream.curr_comm_stat[i]
                print_str = print_str + '\n'
                f.write(print_str)

            elif set_idx == 5:
                print_str = data_stream.curr_time + ","
                for i in range(num_sensor):
                    print_str = print_str + f'{X_tilde[0, i]},'
                print_str = print_str + str(data_stream.curr_flag) + "\n"
                f.write(print_str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--set-idx', type=int, default=5, help='a index for a target set')
    parser.add_argument('-i', '--input-folder', type=str, default='../data/previous', help='the folder that contains set files')
    parser.add_argument('-o', '--output-folder', type=str, default='result', help='the folder that saves outputs')
    args = parser.parse_args()
    num_nodes = [9, 10, 1, 9, 1]
    num_sensors = [7, 7, 5, 7, 5]
    window_len = 10
    ranks = [3, 3, 1, 3, 1]

    input_folder = args.input_folder + "/set" + str(args.set_idx) + "/"
    output_folder = args.output_folder + "/set" + str(args.set_idx) + "/"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in tqdm(os.listdir(input_folder)):
        main(os.path.join(input_folder, filename), os.path.join(output_folder, filename),
             num_nodes[args.set_idx -1], num_sensors[args.set_idx - 1],
             window_len, args.set_idx, ranks[args.set_idx - 1])
        #print(os.path.join(target_folder, filename))
    #main(args)