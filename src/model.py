import copy


class GUIEditorModel:
    """Represents a GUI model that contains an array of editable images."""

    def __init__(self, *images):
        self.layers = []
        self.visibilityIdentifiers = []
        self.currentLayer = -1
        if len(images) > 0:
            self.height = len(images[0])
            self.width = len(images[0][0])
            for image in images:
                """Add checkImageRect method"""
                if len(image) != self.height or len(image[0]) != self.width:
                    raise ValueError("Images must have the same dimensions")
                self.layers.append(image)
                self.visibilityIdentifiers.append(True)
                self.currentLayer += 1

    def getAllImages(self):
        """
        Returns
        ============
            deep copy of all the images in this model, in the same order as the model.
        """
        ans = []
        for image in self.layers:
            ans.append(copy.deepcopy(image))

    def getImageAt(self, index):
        """
        Returns
        ============ 
            deep copy of the image at the given index in this model.
        """
        return copy.deepcopy(self.layers[index])

    def getTopMost(self):
        """Returns a deep copy of the topmost visible image in this model."""
        for i in range(len(self.layers), 0, -1):
            if self.visibilityIdentifiers[i]:
                return self.getImageAt(i)

    def getLayerVisibility(self):
        """
        Returns 
        ============ 
            deep copy of the layer visiblity list
        """
        return copy.deepcopy(self.visibilityIdentifiers)

    def addImage(self, image):
        """
        Parameters
        ============ 
        image:
            image in the PIL RGB format

        Adds the given image to this model above the current selected layer.
        """
        if len(self.layers) == 0 or len(image) == self.height or len(image[0]) == self.width:
            if len(self.layers) == 0:
                self.height = len(image)
                self.width = len(image[0])
            self.layers.insert(self.currentLayer + 1, copy.deepcopy(image))
            self.visibilityIdentifiers.insert(self.currentLayer + 1, True)
            self.currentLayer += 1
        else:
            raise ValueError("Images must have the same dimensions")

    def removeImage(self):
        """Removes the selected image layer from the list of image layers"""
        if self.currentLayer == -1:
            return
        else:
            self.layers.remove(self.currentLayer)
            self.currentLayer -= 1

    def selectLayer(self, index):
        """Selects an image layer to manipulate"""
        if index > len(self.layers) or index < 0:
            raise ValueError("Index out of bounds")
        self.currentLayer = index

    def changeVisibility(self):
        """Flips the visibility of this model's selected layer."""
        self.visibilityIdentifiers[self.currentLayer] = not self.visibilityIdentifiers[self.currentLayer]


class Pixel:
    """Represents a pixel in an image with the given RGB values."""

    def __init__(self, r, g, b):
        if (r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255):
            raise ValueError(
                "At least one of the given values is not a valid color value")
        self.r = r
        self.g = g
        self.b = b

    def __eq__(self, other):
        """Returns whether the given other pixel is the same color as self"""
        if type(other) != Pixel:
            return False
        return self.r == other.r and self.g == other.g and self.b == other.b

    def __hash__(self):
        """returns the hashcode of self"""
        return hash(self.r, self.g, self.b)

# def checkImageRect(image):
#     if len(image) == 0 or len(image[0] == 0):
#         raise ValueError("Given image is empty")
#     firstRowSize = len(image[0])

#     for row in image:
#         if len(row) != firstRowSize:
#             raise ValueError("Given image is not rectangular")
#         for pixel in row:
#             if pixel == null:

