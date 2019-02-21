#### coding: utf-8

# In[12]:


import requests

# make the http request to pull down the data
url = 'http://www.cpc.ncep.noaa.gov/data/indices/wksst8110.for'

response = requests.get(url)
data = response.text

#Check the response to make sure you get a valid response
if response.status_code != 200:
    exit

# split the data on each new line
# will give a list of strings with
# each line/row of the file being its own string
lines = data.split('\n')

# keep track of which line of the file we are on
# while we are looping through the lines
line_number = 0
for line in lines:

    line_number += 1
    if line_number < 5:
        # skip the first four lines
        # the "continue" below means to go back to the top of the list
        # and it will not run any code below this block
        continue

    if line:
        # ^ skip blank lines (there is one at the end of the file)

        # parse the individual fields from each line from the file
        date_line = line[1:10]

        nino_12 = line[15:19]
        nino_12a = line[19:23]

        nino_3 = line[28:32]
        nino_3a = line[32:36]
        
        nino_34 = line[41:45]
        nino_34a = line[45:49]
        
        nino_4 = line[54:58]
        nino_4a = line[58:62]
        

# At end of loop, check that the week numbers line up (however they're supposed to.  
#In this case, I'm checking to make sure I'm sending the tweet in the same week as the data.)
from datetime import date,datetime

line_date = datetime.strptime(date_line,"%d%b%Y")
line_week_number = line_date.isocalendar()[1]
print(line_week_number)
today = datetime.today()
today_week_number = today.isocalendar()[1]
print(today_week_number)

import sys
import smtplib
mta = smtplib.SMTP('smtp.gmail.com',587)
username = ''
password = ''
mta.ehlo()
mta.starttls()
mta.login(username,password)
sent_from = username
to = username 

if line_week_number != (today_week_number - 1):
    subject = 'SSTweeter error: '
    text = 'wrong NOAA date!'
    msg = 'From: gawthrop@iri.columbia.edu\n Subject: {}{}'.format(subject, text)
    mta.sendmail(sent_from, to, msg)
    sys.exit('wrong date')
        
    
#isolate nino 3.4 anomaly and convert to float
#since the above will end on the final line with data
#it will end with the latest data, which is what we want
lateststr = nino_34a
latestfloat = float(lateststr)

# insert your own keys and secrets here...
CONSUMER_KEY = ""
CONSUMER_SECRET = ""
ACCESS_TOKEN = ""
ACCESS_TOKEN_SECRET = ""

from tweepy import OAuthHandler, API

# setup the authentication
auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

# create an object to communicate with the Twitter API
api = API(auth)

#check to see api is working with the correct account
print('Ok, we are ready to tweet as ' + api.me().screen_name)

# establish ENSO ranges
if (latestfloat <= -0.5) and (latestfloat >-1.0):
    ensostatus = u"the weak La Niña range."
elif (latestfloat <=-1.0) and (latestfloat >-1.5):
    ensostatus = u"the moderate La Niña range."
elif (latestfloat <=-1.5):
    ensostatus = u"the strong La Niña range."
elif (latestfloat >= 0.5) and (latestfloat <1.0):
    ensostatus = u"the weak El Niño range."
elif (latestfloat >=1.0) and (latestfloat <1.5):
    ensostatus = u"the moderate El Niño range."
elif (latestfloat >=1.5):
    ensostatus = u"the strong El Niño range."
else: 
    ensostatus = "the neutral ENSO range."
    
# Check reasonable max and minimums on latestfloat
if latestfloat < -4:
    text = 'crazy low data' 
    msg = 'Subject: {}{}'.format(subject, text)
    mta.sendmail(sent_from, to, msg)
    sys.exit('crazy low data')
if latestfloat > 4: 
    text = 'crazy high data' 
    msg = 'Subject: {}{}'.format(subject, text)
    mta.sendmail(sent_from, to, msg)
    sys.exit('crazy high data')
    
# define text of the tweet
tweet_text = 'The latest weekly Nino3.4 SST anomaly is' + lateststr + u'ºC, which is within ' + ensostatus 

import os
from PIL import Image
import urllib
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import io

# define twitter post function with image download from image url
def tweet_image(url, message):
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)
       
    else:
        text = 'DL image not available' 
        msg = 'Subject: {}{}'.format(subject, text)
        mta.sendmail(sent_from, to, msg)
        sys.exit("Unable to download image")
         
    file = Image.open(filename)
    overlay = Image.open("nino34box.png")
    file.paste(overlay, (0, 0), overlay)
    file.save('temp.jpg')
    file = open('temp.jpg', 'rb')
    r1 = api.media_upload(filename='temp.jpg', file=file)
    media_ids = [r1.media_id_string]
    api.update_status(media_ids=media_ids, status=message)
    os.remove(filename)

url = "http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.EMC/.CMB/.GLOBAL/.Reyn_SmithOIv2/.weekly/.ssta/startcolormap/DATA/-5./5./RANGE/black/navy/blue/-5./VALUE/cyan/-0.5/VALUE/white/white/0.5/bandmax/yellow/0.5/VALUE/red/5./VALUE/firebrick/endcolormap/DATA/0.5/STEP/a-+++-a-++-a+X+Y+fig:+colors+nozero+contours+land+:fig+//T/last/plotvalue/X/100.0/300.0/plotrange/Y/-40/40/plotrange+//plotbordertop+40+psdef//plotborderbottom+40+psdef//XOVY+null+psdef//plotaxislength+600+psdef//antialias+true+psdef//color_smoothing+null+psdef+.jpg"
message = tweet_text + ' This map and more in our data library: http://iridl.ldeo.columbia.edu/maproom/ENSO/SST_Plots/Weekly_Anomaly.html. + More about ENSO: http://bit.ly/ENSO101.'
tweet_image(url, message)

text = ' Tweet sent' 
subject = 'SSTweeter Success!'
msg = 'Subject: {}{}'.format(subject, text)
mta.sendmail(sent_from, to, msg)
print("done")