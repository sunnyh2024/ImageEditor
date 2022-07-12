from PIL import Image
import model
import seamCarver as sc
import numpy as np
import random as rand

img = Image.open(r"C:\users\sunny\OneDrive\Desktop\ImageEditor\tower.png")
img = sc.carveSeam(img, 780, 542)
toSave = Image.fromarray(img)
toSave.save(r"C:\users\sunny\OneDrive\Desktop\ImageEditor\amongusCarved.png")
print(toSave.size)

# img = np.array([[[255, 255, 0], [0, 255, 0], [0, 255, 255]], 
# [[0, 255, 0], [255, 0, 255], [255, 0, 0]], 
# [[0, 255, 255], [255, 255, 0], [0, 255, 0]]])
# img = sc.carveSeam(img, 1, 3)
# print(img)

# img = img.resize((300, 300))
# img.save(r"C:\users\sunny\OneDrive\Desktop\ImageEditor\test.png")
