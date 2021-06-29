import numpy as np
class model:
    '''
        num_node: the number of row
        num_sensor: the number of column
        Threshold for cutting the outlier
    '''
    def __init__(self, num_node, num_sensor, rank, thre, lr):
        self.num_node, self.num_sensor = num_node, num_sensor
        self.rank, self.thre, self.lr = rank, thre, lr
        self.P = np.random.rand(num_node, rank)
        self.Q = np.random.rand(num_sensor, rank)

    # target_X should be values subtracted by outlier terms
    def GD_single_step(self, target_X):
        X_diff = target_X - np.matmul(self.P, self.Q.transpose())
        # Update P
        for i in range(self.num_node):
            temp = X_diff[i, :] * self.Q.transpose()
            temp = np.sum(temp, axis=1)
            self.P[i, :] = self.P[i, :] + self.lr * temp.transpose()

        # Update Q
        for i in range(self.num_sensor):
            temp = (X_diff[:, i].T * self.P.T).T
            temp = np.sum(temp, axis=0)
            self.Q[i, :] = self.Q[i, :] + self.lr * temp

    # initialize the matrix
    def GD_initialize(self, target_X, num_iter):
        for i in range(num_iter):
            self.GD_single_step(target_X)
            X_diff = target_X - np.matmul(self.P, self.Q.transpose())
            rmse = np.sqrt(np.sum(X_diff * X_diff) / self.num_node / self.num_sensor)
            print(f'iter: {i}, rmse: {rmse}')

    '''
        X_data: data object in data.py
        curr_time: print of the current time
        print_node: Row to be printed
        file_d: file descriptor to write results
    '''
    def run(self, X_data, curr_time, print_node, file_d):
        outlier = np.matmul(self.P, self.Q.transpose()) - X_data.curr_mat
        O_idx = np.absolute(outlier) < self.thre * X_data.compute_std()
        outlier[O_idx] = 0.
        self.GD_single_step(X_data.curr_mat - outlier)
        print_str = f'{curr_time}, '

        X_tilde = np.matmul(self.P, self.Q.transpose())
        for i in range(self.num_sensor):
            print_str = print_str + f'{X_data.curr_mat[print_node, i]}, {X_tilde[print_node, i]},'
        print_str = print_str + "\n"
        file_d.write(print_str)
