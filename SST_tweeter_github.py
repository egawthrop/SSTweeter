
# coding: utf-8

# In[12]:


import requests

# make the http request to pull down the data
url = 'http://www.cpc.ncep.noaa.gov/data/indices/wksst8110.for'

response = requests.get(url)
data = response.text

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
        date = line[1:10]

        nino_12 = line[15:19]
        nino_12a = line[19:23]

        nino_3 = line[28:32]
        nino_3a = line[32:36]
        
        nino_34 = line[41:45]
        nino_34a = line[45:49]
        
        nino_4 = line[54:58]
        nino_4a = line[58:62]
        
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
    ensostatus = "the weak La Niña range."
elif (latestfloat <=-1.0) and (latestfloat >-1.5):
    ensostatus = "the moderate La Niña range."
elif (latestfloat <=-1.5):
    ensostatus = "the strong La Niña range."
elif (latestfloat >= 0.5) and (latestfloat <1.0):
    ensostatus = "the weak El Niño range."
elif (latestfloat >=1.0) and (latestfloat <1.5):
    ensostatus = "the moderate El Niño range."
elif (latestfloat >=1.5):
    ensostatus = "the strong El Niño range."
else: 
    ensostatus = "the neutral ENSO range."
    
# define text of the tweet
tweet_text = 'The latest weekly Nino3.4 SST anomaly is ' + lateststr + 'ºC, which is within ' + ensostatus 

import os

# define twitter post function with image download from image url
def tweet_image(url, message):
    filename = 'temp.jpg'
    request = requests.get(url, stream=True)
    if request.status_code == 200:
        with open(filename, 'wb') as image:
            for chunk in request:
                image.write(chunk)

        api.update_with_media(filename, status=message)
        os.remove(filename)
    else:
        print("Unable to download image")


url = "http://iridl.ldeo.columbia.edu/SOURCES/.NOAA/.NCEP/.EMC/.CMB/.GLOBAL/.Reyn_SmithOIv2/.weekly/.ssta/startcolormap/DATA/-5./5./RANGE/black/navy/blue/-5./VALUE/cyan/-0.5/VALUE/white/white/0.5/bandmax/yellow/0.5/VALUE/red/5./VALUE/firebrick/endcolormap/DATA/0.5/STEP/a-+++-a-++-a+X+Y+fig:+colors+nozero+contours+land+:fig+//T/last/plotvalue/X/100.0/300.0/plotrange/Y/-40/40/plotrange+//plotbordertop+40+psdef//plotborderbottom+40+psdef//XOVY+null+psdef//plotaxislength+600+psdef//antialias+true+psdef//color_smoothing+null+psdef+.jpg"
message = 'The latest weekly Nino3.4 SST anomaly is ' + lateststr + 'ºC, which is within ' + ensostatus + ' This map and more in our data library: http://iridl.ldeo.columbia.edu/maproom/ENSO/SST_Plots/Weekly_Anomaly.html.'
tweet_image(url, message)


# run using cron in unix/remote server to ensure a continuous SST update 

