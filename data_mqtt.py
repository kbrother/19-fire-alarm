import numpy as np
class data:
    '''
        Save only vital parameter
        num_node: the number of row
        num_sensor: the number of column
        window_len: the length of window
    '''
    def __init__(self, num_node, num_sensor, window_len):
        self.num_sensor = num_sensor
        self.window_len = window_len
        self.num_node = num_node

        # Initialize window
        # The last entry of the window is set to the current matrix
        self.curr_window = []
        self.avg_mat = np.zeros((self.num_node, self.num_sensor))
        self.sq_mat = np.zeros((self.num_node, self.num_sensor))

    # Append a single matrix to json
    def build_window(self, json_dict):
        curr_mat = self.parse_json(json_dict)
        self.curr_window.append(curr_mat)
        self.avg_mat = self.avg_mat + curr_mat
        self.sq_mat = self.sq_mat + curr_mat * curr_mat

        if len(self.curr_window) == self.window_len:
            self.avg_mat = self.avg_mat / self.window_len
            #self.curr_mat = np.copy(self.curr_window[-1])
            self.compute_std()

    # Extract a single matrix from json input
    def parse_json(self, json_dict):
        curr_mat = np.zeros((self.num_node, self.num_sensor))
        # Set the first column
        for i in range(self.num_node):
            curr_mat[i, 0] = json_dict["temp"][i]
        for i in range(self.num_node):
            curr_mat[i, 1] = json_dict["hum"][i]
        for i in range(self.num_node):
            curr_mat[i, 2] = json_dict["pm1"][i]
        for i in range(self.num_node):
            curr_mat[i, 3] = json_dict["pm2"][i]
        for i in range(self.num_node):
            curr_mat[i, 4] = json_dict["pm10"][i]
        for i in range(self.num_node):
            curr_mat[i, 5] = json_dict["co2"][i]
        for i in range(self.num_node):
            curr_mat[i, 6] = json_dict["co"][i]
        return curr_mat

    # Move the window by a single matrix
    # Get the matrix of average and std
    def update_window(self, X_refined):
        out_mat = self.curr_window.pop(0)
        in_mat = self.curr_mat.copy()
        self.curr_window.append(in_mat)

        self.avg_mat = self.avg_mat + (in_mat - out_mat) / self.window_len
        self.sq_mat = self.sq_mat + np.square(in_mat) - np.square(out_mat)
        self.compute_std()

    # Save the std of the current matrix in 'self.std'
    def compute_std(self):
        temp = self.sq_mat / self.window_len - self.avg_mat * self.avg_mat
        temp[temp < 0] = 0.
        self.std_mat = np.sqrt(temp)

    # Normalize the current matrix with the average and the standard deviation
    def normalize_matrix(self, input_mat):
        eps = 1e-7
        return (input_mat - self.avg_mat) / (self.std_mat + eps)

    # Denormalize the current matrix with the average and the std
    def denormalize_matrix(self, input_mat):
        eps = 1e-7
        return input_mat * (self.std_mat + eps) + self.avg_mat
