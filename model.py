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
            #print(f'iter: {i}, rmse: {rmse}')

    '''
        curr_mat: the current input matrix
    '''
    def run(self, curr_mat):
        outlier = np.matmul(self.P, self.Q.transpose()) - curr_mat
        O_idx = np.absolute(outlier) < self.thre
        outlier[O_idx] = 0.
        self.GD_single_step(curr_mat + outlier)