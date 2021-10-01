'''
    Code that print the one day result
'''
from data_web import data
from model import model
from tqdm import tqdm
import numpy as np
import argparse

def main(args):
    data_stream = data(args.input_file, args.num_node, args.num_sensor, args.window_len)
    test_model = model(args.num_node, args.num_sensor, 3, 50, 1e-4)
    # Initialize matrix
    normed_mat = data_stream.normalize_matrix(data_stream.curr_mat)
    test_model.GD_initialize(normed_mat, 100)

    pbar = tqdm(total=data_stream.num_line)
    pbar.update(data_stream.curr_line)
    with open(args.output_file, 'w') as f:
        f.write('temp orig, temp ours, humid orig, humid ours, CO orig, CO ours, CO2 orig, CO2 ours, \
            PM1.0 orig, PM1.0 ours, PM2.5 orig, PM2.5 ours, PM10 orig, PM10 ours, Register_Date\n')
        while data_stream.curr_line < data_stream.num_line - args.num_node:
            # Normalize matrix
            data_stream.update_mat()
            normed_mat = data_stream.normalize_matrix(data_stream.curr_mat)
            refined_mat = test_model.run(normed_mat)
            refined_mat = data_stream.denormalize_matrix(refined_mat)
            data_stream.curr_mat = refined_mat

            # Update the factor matrix
            data_stream.update_window()
            pbar.update(data_stream.num_node)

            # Write the result
            X_tilde = data_stream.denormalize_matrix(np.matmul(test_model.P, test_model.Q.transpose()))
            for k in range(args.num_write):
                print_str = ''

                hour = int(data_stream.curr_date.split()[-1].split(':')[0])
                if hour >=8 and hour < 21:
                    for j in range(test_model.num_sensor):
                        print_str = print_str + f'{data_stream.curr_mat[args.target_node, j]}, {X_tilde[args.target_node, j]},'
                    print_str = print_str + data_stream.curr_date
                    print_str = print_str + "\n"
                    f.write(print_str)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--input-file', type=str, default='input_data/210520_문창시장3_robust.csv', help='the input file')
    parser.add_argument('-n', '--num-node', type=int, default=7, help='the number of node')
    parser.add_argument('-s', '--num-sensor', type=int, default=7, help='the number of sensor')
    parser.add_argument('-w', '--window-len', type=int, default=40, help='the length of window')
    parser.add_argument('-o', '--output-file', type=str, default='result/210903/문창시장3_robust.csv', help='the output file')
    parser.add_argument('-t', '--target-node', type=int, default=0, help='the target node')
    parser.add_argument('-nw', '--num-write', type=int, default=1, help='the number of duplicate writes')
    args = parser.parse_args()

    main(args)