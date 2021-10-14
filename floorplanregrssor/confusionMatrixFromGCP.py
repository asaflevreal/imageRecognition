import pandas as pd
def get_normalized_confusion_matrix_fron_gcp(matrix):
    order_desired = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']
    matrix = matrix.reindex(order_desired)
    matrix = matrix[order_desired]
    matrix_norm = matrix.apply(lambda col: col / col.sum(), axis=0)
    return matrix_norm

matrix = pd.read_clipboard()
matrix = get_normalized_confusion_matrix_fron_gcp(matrix)