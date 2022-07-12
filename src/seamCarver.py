from operator import attrgetter
import numpy as np
from PIL import Image
from matplotlib import cm
import random as rand


class SeamInfo:

    def __init__(self, weight, posns):
        self.weight = weight
        self.pixels = posns


def getEnergyMap(image):
    """creates a map of the energies of each pixel
    The outer array in the map represents the y coordinates (rows)"""
    shape = image.shape
    map = []
    for i in range(shape[0]):
        map.append([])
        for j in range(shape[1]):
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
    shape = image.shape
    tl, t, tr, l, r, dl, d, dr = (0, 0, 0, 0, 0, 0, 0, 0)
    if y != 0:
        t = getBrightness(image[y - 1][x])
        if x != 0:
            tl = getBrightness(image[y - 1][x - 1])
        if x != shape[1] - 1:
            tr = getBrightness(image[y - 1][x + 1])
    if y != shape[0] - 1:
        d = getBrightness(image[y + 1][x])
        if x != 0:
            dl = getBrightness(image[y + 1][x - 1])
        if x != shape[1] - 1:
            dr = getBrightness(image[y + 1][x + 1])
    if x != 0:
        l = getBrightness(image[y][x - 1])
    if x != shape[1] - 1:
        r = getBrightness(image[y][x + 1])
    return tl, t, tr, l, r, dl, d, dr


def getBrightness(rgb):
    """helper for getNeighbors that returns the brightness as the average of the given rgb values"""
    return (int(rgb[0]) + int(rgb[1]) + int(rgb[2])) / 765


def findLowestSeam(image, dir):
    # if dir is true, finds lowest vertical seam, else finds lowest horizontal seam
    seams = []
    energyMap = getEnergyMap(image)
    shape = energyMap.shape
    if (dir):
        for i in range(shape[1]):
            seams.append(SeamInfo(energyMap[0][i], [i]))
        for j in range(1, shape[0]):
            newSeams = []
            for i in range(shape[1]):
                newSeams.append(createNewVerticalSeam(seams, (i, j), energyMap[j][i]))
            seams = newSeams
    else:
        for j in range(shape[0]):
            seams.append(SeamInfo(energyMap[j][0], [j]))
        for i in range(1, shape[1]):
            newSeams = []
            for j in range(shape[0]):
                newSeams.append(createNewHorizontalSeam(seams, (i, j), energyMap[j][i]))
            seams = newSeams
    return min(seams, key=attrgetter('weight'))

def createNewVerticalSeam(seams, posn, weight):
    neighborSeams = [float('inf'), seams[posn[0]].weight, float('inf')]
    if (posn[0] != 0):
        neighborSeams[0] = seams[posn[0] - 1].weight
    if (posn[0] != len(seams) - 1):
        neighborSeams[2] = seams[posn[0] + 1].weight
    minValue = min(neighborSeams)
    minIndex = neighborSeams.index(minValue)
    prevSeam = seams[posn[0] - 1 + minIndex]
    newPixelList = [] 
    newPixelList.extend(prevSeam.pixels)
    newPixelList.append(posn[0])
    return SeamInfo(prevSeam.weight + weight, newPixelList)

def createNewHorizontalSeam(seams, posn, weight):
    neighborSeams = [float('inf'), seams[posn[1]].weight, float('inf')]
    if (posn[1] != 0):
        neighborSeams[0] = seams[posn[1] - 1].weight
    if (posn[1] < len(seams) - 1):
        neighborSeams[2] = seams[posn[1] + 1].weight
    minValue = min(neighborSeams)
    minIndex = neighborSeams.index(minValue)
    prevSeam = seams[posn[1] - 1 + minIndex]
    newPixelList = [] 
    newPixelList.extend(prevSeam.pixels)
    newPixelList.append(posn[1])
    return SeamInfo(prevSeam.weight + weight, newPixelList)

    
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


def removeSeam(image, seam, axis=1):
    shape = image.shape
    mask = np.ones((shape[0], shape[1]), bool)

# 0 means horizontal
    if (axis == 1):
        for i in range (len(seam.pixels)):
            mask[i, seam.pixels[i]] = False
        newImage = image[mask].reshape(shape[0], shape[1] - 1, shape[2])

    else:
        for i in range (len(seam.pixels)):
            mask[seam.pixels[i], i] = False
        newImage = image[mask].reshape(shape[0] - 1, shape[1], shape[2])

    return newImage


def carveSeam(image, targetWidth, targetHeight):
    import time

    image = np.array(image)
    shape = list(image.shape)
    start = time.time()
    while shape[1] > targetWidth and shape[0] > targetHeight:
        r = rand.randint(0, 1)
        seam = findLowestSeam(image, r)
        image = removeSeam(image, seam, r)
        shape = list(image.shape)
    while shape[1] > targetWidth:
        c = time.time()
        print(c - start)
        start = c
        seam = findLowestSeam(image, 1)
        c = time.time()
        print('find: ', c - start)
        start = c
        image = removeSeam(image, seam, 1)
        c = time.time()
        print('remove: ', c - start)
        start = c
        shape = list(image.shape)
    while shape[0] > targetHeight:
        seam = findLowestSeam(image, 0)
        image = removeSeam(image, seam, 0)
        shape = list(image.shape)
    return image
    # return Image.fromarray(image.astype(np.uint8))
