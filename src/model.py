import copy
from PIL import Image, ImageFilter, ImageOps
import random as rand
import numpy as np
from utils import getDistance


class GUIEditorModel:
    """
    Represents a GUI model that contains an array of editable images.
    For the array, the first image will be the topmost in the project, and the last image will be the bottommost
    """

    def __init__(self, *images):
        self.layers = []
        self.visibilityIdentifiers = []
        self.currentLayer = -1
        if len(images) > 0:
            self.height = images[0].height
            self.width = images[0].width
            for image in images:
                """Add checkImageRect method"""
                if image.height != self.height or image.width != self.width:
                    raise ValueError("Images must have the same dimensions")
                self.layers.append(image)
                self.visibilityIdentifiers.append(True)
                self.currentLayer += 1

    def getSize(self):
        """
        Returns
        ============ 
        tuple representing the width and the height of the images in the current project.
        (defaults to 512 pixels)
        """
        if not (self.width and self.height):
            self.width = self.height = 512
        return self.width, self.height

    def getAllImages(self):
        """
        Returns
        ============ 
        deep copy of all the images in this model, in the same order.
        """
        ans = []
        for image in self.layers:
            ans.append(copy.deepcopy(image))
        return ans

    def getImageAt(self, index):
        """
        Returns
        ============ 
        deep copy of the image at the given index in this model.
        """
        return copy.deepcopy(self.layers[index])

    def getTopMost(self):
        """
        Returns
        ============ 
        deep copy of the topmost visible image in this model.
        """
        for i in range(len(self.layers)):
            if self.visibilityIdentifiers[i]:
                return self.getImageAt(i), i

    def getDisplayImage(self):
        """
        Returns
        ============
        merges the current images in the model into a single image to be displayed in the GUI
        """
        if not self.layers:
            return 
        # set placeholder background
        background = Image.new(mode="RGBA", size=(self.width, self.height), color=(255, 255, 255, 0)) 
        for i in range(len(self.layers), 0, -1):
            if self.visibilityIdentifiers[i-1]:
                foreground = self.getImageAt(i-1)
                background.paste(foreground, (0, 0), foreground.convert('RGBA'))
        return background

    def getLayerVisibility(self):
        """
        Returns
        ============ 
        deep copy of the layer visiblity list
        """
        return copy.deepcopy(self.visibilityIdentifiers)

    def addImage(self, image):
        """
        Adds the given image to this model above the current selected layer.
        """
        if len(self.layers) == 0 or image.height == self.height or image.width == self.width:
            if len(self.layers) == 0:
                self.height = len(image)
                self.width = len(image[0])
            self.layers.insert(self.currentLayer, copy.deepcopy(image))
            self.visibilityIdentifiers.insert(self.currentLayer, True)
        else:
            raise ValueError("Images must have the same dimensions")

    def removeImage(self):
        """
        Removes the selected image layer from the list of image layers.
        """
        if self.currentLayer == -1:
            return
        else:
            del self.layers[self.currentLayer]
            del self.visibilityIdentifiers[self.currentLayer]
            self.currentLayer -= 1

    def removeAllImages(self):
        """
        Removes all the images from this model above
        """
        self.layers.clear()
        self.visibilityIdentifiers.clear()
        self.currentLayer = -1

    def moveLayer(self, start, end):
        """
        Moves the image current at the given start index to the given end index
        """
        self.layers.insert(end, self.layers.pop(start))

    def selectLayer(self, index):
        """
        Parameters
        ============ 
        index:
            integer representing the index of the image layer in the model
        
        Selects the given image layer to manipulate
        """
        if index > len(self.layers) or index < 0:
            raise ValueError("Index out of bounds")
        self.currentLayer = index

    def changeVisibility(self):
        """
        Flips the visibility of this model's selected layer.
        """
        self.visibilityIdentifiers[self.currentLayer] = not self.visibilityIdentifiers[self.currentLayer]

    def grayscale(self):
        """
        Grayscales the model's selected layer.
        """
        self.layers[self.currentLayer] = ImageOps.grayscale(
            self.layers[self.currentLayer])

    def sepia(self):
        """
        Applies a sepia filter to this model's selected layer.
        """
        # https://stackoverflow.com/questions/36434905/processing-an-image-to-sepia-tone-in-python
        img = self.getImageAt(self.currentLayer)
        ansImg = np.array(self.getImageAt(self.currentLayer))
        for i in range(self.height):
            for j in range(self.width):
                r, g, b = img.getpixel((j, i))
                newR = int(0.393 * r + 0.769 * g + 0.189 * b)
                newG = int(0.349 * r + 0.686 * g + 0.168 * b)
                newB = int(0.272 * r + 0.534 * g + 0.131 * b)

                if newR > 255:
                    newR = 255
                if newR < 0:
                    newR = 0
                if newG > 255:
                    newG = 255
                if newG < 0:
                    newG = 0
                if newB > 255:
                    newB = 255
                if newB < 0:
                    newB = 0
                ansImg[i, j] = (newR, newG, newB)
        self.layers[self.currentLayer] = Image.fromarray(ansImg)

    def blur(self):
        """
        Blurs this model's selected layer.
        """
        self.layers[self.currentLayer] = self.layers[self.currentLayer].filter(
            ImageFilter.BLUR)

    def sharpen(self):
        """
        Sharpens this model's selected layer.
        """
        self.layers[self.currentLayer] = self.layers[self.currentLayer].filter(
            ImageFilter.SHARPEN)

    def downscale(self, targetHeight, targetWidth):
        """
        Parameters:
        ============ 
        targetHeight:
            the height (in pixels) that the images will be after the downsize
        targetWidth:
            the width (in pixels) that the images will be after the downsize
        
        Downscales the layers in this model to the targetWidth and targetHeight.
        """
        if targetHeight < 0 or targetHeight > self.height or targetWidth < 0 or targetWidth > self.width:
            raise ValueError("At least one target is invalid")
        self.height = targetHeight
        self.width = targetWidth
        for i in range(len(self.layers)):
            self.layers[i] = self.getImageAt(i).resize((targetWidth, targetHeight))

    def mosaic(self, numSeeds):
        """
        Applies a mosaic filter to this model's selected layer.
        """
        img = np.array(self.layers[self.currentLayer])
        seeds = self.getSeeds(numSeeds)
        clusters = self.getClusters(seeds)
        avgRGB = self.getAvgRGB(clusters, seeds, img)

        ansImg = np.array(self.getImageAt(self.currentLayer))
        for i in range(self.height):
            for j in range(self.width):
                cluster = clusters[j, i]
                rgb = avgRGB[cluster]
                ansImg[j, i] = (rgb[0], rgb[1], rgb[2])
        self.layers[self.currentLayer] = Image.fromarray(ansImg)

    def getAvgRGB(self, clusters, seeds, image):
        """
        Parameters:
        ============ 
        clusters:
            2-D numpy array of integers that represents the cluster number of the corresponding pixel
        seeds:
            List of tuples that represent the posns of the pixel seeds in the image
        image:
            PIL image that will be mosaic-ed
        
        Returns:
        ============ 
        Dictionary that maps each cluster to the to the average color of that cluster.
        """
        averages = {}
        clusterColors = np.zeros((len(seeds), 3))

        for sdIndex in range(len(seeds)):
            totalPixels = 0
            for i in range(self.height):
                for j in range(self.width):
                    if clusters[j, i] == sdIndex:
                        r, g, b = image[j, i, 0], image[j, i, 1], image[j, i, 2]
                        clusterColors[sdIndex, 0] += r
                        clusterColors[sdIndex, 1] += g
                        clusterColors[sdIndex, 2] += b
                        totalPixels += 1
            avgR = clusterColors[sdIndex, 0] // totalPixels
            avgG = clusterColors[sdIndex, 1] // totalPixels
            avgB = clusterColors[sdIndex, 2] // totalPixels
            averages[sdIndex] = (avgR, avgG, avgB)
        return averages

    def getClusters(self, seeds):
        """
        Parameters:
        ============ 
        seeds:
            list of tuples that represent the positions of the seeds in the form (x, y)
        image:
            PIL image that will used to generate the seeds
        
        Returns:
        ============ 
        Double array of integers that represents the seed that each corresponding pixel is closest to.
        """
        clusters = np.zeros((self.height, self.width))
        for i in range(self.height):
            for j in range(self.width):
                currPosn = (j, i)
                cluster = 0
                minDist = getDistance(currPosn, seeds[0])

                for k in range(len(seeds)):
                    tempDist = getDistance(currPosn, seeds[k])
                    if tempDist < minDist:
                        minDist = tempDist
                        cluster = k
                clusters[j, i] = cluster
        return clusters

    def getSeeds(self, numSeeds):
        """
        Parameters:
        ============ 
        numSeeds:
            the number of seeds that will be generated

        Returns:
        ============ 
        List of tuples representing the position of each seed in the model's selected image
        """
        seeds = []
        found = 0
        while found < numSeeds:
            posn = (rand.randrange(self.width), rand.randrange(self.height))
            if not posn in seeds:
                seeds.append(posn)
                found += 1
        return seeds
        
    
    def verticalFlip(self):
        """
        Flips the current image vertically
        """
        self.layers[self.currentLayer] = self.getImageAt(self.currentLayer).transpose(Image.FLIP_TOP_BOTTOM)
    
    def horizontalFlip(self):
        """
        Flips the current image horizontally
        """
        self.layers[self.currentLayer] = self.getImageAt(self.currentLayer).transpose(Image.FLIP_LEFT_RIGHT)

    def rotateAll90(self):
        """
        Rotates all images by 90 degress counterclockwise
        """
        for i in range(len(self.layers)):
            self.layers[i] = self.getImageAt(i).rotate(90)
        temp = self.width
        self.width = self.height
        self.height = temp


