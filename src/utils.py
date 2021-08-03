
def getDistance(posn1, posn2):
    """Helper for getSeeds that calculates the cartesian distance between two tuple points."""
    distX = (posn1[0] - posn2[0]) ** 2
    distY = (posn1[1] - posn2[1]) ** 2
    return (distX + distY) ** 0.5