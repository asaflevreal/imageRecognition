import numpy as np
from PIL import Image
import pandas as pd
img1 = Image.open('/Users/asaflev/Downloads/floorplan/test/5c905e9799b4a70017083061_2_2_1820_4.png')
img1 = np.array(img1)
img1 = pd.DataFrame(img1)

# img1 = img1.resize((10, 10))
#
# # record the original shape
# shape = arr.shape
#
# # make a 1-dimensional view of arr
# flat_arr = arr.ravel()
#
# # convert it to a matrix
#
# # do something to the vector
#
# # reform a numpy array of the original shape
# arr2 = np.asarray(vector).reshape(shape)
#
# # make a PIL image
# img2 = Image.fromarray(arr2, 'RGBA')
# img2.show()
