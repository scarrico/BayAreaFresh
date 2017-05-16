#
# This script outlines  the basic funcationality needed to build
# an automatic scraper or other chrome automation function.  It solves
# several annoying problems with automator and appleScript and should save
# people a bunch of time.  It does not catch errors or implement other 
# bulletproofing.
# 
# It uses google.com for illustration.  
# Operations: 
#   Open chrome window of a certain size at position 0,0
#   Type something in 
#   Click somewhere on the screen
#   Screen shot just the window

set screenWidth to 1200
set screenHeight to 1440

tell application "Google Chrome"
	activate
	set w to make new window with properties {bounds:{0, 0, screenWidth, screenHeight}}
	delay (random number from 0.2304 to 2.8472)
	open location "http://google.com"
	delay (random number from 1.2304 to 2.8472)
	tell application "System Events" to keystroke "test"
	delay (random number from 0.335 to 1.534)
	
	tell application "System Events" to keystroke return
	delay (random number from 0.335 to 1.534)
	
	repeat 5 times
		tell application "System Events" to keystroke tab
		delay (random number from 0.335 to 1.534)
	end repeat
end tell
do shell script "/usr/local/bin/click -x 0 -y 0"
set fileName to do shell script "date \"+Screen Shot  %Y-%m-%d at %H.%M.%S.png\""
tell application "System Events" to set thePath to POSIX path of desktop folder
do shell script "screencapture  -o -R0,0,1200,1400 -x -T 1 " & "\"" & thePath & "/" & fileName & "\""

	
