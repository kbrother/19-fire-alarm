import numpy as np
class data:
    '''
        file_name: data file
        num_node: the number of row
        num_sensor: the number of column
    '''
    def __init__(self, file_name, num_node, num_sensor, window_len):
        # Read lines from the file
        with open(file_name) as f:
            self.lines = f.read().split("\n")

        self.num_sensor = num_sensor
        self.curr_line = 1 + num_node * (window_len - 1)
        self.window_len = window_len
        self.num_node = num_node
        self.num_line = len(self.lines) - 1

        # Initialize window
        # The last entry of the window is set to the current matrix
        self.curr_window = []
        self.avg_mat = np.zeros((self.num_node, self.num_sensor))
        self.sq_mat = np.zeros((self.num_node, self.num_sensor))
        for i in range(1, 1 + self.window_len*self.num_node, self.num_node):
            curr_mat = self.extract_matrix(i)
            self.curr_window.append(curr_mat)
            self.avg_mat = self.avg_mat + curr_mat
            self.sq_mat = self.sq_mat + curr_mat * curr_mat

        self.avg_mat = self.avg_mat / self.window_len
        self.curr_mat = np.copy(self.curr_window[-1])
        #self.normalize_matrix()

    # Given a line idx, get the matrix for that line
    def extract_matrix(self, line_idx):
        curr_matrix = np.ndarray(shape=(self.num_node, self.num_sensor))
        for i in range(line_idx, self.num_node + line_idx):
            words = self.lines[i].split(",")
            if len(words) < 2 + self.num_sensor:
                print(line_idx)
            for j in range(2, 2 + self.num_sensor):
                curr_matrix[i-line_idx, j-2] = words[j]

        return curr_matrix

    # Move the window by a single matrix
    # Get the matrix of average and std
    def update_window(self):
        self.curr_line += self.num_node
        out_mat = self.curr_window.pop(0)
        in_mat = self.extract_matrix(self.curr_line)
        self.curr_window.append(in_mat)

        self.avg_mat = self.avg_mat + (in_mat - out_mat) / self.window_len
        self.sq_mat = self.sq_mat + np.square(in_mat) - np.square(out_mat)
        self.curr_mat = np.copy(in_mat)
        self.normalize_matrix()

    def normalize_matrix(self):
        eps = 1e-7
        temp = self.sq_mat / self.window_len - self.avg_mat * self.avg_mat
        temp[temp < 0] = 0.
        std_mat = np.sqrt(temp)
        self.curr_mat =  (self.curr_mat - self.avg_mat) / (std_mat + eps)

    def compute_std(self):
        temp = self.sq_mat / self.window_len - self.avg_mat * self.avg_mat
        temp[temp < 0] = 0.
        std_mat = np.sqrt(temp)
        std_mat[std_mat < 1e-3] = 1
        return std_mat