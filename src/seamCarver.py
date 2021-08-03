import numpy as np
from PIL import Image
from matplotlib import cm


class SeamInfo:

    def __init__(self, weight, posn):
        self.weight = weight
        self.pixels = [posn]

    def add(self, weight, posn):
        self.weight += weight
        self.pixels.append(posn)


def getEnergyMap(image):
    """creates a map of the energies of each pixel"""
    width, height = image.size
    map = []
    for i in range(height):
        map.append([])
        for j in range(width):
            tl, t, tr, l, r, dl, d, dr = getNeighbors(image, j, i)
            map[i].append(getEnergy(tl, t, tr, l, r, dl, d, dr))
    return np.array(map)


def getEnergy(tl, t, tr, l, r, dl, d, dr):
    """helper for getEnergyMap that returns the energy of a single pixel given its neighbors"""
    vertEnergy = tl + 2 * t + tr - dl - 2 * d - dr
    horizEnergy = tl + 2 * l + dl - tr - 2 * r - dr
    return (vertEnergy ** 2 + horizEnergy ** 2) ** 0.5


def getNeighbors(image, x, y):
    """helper for getEnergyMap that gets the neighbors of the pixel at the given x y position in the image"""
    width, height = image.size
    tl, t, tr, l, r, dl, d, dr = (0, 0, 0, 0, 0, 0, 0, 0)
    if y != 0:
        t = getBrightness(image.getpixel((x, y - 1)))
        if x != 0:
            tl = getBrightness(image.getpixel((x - 1, y - 1)))
        if x != width - 1:
            tr = getBrightness(image.getpixel((x + 1, y - 1)))
    if y != height - 1:
        d = getBrightness(image.getpixel((x, y + 1)))
        if x != 0:
            dl = getBrightness(image.getpixel((x - 1, y + 1)))
        if x != width - 1:
            dr = getBrightness(image.getpixel((x + 1, y + 1)))
    if x != 0:
        l = getBrightness(image.getpixel((x - 1, y)))
    if x != width - 1:
        r = getBrightness(image.getpixel((x + 1, y)))
    return tl, t, tr, l, r, dl, d, dr


def getBrightness(rgb):
    """helper for getNeighbors that returns the brightness as the average of the given rgb values"""
    return (rgb[0] + rgb[1] + rgb[2]) / 765

def findLowestSeam(image, dir):
    # if dir is true, finds lowest vertical seam, else finds lowest horizontal seam
    seams = []
    energyMap = getEnergyMap(image)
    height = energyMap.shape[0]
    width = energyMap.shape[1]
    if (dir):
        for i in range(width):
            seams.append(SeamInfo(energyMap[0][i], i))
        for i in range(height - 1):
            for j in range(width):
                weight, posn = findLowestEnergyVert(energyMap, (i, j))
                seams[j].add(weight, posn[0])
    else:
        for i in range(height):
            seams.append(SeamInfo(energyMap[i][0], i))
        for i in range(width - 1):
            for j in range(height):
                weight, posn = findLowestEnergyHoriz(energyMap, (i, j))
                seams[j].add(weight, posn[1])
    weights = [seam.weight for seam in seams]
    return seams[weights.index(min(weights))].pixels

def findLowestEnergyVert(energyMap, posn):
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

def findLowestEnergyHoriz(energyMap, posn):
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

def removeSeam(image, seam):
    arrayImg = np.array(image)
    grid = arrayImg.tolist()
    posns = seam.pixels
    for i in range(len(seam.pixels)):
        grid[i].pop(posns[i][1])
    arrayImg = np.array(grid)
    # return Image.fromarray(arrayImg)
    return arrayImg

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
    result = np.delete(image, seam, axis=0)  #.reshape(shape)
    return Image.fromarray(result.astype(np.uint8))