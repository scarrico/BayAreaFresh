#!/bin/bash
# USAGE:
# <this scriptname> <script directory>
#
# To run use home directory for this script in $1
# File .smsenv in $1 directory sets following variables
# export TWILIO_ACCOUNT_SID
# export TWILIO_AUTH_TOKEN
# export TWILIO_FROM_NUMBER
# export PHONE
# 
# cron entry (substitute actual values below)
# 0 * * * * <full path to script+ipmessenger.bash> <full path to script> >> <full path to script+ipmessenger.log> 2>&1

if [ -z ${1+x} ] 
then 
        echo "first parameter must be execution directory"
        exit 1
fi
d=$1
e="/.smsenv"
. $d$e
newip=$d"newip"
oldip=$d"oldip"
cp $newip $oldip
myip="$(dig +short myip.opendns.com @resolver1.opendns.com)" 
echo $myip > $newip
l=`diff $newip $oldip | wc -l`
if [ "$l" -gt "0" ]
then
     MSG="New_IP_"$myip
     RESPONSE=`curl -fSs -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN" -d "From=$TWILIO_FROM_NUMBER" -d "To=$PHONE" -d "Body=$MSG" "https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/SMS/Messages" 2>&1`
	if [ $? -gt 0 ]
    then 
        echo "Failed to send SMS to $PHONE: $RESPONSE"
	fi
  echo "***** new ip: $myip ****"
fi
