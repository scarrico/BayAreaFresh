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
        self.scale = 2
        # Include security and date, security and timeframe
        self.topMargin4Date = int(round(0*self.scale))
        # Bottom of data, security, and timeframe
        self.bottomMargin4Date = int(round(130*self.scale))
        self.topMargin4Array = int(round(330*self.scale))
        self.bottomMargin4Array = int(round(840*self.scale))
        self.leftMargin = 0 * self.scale  # For entire array
        self.leftMargin4JustBars = int(round(210*self.scale))
        self.leftMargin = self.leftMargin4JustBars
        self.leftMargin = int(round(20*self.scale))  # Want left labels now
        self.rightMargin = int(round(750*self.scale))
        self.rightMarginWords = int(round(240*self.scale))
        self.imageLoc = ""
        # whiteList = list(ascii_letters + digits)
        self.whiteList = ""
        gen = (i for j in (range(ord('a'), ord('z')+1),
                           range(ord('A'), ord('Z')+1),
                           range(ord('0'), ord('9')+1)) for i in j)
        
        for i in gen:
            self.whiteList = self.whiteList+chr(i)
        self.whiteList = self.whiteList+chr(ord('-'))
        
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
        
    def cleanImage(self, img):
        # INTER_LANCZOS4 is Similar to INTER_CUBIC
        # Magnify
        img = cv2.resize(img, None, fx=self.scale, fy=self.scale,
                         interpolation=cv2.INTER_CUBIC)
        logger.debug(VisualRecord("Original Image", img, "End image"))
        # b&w for better recognition
        grayImg = arrayDaily.image2Gray(img)
        (thresh, im_bw) = cv2.threshold(grayImg, 128, 255,
                                        cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        thresh = arrayDaily.segmentWithThreshold(im_bw)
        # Sharpen
        blur = cv2.GaussianBlur(thresh, (1, 1), 0)
        sharp = blur.copy()
        alpha = 0.5
        alpha = 1.5
        gamma = 0.2
        gamma = 0
        cv2.addWeighted(blur, alpha, sharp, 1-alpha, gamma, sharp)
        # Denoise
        clean = sharp.copy()
        cv2.fastNlMeansDenoising(sharp, clean, 55, 5, 21)
        return(clean)

    def OcrSegment(self, sharp):
        # Given a (hopefully) sharpened image, ocr the segment
        img = Image.fromarray(sharp)
        logger.debug(VisualRecord("Tesseract Input", img, "End image"))
        # Read off the labels one at a time.  Need a margin
        # since otherwise the cropping is too close for tesseract.
        with PyTessBaseAPI() as api:
            # api.Init(".","eng",tesseract.OEM_DEFAULT)
            api.SetVariable("tessedit_char_whitelist", self.whiteList)
            api.SetImage(img)
            boxes = api.GetComponentImages(RIL.TEXTLINE, True)
            for i, (im, box, _, _) in enumerate(boxes):
                margin = 5
                api.SetRectangle(box['x'], box['y'],
                                 box['w']+margin, box['h']+margin)
                croppedSegment = sharp[box['y']:box['y']+box['h']+margin,
                                       box['x']:box['x']+box['w']+margin]
                ocrResult = api.GetUTF8Text()
                # Mean confidences
                conf = api.MeanTextConf()
                print("confidences: ", api.AllWordConfidences())
                print(ocrResult)
                tailPrint = "\n"+ocrResult+"end image"
                logger.debug(VisualRecord("ocrResult",
                                          croppedSegment, tailPrint))
                print(repr(box))

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
im_bw = arrayDaily.cleanImage(img)
sharp = arrayDaily.cropArray(im_bw)
arrayDaily.OcrSegment(sharp)
exit()
sharp = arrayDaily.cropWords(im_bw)
arrayDaily.OcrSegment(sharp)
