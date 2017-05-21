#!/Library/Frameworks/Python.framework/Versions/3.5/bin/python3

from subprocess import check_call
from random import randint
from time import sleep
from abc import ABC


class captureAgent (ABC):
    '''
    captureAgent uses applescript helper functions to automatically
    take pictures of parts of websites.

    The class that instantiates this abstract base class sets the various
    coordinates and sequece of operations.

    '''

    x = 0  # x coordinate offset of list
    y = 1  # 7 coordinate offset of list

    def __init__(self):
        '''
        Attributes:
        self.dirHelpers = '/usr/local/bin/
        self.dirTimePeriods = [self.dir1...self.dirn]
        self.filePrefixes = [self.filePrefix1...self.filePrefixn]
        self.url = "https://www.yahoo.com"
        self.openWindow = self.dirHelpers+"mkswindow.scrpt"
        self.argvalueWindow = self.url + " " + str(1200) + " " + str(1524)
        # Locations of interest:
        # These should be variables
        # There will be many coordinate variables
        self.BrowserLoc = [773, 45]  # as an example

        # Click stream to get to first snapshot
        # Uses various coordinate variables to create click stream
        self.getToFirst = [self.BrowserLoc]
        # Click stream to get to weekly array
        self.getToSecond = [self.BrowserLoc]
        self.getTimePeriods = [self.getToFirst, self.getToSecond]
        self.zeroBrowser = [self.HomeLoc]
        self.clickCmd = self.dirHelpers+"clickScreen.scrpt"
        self.snapshotCmd = self.dirHelpers+"screenshot.scrpt"
        self.activateCmd = self.dirHelpers+"activate.scrpt"
        '''

    def makeRandomWait(self, lowest, highest):
        if randint(0, 1) == 0:
            randomwait = randint(lowest, highest)+randint(2, 100)/100
            print("randomwait + : ", randomwait)
        else:
            randomwait = randint(highest, highest)-randint(2, 50)/100
            print("randomwait - : ", randomwait)
        sleep(randomwait)

    def createBrowserWindow(self):
        # Create window of appropriate size in known location
        check_call([self.openWindow, self.argvalueWindow])
        sleep(randint(2, 7))

    def setBrowserToZero(self):
        '''
        This is where we expect everything to start from
        '''
        for click in self.zeroBrowser:
            xClick = click[self.x]+randint(0, 5)
            yClick = click[self.y]+randint(0, 5)
            argvalue = str(xClick) + " " + str(yClick)
            print(self.clickCmd, argvalue)
            check_call([self.clickCmd, argvalue])

    def navigateToLocation(self, navLocationList):
        for click in navLocationList:
            self.makeRandomWait(7, 16)
            xClick = click[self.x]+randint(0, 5)
            yClick = click[self.y]+randint(0, 5)
            argvalue = str(xClick) + " " + str(yClick)
            print(self.clickCmd, argvalue)
            check_call([self.clickCmd, argvalue])

    def createSnapshot(self, dirName, filePrefix):
        '''
        Create the snapshot
        '''
        argvalue = self.dirArrays+dirName + " " + filePrefix + " "
        argvalue += str(self.ArrayTopLeftCap[0]) + " " + \
            str(self.ArrayTopLeftCap[1]) + " "
        argvalue += str(self.ArrayBottomRightCap[0]) + " " + \
            str(self.ArrayBottomRightCap[1])
        check_call([self.snapshotCmd, argvalue])

    def getSingleSnapshot(self, dirName, filePrefix):
        '''
        For debugging and one off runs.
        If your browser is at the right spot, just do a screenshot
        Snapshot relevant part of screen to dir, filename
        eg:
            ./% getSingleSnapshot directoryName/ filePrefix
        '''
        argvalue = ""
        check_call([self.activateCmd, argvalue])
        argvalue = self.dirArrays+dirName + " " + filePrefix + " "
        argvalue += str(self.ArrayTopLeftCap[0]) + " " + \
            str(self.ArrayTopLeftCap[1]) + " "
        argvalue += str(self.ArrayBottomRightCap[0]) + " " + \
            str(self.ArrayBottomRightCap[1])
        self.createSnapshot(dirName, filePrefix)

    def getAllSnapshots(self):
        '''
        Get to the right spot in the browser
        Snapshot relevant part of screen to dir, filename
            ./% getAllSnapshots
        '''
        for navList, dirName, filePrefix in \
                zip(self.getTimePeriods,
                    self.dirTimePeriods, self.filePrefixes):
                print(navList, dirName, filePrefix)
                self.navigateToLocation(navList)
                self.createSnapshot(dirName, filePrefix)

