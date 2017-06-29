import cv2
import glob
import sys
import numpy as np
from PIL import Image
from tesserocr import PyTessBaseAPI, RIL
from difflib import SequenceMatcher as SM
import re
import datetime

from logging import FileHandler
import logging

sys.path.insert(0, '../utilities')
from nyseTradingDays import NYSE_tradingdays, NYSE_holidays
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
        self.arrayDict = {}   # representation of the array
        self.unclassified = "unclassified"
        self.timeUnit = "timeUnit"
        self.ensembleSegment = "ensembleSegment"
        self.unInteresting = "unInteresting"

    def readArray(self, loc, printFile="imgReadIn.png"):
        self.imageLoc = loc
        self.image = cv2.imread(loc)
        return self.image

    def image2Gray(self, img, printFile="grayTransform.png"):
        self.grayImage = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return self.grayImage

    # Will need generalized cropping function to accomidate
    # different image sources.  Use this simple code for now.
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
        # Note: didn't try bilateral filtering which might be good:
        # blur = cv2.bilateralFilter(img,9,75,75)
        #
        # INTER_LANCZOS4 is Similar to INTER_CUBIC
        # Magnify
        img = cv2.resize(img, None, fx=self.scale, fy=self.scale,
                         interpolation=cv2.INTER_CUBIC)
        # logger.debug(VisualRecord("Original Image", img, "End image"))
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

    def ocrSegment(self, sharp):
        print("input image sharp shape:", sharp.shape)
        maxY = sharp.shape[0] # Rows
        maxX = sharp.shape[1] # Columns
        # Given a (hopefully) sharpened image, ocr the segment
        img = Image.fromarray(sharp)
        # logger.debug(VisualRecord("Tesseract Input", img, "End image"))
        # Read off the labels one at a time.  Need a margin
        # since otherwise the cropping is too close for tesseract.
        with PyTessBaseAPI() as api:
            # api.Init(".","eng",OEM_DEFAULT)

            api.SetVariable("tessedit_char_whitelist", self.whiteList)
            api.SetImage(img)

            timg = api.GetThresholdedImage()
            logger.debug(VisualRecord("Tesseract's image ***", timg, "End image"))
            boxes = api.GetComponentImages(RIL.TEXTLINE, True)
            i = 0
            for i, (im, box, _, _) in enumerate(boxes):
                margin = 5
                api.SetRectangle(box['x'], box['y'],
                                 box['w']+margin, box['h']+margin)
                croppedSegment = sharp[box['y']:box['y']+box['h']+margin,
                                       box['x']:box['x']+box['w']+margin]
                ocrResult = api.GetUTF8Text()
                # Mean confidences
                conf = api.MeanTextConf()
                # print("confidences: ", api.AllWordConfidences())
                print(ocrResult)
                # print (dir(api.GetBoxText(0)))
                print("==>", self.classifyEntry(ocrResult))
                # Still need to split time units and aggregate
                # when necessary with date
                classOfLine = self.classifyEntry(ocrResult)
                # [classification of line, box info of text, box info, text,
                # coordinate which we use to find bar if relevant.]
                self.arrayDict[i] = [classOfLine, api.GetBoxText(0), box,
                                     ocrResult, 0]
                # split, find, etc defined for this.
                # print(api.GetBoxText(0)) # Letter coordinates

                tailPrint = "\n"+ocrResult+"end image"
                logger.debug(VisualRecord("ocrResult",
                                          croppedSegment, tailPrint))
                print(repr(box))
        self.fixDates()
        # print(self.arrayDict)

    def fixDates(self):
        # Heuristics wont work reliably.  Tesseract is too flaky.  
        # Create ML model instead. Fine example of replacing code
        # with ML.
        #
        # For now to test this out we will just take the first 
        # date month pair and then count out the number of slots
        # we find using the nyse trading days gist.
        #
        # Modify self.arrayDict so that dates and times are combined
        # if needed and then split into properly labeled single
        # entries.  Also add mid-point used to find the X axis
        # coordinate we follow to get the heights of bars.
        #
        # Get the locations of date related data
        timeUnitIndex = []
        dateUnitIndex = []
        theTimes = []
        theDates = []
        self.ocrStringIndex = 3
        tdays = list((NYSE_tradingdays(datetime.datetime(2017, 5,22), datetime.datetime(2017, 5, 22)+datetime.timedelta(days=11))))
        print (tdays)
        for line in self.arrayDict:
            if self.arrayDict[line][0] == self.dateUnit:
                dateUnitIndex.append(line)
            if self.arrayDict[line][0] == self.timeUnit:
                timeUnitIndex.append(line)
        if len(timeUnitIndex) > 0:
            for tu in timeUnitIndex:
                times = self.arrayDict[tu][self.ocrStringIndex].split()
                print(times)
                for t in times:
                    try:
                        theTimes.append(re.findall('[0-9]+', t)[0])
                    except IndexError as ie:
                        print ("index out of range")
                    except Exception as e:
                        print(e.args)
                        
            print("The Times:", theTimes)
        if len(dateUnitIndex) > 0:
            for d in dateUnitIndex:
                theDates = self.arrayDict[d][self.ocrStringIndex].split()
            print("The Dates:", theDates)
        # Simple case dates and times match
        if len(theDates) == len(theTimes):
            print("NOT TESTED: write code when dates and times match")
        elif len(theDates) > len(theTimes):
            print("NOT TESTED: write code when dates > times match")
        elif len(theDates) < len(theTimes):
            print("NOT TESTED: write code when number of dates < times ")
        print(timeUnitIndex)
        print(dateUnitIndex)

    def classifyEntry(self, ocrResult):
        # Simple heuristic based classifier
        self.unclassified = "unclassified"
        self.dateUnit = "dateUnit"
        self.timeUnit = "timeUnit"
        self.granularity = "grandularity"
        # So we can do i,j for height of bar chart
        # i = one of aggregate..overnightVol.
        # j = one of the time units, possibly a compound one
        # In the case of compound time, date and month are here.
        self.splitTimeUnit = "splitTimeUnit"
        self.ensembleSegment = "ensembleSegment"
        self.unInteresting = "unInteresting"
        self.aggregate = "Aggregate"
        self.transverse = "Transverse"
        self.empirical = "Empirical"
        self.longTerm = "Long Term"
        self.tradingCycle = "Trading Cycle"
        self.directionChange = "Direction Change"
        self.panicCycle = "Panic Cycle"
        self.internalVolatility = "Internal Volatility"
        self.overnightVolatility = "Overnight Volatility"
        self.daily = "DAILY FORECAST"
        self.weekly = "WEEKLY FORECAST"
        self.monthly = "MONTHLY FORECAST"
        self.quarterly = "QUARTERLY FORECAST"
        self.yearly = "YEARLY FORECAST"
        allGranularities = [self.daily, self.weekly, self.monthly,
                            self.quarterly, self.yearly]
        ensemble = [self.aggregate, self.transverse, self.longTerm,
                    self.empirical, self.tradingCycle,
                    self.directionChange, self.panicCycle,
                    self.panicCycle, self.internalVolatility,
                    self.overnightVolatility]
        self.timePeriods = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                            'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                            '2015', '2016', '2017', '2018', '2019',
                            '2020', '2021', '2022', '2023', '2024',
                            '2025', '2026', '2027', '2028', '2029',
                            '2030', '2031', '2032', '2033', '2034']
        countDateUnits = 0
        for t in self.timePeriods:
            countDateUnits += ocrResult.count(t)
        if countDateUnits > 10:
                return(self.dateUnit)
        for e in ensemble:
            if (SM(None, e, ocrResult).ratio() > .8):
                return(self.ensembleSegment)
        countNumbers = 0
        for n in range(1, 31):
            countNumbers += ocrResult.count(str(n))
        if countNumbers > 8:
            return(self.timeUnit)
        for g in allGranularities:
            if g in ocrResult:
                return(self.granularity)
        return(self.unclassified)

    def extractData(self, sharp, orig):
        pass
        # Ocr output to document representation
        # we need a numpy array for k-means, but the data
        # associated with an entry is rather complex and regular python
        # data structures would be convinient.  So we treat two structures
        # like two database tables with an id as a key between the two.
        # The numpy array is the height we will cluster on, id.
        # The python structure is a dict indexed by id and contains a list
        # of box, boxText.
        #
        # height of bar, color of bar, x, y, w, h, Text,
        #
        # classify document rows:
        # (array label, array indicator, timeUnit1, timeUnit2, miscText)
        # Get bar arrayLabel*(1..timeUnits)
        # Extract bar height in pixels
        # Build/Use bar height classifier 0..5, probably gaussian mixture model
        # K-means will probably work better
        # Represent array data and save

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


dirWithArrays = "../../arrays/daily/Dow/array/"
iteration = 0
# BEGIN Set up debugging system
logger = logging.getLogger("demo")
logFile = "../../bin/test"+str(iteration)+".html"
fh = FileHandler(logFile, mode="w")
logger.setLevel(logging.DEBUG)
logger.addHandler(fh)
# END Set up debugging system
# imageLoc = "../arrays/daily/Dow/array/daily-Dow-array-2017-05-30-20.27.08.png"
for imageLoc in glob.glob(dirWithArrays+"*.png"):
        print("processing file: ", imageLoc)
        arrayDaily = arrayImage()
        # imageLoc = "../arrays/daily/Dow/array/daily-Dow-array-2017-05-24-21.37.37.png"
        img = arrayDaily.readArray(imageLoc)
        im_bw = arrayDaily.cleanImage(img)
        arrayDaily.ocrSegment(im_bw)
        iteration += 1
        if iteration > 0:
            exit()
