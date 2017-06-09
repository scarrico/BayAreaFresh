import cv2
import numpy as np
from PIL import Image
import pytesseract
from logging import FileHandler
import logging
# Required patch on __init__.py
# Added .decode() to line with base64 print
# Left message on github.
from vlogging import VisualRecord


class arrayImage(object):
    def __init__(self, showImages=True, printImages=True):
        # Include security and date, security and timeframe
        self.topMargin4Date = 0
        # Bottom of data, security, and timeframe
        self.bottomMargin4Date = 130
        self.topMargin4Array = 330
        self.bottomMargin4Array = 840
        self.leftMargin = 0  # For entire array
        self.leftMargin4JustBars = 210
        self.leftMargin = self.leftMargin4JustBars
        self.leftMargin = 20 # Want left labels now
        self.rightMargin = 750
        self.imageLoc = ""

    def readArray(self, loc, printFile="imgReadIn.png"):
        self.imageLoc = loc
        self.image = cv2.imread(loc)
        return self.image

    def image2Gray(self, img, printFile="grayTransform.png"):
        self.grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return self.grayImage

    def cropArray(self, img):
        return img[self.topMargin4Array:self.bottomMargin4Array,
                   self.leftMargin:self.rightMargin]

    def cropDateInfo(self, img):
        return img[self.topMargin4Date:self.bottomMargin4Date,
                   self.leftMargin:self.rightMargin]

    def segmentWithThreshold(self, img):
        ret, thresh = cv2.threshold(img, 0, 255,
                                    cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
        return thresh

    # Produces outline of bars
    def segmentWithCanny(self, img):
        edges = cv2.Canny(img, 100, 200)
        return edges

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    @property
    def grayImage(self):
        return self._grayImage

    @grayImage.setter
    def grayImage(self, value):
        self._grayImage = value


# BEGIN Set up debugging system
logger = logging.getLogger("demo")
fh = FileHandler('test.html', mode="w")
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)
# END Set up debugging system

arrayDaily = arrayImage()
imageLoc = "../arrays/daily/Dow/array/daily-Dow-array-2017-05-30-20.27.08.png"
img = arrayDaily.readArray(imageLoc)
logger.debug(VisualRecord("Original Image", img, "End image"))
grayImg = arrayDaily.image2Gray(arrayDaily.image)
logger.debug(VisualRecord("gray Image", grayImg, "End image"))
croppedArray = arrayDaily.cropArray(grayImg)
logger.debug(VisualRecord("cropped gray Image", croppedArray, "End image"))
thresh = arrayDaily.segmentWithThreshold(croppedArray)
logger.debug(VisualRecord("cropped gray Image", thresh, "End image"))
res = cv2.resize(croppedArray,None,fx=2, fy=2, interpolation = cv2.INTER_CUBIC)

img = Image.fromarray(res)
logger.debug(VisualRecord("Tesseract Input", img, "End image"))
txt = pytesseract.image_to_string(img)
print(txt)
