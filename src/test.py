from PIL import Image
import model
import seamCarver as sc
import numpy as np
import random as rand

# img = Image.open(r"C:\users\sunny\OneDrive\Desktop\ImageEditor\test.png")
# seam = sc.findLowestSeam(np.array(img), 0)
# print(seam)
# img = sc.carveSeam(img, 2, 3)
# seam = sc.findLowestSeam(img, True)
# print(seam)
# img = sc.remove_seam(img, seam, 1)
# img.save(r"C:\users\sunny\OneDrive\Desktop\ImageEditor\test2.png")
# print(img.size)

img = np.array([[[255, 255, 0], [0, 255, 0], [0, 255, 255]], 
[[0, 255, 0], [255, 0, 255], [255, 0, 0]], 
[[0, 255, 255], [255, 255, 0], [0, 255, 0]]])
img = sc.carveSeam(img, 1, 3)
print(img)

# img = img.resize((300, 300))
# img.save(r"C:\users\sunny\OneDrive\Desktop\ImageEditor\test.png")
