import cv2
import numpy as np
from PIL import Image
from tesserocr import PyTessBaseAPI, RIL

from logging import FileHandler
import logging
# vlogging required patch in __init__.py
# Added .decode() to line with base64 print
# Left message on github.
from vlogging import VisualRecord


class arrayImage(object):
    def __init__(self, showImages=True, printImages=True):
        # Include security and date, security and timeframe
        scale = 1.5
        self.topMargin4Date = int(round(0*scale))
        # Bottom of data, security, and timeframe
        self.bottomMargin4Date = int(round(130*scale))
        self.topMargin4Array = int(round(330*scale))
        self.bottomMargin4Array = int(round(840*scale))
        self.leftMargin = 0 * scale  # For entire array
        self.leftMargin4JustBars = int(round(210*scale))
        self.leftMargin = self.leftMargin4JustBars
        self.leftMargin = int(round(20*scale))  # Want left labels now
        self.rightMargin = int(round(750*scale))
        self.rightMarginWords = int(round(240*scale))
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

    def cropWords(self, img):
        return img[self.topMargin4Array:self.bottomMargin4Array,
                   self.leftMargin:self.rightMarginWords]

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
img = cv2.resize(img, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
logger.debug(VisualRecord("Original Image", img, "End image"))
grayImg = arrayDaily.image2Gray(img)
(thresh, im_bw) = cv2.threshold(grayImg, 128, 255,
                                cv2.THRESH_BINARY | cv2.THRESH_OTSU)

logger.debug(VisualRecord("b and w Image", im_bw, "End image"))
croppedArray = arrayDaily.cropArray(im_bw)
croppedArray = arrayDaily.cropWords(im_bw)
logger.debug(VisualRecord("cropped gray Image", croppedArray, "End image"))
thresh = arrayDaily.segmentWithThreshold(croppedArray)
logger.debug(VisualRecord("cropped gray Image", thresh, "End image"))

img = Image.fromarray(thresh)
logger.debug(VisualRecord("Tesseract Input", img, "End image"))
with PyTessBaseAPI() as api:
    api.SetImage(img)
    boxes = api.GetComponentImages(RIL.TEXTLINE, True)
    for i, (im, box, _, _) in enumerate(boxes):
        api.SetRectangle(box['x'], box['y'], box['w'], box['h'])
        ocrResult = api.GetUTF8Text()
        conf = api.MeanTextConf()
        print(ocrResult)
        print(repr(box))
