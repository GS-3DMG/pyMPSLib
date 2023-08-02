class Coords:

    def __init__(self, x, y, z, value=0):
        self.x = x
        self.y = y
        self.z = z
        self.value = value

    def setXIndex(self, x):
        self.x = x

    def setYIndex(self, y):
        self.y = y

    def setZIndex(self, z):
        self.z = z

    def setValue(self, v):
        self.value = v

    def getXIndex(self):
        return self.x

    def getYIndex(self):
        return self.y

    def getZIndex(self):
        return self.z

    def getValue(self):
        return self.value

    def getIndex(self):
        return self.x, self.y, self.z

    def coords2String(self):
        return str(self.x) + " " + str(self.y) + " " + str(self.z) + " " + str(self.value)
