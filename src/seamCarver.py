import numpy as np
from PIL import Image
from matplotlib import cm
import random as rand


class SeamInfo:

    def __init__(self, weight, posn):
        self.weight = weight
        self.pixels = [posn]

    def add(self, weight, posn):
        self.weight += weight
        self.pixels.append(posn)


def getEnergyMap(image):
    """creates a map of the energies of each pixel
    The outer array in the map represents the x coordinates (columns)"""
    shape = image.shape
    map = []
    for i in range(shape[0]):
        map.append([])
        for j in range(shape[1]):
            tl, t, tr, l, r, dl, d, dr = getNeighbors(image, i, j)
            map[i].append(getEnergy(tl, t, tr, l, r, dl, d, dr))
    return np.array(map)


def getEnergy(tl, t, tr, l, r, dl, d, dr):
    """helper for getEnergyMap that returns the energy of a single pixel given its neighbors"""
    vertEnergy = tl + 2 * t + tr - dl - 2 * d - dr
    horizEnergy = tl + 2 * l + dl - tr - 2 * r - dr
    return (vertEnergy ** 2 + horizEnergy ** 2) ** 0.5


def getNeighbors(image, x, y):
    """helper for getEnergyMap that gets the neighbors of the pixel at the given x y position in the image"""
    shape = image.shape
    tl, t, tr, l, r, dl, d, dr = (0, 0, 0, 0, 0, 0, 0, 0)
    if y != 0:
        t = getBrightness(image[x][y - 1])
        if x != 0:
            tl = getBrightness(image[x - 1][y - 1])
        if x != shape[0] - 1:
            tr = getBrightness(image[x + 1][y - 1])
    if y != shape[1] - 1:
        d = getBrightness(image[x][y + 1])
        if x != 0:
            dl = getBrightness(image[x - 1][y + 1])
        if x != shape[0] - 1:
            dr = getBrightness(image[x + 1][y + 1])
    if x != 0:
        l = getBrightness(image[x - 1][y])
    if x != shape[0] - 1:
        r = getBrightness(image[x + 1][y])
    return tl, t, tr, l, r, dl, d, dr


def getBrightness(rgb):
    """helper for getNeighbors that returns the brightness as the average of the given rgb values"""
    return (rgb[0] + rgb[1] + rgb[2]) / 765


def findLowestSeam(image, dir):
    # if dir is true, finds lowest horizontal seam, else finds lowest vertical seam
    seams = []
    energyMap = getEnergyMap(image)
    shape = energyMap.shape
    if (dir):
        for j in range(shape[1]):
            seams.append(SeamInfo(energyMap[0][j], j))
        for i in range(shape[0] - 1):
            for j in range(shape[1]):
                weight, posn = findLowestEnergyHoriz(energyMap, (i, j))
                seams[j].add(weight, posn[1])
    else:
        for i in range(shape[0]):
            seams.append(SeamInfo(energyMap[i][0], i))
        for j in range(shape[1] - 1):
            for i in range(shape[0]):
                weight, posn = findLowestEnergyVert(energyMap, (i, j))
                seams[j].add(weight, posn[0])
    weights = [seam.weight for seam in seams]
    return seams[weights.index(min(weights))].pixels


def findLowestEnergyHoriz(energyMap, posn):
    i = posn[0]
    j = posn[1]
    nextEnergies = {}
    if j != 0:
        nextEnergies[energyMap[i + 1, j - 1]] = (j - 1, i + 1)
    if j != energyMap.shape[1] - 1:
        nextEnergies[energyMap[i + 1, j + 1]] = (j + 1, i + 1)
    nextEnergies[energyMap[i + 1, j]] = (j, i + 1)
    key = min(nextEnergies.keys())
    return key, nextEnergies[key]


def findLowestEnergyVert(energyMap, posn):
    i = posn[0]
    j = posn[1]
    nextEnergies = {}
    if i != 0:
        nextEnergies[energyMap[i - 1, j + 1]] = (j - 1, i + 1)
    if i != energyMap.shape[1] - 1:
        nextEnergies[energyMap[i + 1, j + 1]] = (j + 1, i + 1)
    nextEnergies[energyMap[i, j + 1]] = (j + 1, i)
    key = min(nextEnergies.keys())
    return key, nextEnergies[key]


def removeSeam(image, seam, axis=0):
    image = np.asanyarray(image)
    seam = np.asanyarray(seam)
    axis = np.core.multiarray.normalize_axis_index(axis, image.ndim)

    assert image.ndim == 3
    assert image.shape[-1] == 3
    assert axis in {0, 1}
    assert seam.size == image.shape[axis]

    shape = list(image.shape)
    if (axis == 0):
        seam = [list(range(len(seam))), seam]

    else:
        seam = [seam, list(range(len(seam)))]

    seam = np.ravel_multi_index(seam, (image.shape[:-1]))
    image = image.reshape(-1, 3)
    shape[axis] -= 1
    result = np.delete(image, seam, axis=0).reshape(shape)
    return result


def carveSeam(image, targetWidth, targetHeight):
    image = np.array(image)
    shape = list(image.shape)
    while shape[0] > targetWidth and shape[1] > targetHeight:
        r = rand.randint(0, 1)
        seam = findLowestSeam(image, r)
        image = removeSeam(image, seam, r)
        shape = list(image.shape)
    while shape[0] > targetWidth:
        seam = findLowestSeam(image, 0)
        image = removeSeam(image, seam, 0)
        shape = list(image.shape)
    while shape[1] > targetHeight:
        seam = findLowestSeam(image, 1)
        image = removeSeam(image, seam, 1)
        shape = list(image.shape)
    return Image.fromarray(image.astype(np.uint8))
