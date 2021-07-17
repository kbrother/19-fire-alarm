import numpy as np
class data:
    '''
        file_name: data file
        num_node: the number of row
        num_sensor: the number of column
    '''
    def __init__(self, file_name, num_node, num_sensor, window_len, set_idx):
        # Read lines from the file
        with open(file_name) as f:
            self.lines = f.read().split("\n")
        self.lines.pop(-1)

        self.num_sensor, self.window_len = num_sensor, window_len
        self.num_node, self.num_line = num_node, len(self.lines)
        self.set_idx = set_idx

        # Initialize window
        # The last entry of the window is set to the current matrix
        self.curr_window = []
        self.avg_mat = np.zeros((self.num_node, self.num_sensor))
        self.sq_mat = np.zeros((self.num_node, self.num_sensor))
        for i in range(1, 1 + self.window_len):
            curr_mat = self.extract_matrix(i)
            self.curr_window.append(curr_mat)
            self.avg_mat = self.avg_mat + curr_mat
            self.sq_mat = self.sq_mat + curr_mat * curr_mat

        self.avg_mat = self.avg_mat / self.window_len
        self.curr_mat = np.copy(self.curr_window[-1])
        self.compute_std()
        self.curr_line = self.window_len
        #self.normalize_matrix()

    # Given a line idx, get the matrix for that line
    def extract_matrix(self, line_idx):
        curr_matrix = np.ndarray(shape=(self.num_node, self.num_sensor))
        words = self.lines[line_idx].split(",")
        if self.set_idx == 1:
            for i in range(self.num_node):
                for j in range(self.num_sensor):
                    #print(words[i*8 + j + 1])
                    curr_matrix[i, j] = float(words[i*8 + j + 1])
                    #print(curr_matrix[i, j])
            self.curr_time = int(float(words[0]))

        elif self.set_idx == 2:
            for i in range(self.num_node):
                for j in range(self.num_sensor):
                    curr_matrix[i, j] = float(words[i*7 + j + 1])

            self.curr_time = words[0]
            self.curr_flag = int(float(words[-1]))

        elif self.set_idx == 3:
            for j in range(self.num_sensor):
                curr_matrix[0, j] = float(words[j + 1])
            self.curr_time = words[0]

        elif self.set_idx == 4:
            self.curr_comm_stat = []
            self.curr_time = []
            self.curr_reg_dat = words[0]
            for i in range(self.num_node):
                self.curr_time.append(int(float(words[9*i + 1])))
                for j in range(self.num_sensor):
                    curr_matrix[i, j] = float(words[9*i + j + 2])
                self.curr_comm_stat.append(words[9*i + 1 + self.num_sensor])

        elif self.set_idx == 5:
            self.curr_time = words[0]
            for i in range(self.num_sensor):
                curr_matrix[0, i] = float(words[i + 1])
            self.curr_flag = int(float(words[-1]))
        return curr_matrix

    # Move the window by a single matrix
    # Get the matrix of average and std
    def update_window(self):
        self.curr_line += 1
        out_mat = self.curr_window.pop(0)
        in_mat = self.extract_matrix(self.curr_line)
        self.curr_window.append(in_mat)

        self.avg_mat = self.avg_mat + (in_mat - out_mat) / self.window_len
        self.sq_mat = self.sq_mat + np.square(in_mat) - np.square(out_mat)
        self.curr_mat = np.copy(in_mat)
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