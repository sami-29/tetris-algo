import numpy as np
cimport numpy as np

def calculate_placement_height(np.ndarray[np.int_t, ndim=2] board, np.ndarray[np.int_t, ndim=2] tetromino, int col):
    cdef int height = 0
    cdef int rows = tetromino.shape[0]
    cdef int cols = tetromino.shape[1]

    while height + rows <= board.shape[0] and not np.any(board[height:height+rows, col:col+cols] + tetromino > 1):
        height += 1

    return height
