from datetime import datetime as dt, time
import json
import urllib.request

url = f"http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/351290?res=3hourly&key=53d263d4-fd13-4f65-a707-b7265601b092"
response = urllib.request.urlopen(url)
weather_data = (response.read()).decode("utf-8")
        
# Convert the data to a dictionary
weather = json.loads(weather_data)

# Collect the data for the current day
date0 = weather["SiteRep"]["DV"]["Location"]["Period"][0]["value"]
time0 = weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][0]["$"]
# Count how many three hour spreads there are and add this to an array
timelist = [180, 360, 540, 720, 900, 1080, 1260]
timeNumbers = timelist.index(int(time0))
timeArray = timelist[(timeNumbers):]
# Add the temperatures to an array
tempArray = []
for i in range(len(timeArray)):
     tempArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["T"])
# Add the feels like temperatures to an array
feelsArray = []
for i in range(len(timeArray)):
     feelsArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["F"])
# Add the weather type to an array
typeArray = []
for i in range(len(timeArray)):
     typeArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["W"])
# Add the precipitation probability to an array
precipArray = []
for i in range(len(timeArray)):
     precipArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["Pp"])
# Add the fwind speed to an array
windSpeedArray = []
for i in range(len(timeArray)):
     windSpeedArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["S"])
# Add the wind gust speed to an array
windGustArray = []
for i in range(len(timeArray)):
     windGustArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["G"])
# Add the wind direction to an array
windDirectionArray = []
for i in range(len(timeArray)):
     windDirectionArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["D"])
# Add the screen relative humidity to an array
humidArray = []
for i in range(len(timeArray)):
     humidArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["H"])
# Add the visibility to an array
visabilityArray = []
for i in range(len(timeArray)):
     visabilityArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["V"])
# Add the UV index values to an array
UVArray = []
for i in range(len(timeArray)):
     UVArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["U"])

date1 = weather["SiteRep"]["DV"]["Location"]["Period"][1]["value"]

print(humidArray)