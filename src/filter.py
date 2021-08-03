from abc import ABC, abstractmethod
from model import Pixel
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFilter

class Filter(ABC):
    """Represents a filter that can be applied to an image represented by a 2D array of pixels"""
    @abstractmethod
    def apply(self, image):
        pass
    
class ColorFilter(Filter):
    
    def __init__(self, matrix):
        if (len(matrix) != 3 or len(matrix[0]) != 3 or len(matrix[1]) != 3 or len(matrix[2]) != 3):
            raise ValueError("Given color matrix is invalid, must be a 3 x 3")
        self.colorMatrix = matrix
    
    def apply(self, image):
        """Check if image is rectangular"""
        height = len(image)
        width = len(image[0])
        newImage = []
        for i in range(height):
            for j in range(width):
                pixel = image[i][j]
                newRGB = np.multiply(np.array(self.colorMatrix), np.array([[pixel.r], [pixel.g], [pixel.b]]))
                for k in range(3):
                    if newRGB[k] > 255:
                        newRGB[k] = 255
                    if newRGB[k] < 0:
                        newRGB[k] = 0
                newImage[i][j] = Pixel(newRGB[0][0], newRGB[1][0], newRGB[2][0])
        return newImage
        

class ResFilter(Filter):
    def __init__(self, matrix):
        size = len(matrix)
        for row in matrix:
            if len(row) != size:
                raise ValueError("Matrix must be a square")
        self.kernel = matrix
        self.size = size
        
    def apply(self, image):
        height = len(image)
        width = len(image[0])
        ansImg = []
        for i in range(height):
            ansImg.append([])
            for j in range(width):
                pMatrix = [] #Use utils class to get matrix here
                rMatrix = []
                gMatrix = []
                bMatrix = []
                for x in range(self.size):
                    rMatrix.append([])
                    gMatrix.append([])
                    bMatrix.append([])
                    for y in range(self.size):
                        rMatrix[x].append(pMatrix[x][y].r)
                        gMatrix[x].append(pMatrix[x][y].g)
                        bMatrix[x].append(pMatrix[x][y].b)
                newRGB = []
                for k in range(3):
                    if newRGB[k] > 255:
                        newRGB[k] = 255
                    if newRGB[k] < 0:
                        newRGB[k] = 0
                ansImg[i].append(Pixel(newRGB[0], newRGB[1], newRGB[2]))
    
    def grayscale(image):
        return image.convert('LA')
