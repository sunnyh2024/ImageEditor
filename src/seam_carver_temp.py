import numpy as np
from PIL import Image

def removeSeam(image, seam):
    """
    image: numpy array representing a PIL image
    seam: list of pixels represented as tuples in the form (x, y)
    returns a PIL image
    """
    grid = image.tolist()
    for i in range(len(seam)):
        grid[i].pop(seam[i][1])
    return Image.fromarray(np.array(grid))

example = np.array([
    [[255, 255, 255],
     [0,    0,    0],
     [255, 255, 255]],
    [[0,    0,    0],
     [255, 255, 255],
     [0,    0,    0]],
    [[255, 255, 255],
     [0,    0,    0],
     [255, 255, 255]]])
seam = [(0, 0), (1, 1), (0, 2)]

# NEW FUNCTION
def remove_seam(image, seam, axis=0):
    image = np.asanyarray(image)
    seam = np.asanyarray(seam)
    axis = np.core.multiarray.normalize_axis_index(axis, image.ndim)

    assert image.ndim == 3
    assert image.shape[-1] == 3
    assert axis in {0, 1}
    assert seam.size == image.shape[axis]

    shape = list(image.shape)
    seam = [seam, seam]
    seam[axis] = np.arange(image.shape[axis])
    seam = np.ravel_multi_index(seam, image.shape[:-1])
    image = image.reshape(-1, 3)
    shape[axis] -= 1
    result = np.delete(image, seam, axis=0).reshape(shape)
    return result

example = np.array([
    [[255, 255, 255], [0,    0,    0], [255, 255, 255]],
    [[0,    0,    0], [255, 255, 255], [0,    0,    0]],
    [[255, 255, 255], [0,    0,    0], [255, 255, 255]]])

# this seam should remove the top left, center, and bottom left pixels
seam = [0, 1, 0]

example = np.array(Image.open(r"C:\users\sunny\OneDrive\Desktop\ImageEditor\test.png"))

img = remove_seam(example, seam)
print(img)
img = (Image.fromarray(img.astype(np.uint8)))
img.show()