################################################################################
#
#  United States Weather
#
#  Webscrapes weather info from weather.gov.
#
#   - Initialization parameters:
#
#       refresh    Minutes to wait between webscrapes (default=20).  Note that
#                  the weather will always be refreshed when the "last update"
#                  of the last fetch is a bit more than an hour old.  Use this
#                  refresh time to get more-frequent forecast updates if wanted.
#       lat, lon   Latitude amd longitude of weather/forecast location, used to 
#                  get data from weather.gov website.  (If either are missing,
#                  both default to lat 36.116453, lon -86.675228)
#       location   Description of location to display during weather segment
#                  If omitted, the "consitions" location from weather.gov for
#                  for the given lat & lon is used
#
#   - Format parameters:
#
#       forecast_periods  Maximum number of forecast periods, out of however
#                         are currently available, to show after giving weather
#                         Can be zero.  Default is 5.
#                         If it's 2 or higher, forecasts are preceeded by an
#                         "extended forecast" header.
#
#
#   Jeff Jetton, Jan-Mar 2023
#
################################################################################

# http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/xml/sitelist/?res=3hourly&key=53d263d4-fd13-4f65-a707-b7265601b092
# <Location elevation="70.0" id="351290" latitude="54.7751" longitude="-1.5833" name="Durham" region="ne" unitaryAuthArea="Durham"/>

# <Location elevation="102.0" id="99049" latitude="54.767" longitude="-1.583" name="Durham" region="ne" unitaryAuthArea="Durham"/>
# <Location elevation="55.0" id="324152" latitude="51.3775" longitude="-0.0933" name="Croydon" region="se" unitaryAuthArea="Greater London"/>
# <Location elevation="53.0" id="353773" latitude="51.3617" longitude="-0.1923" name="Sutton" region="se" unitaryAuthArea="Greater London"/>
# <Location elevation="11.0" id="352409" latitude="51.5081" longitude="-0.1248" name="London" region="se" unitaryAuthArea="Greater London"/>

# http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/xml/351290/?res=3hourly&key=53d263d4-fd13-4f65-a707-b7265601b092
# The predicted forecast every 3 hours within a day, starting at 0 to 21 hrs of the day

from datetime import datetime as dt, time
import json
import urllib.request
from segment_parent import SegmentParent


class Segment(SegmentParent):                  
    # Redefine this so that any UK location can be provided in the CONFIG and it is searched, otherwise London is provided
    def __init__(self, display, init):
        super().__init__(display, init, default_refresh=20)
        # Set the ID from the API based on the location provided
        self.location = init.get('location', None)
        if self.location == "Durham":
            self.id = "351290"
        if self.location == "Sutton":
            self.id = "353773"      
        # Use default of London if a city is not provided
        if self.location == "London" or self.location == None:
            self.location = "London"
            self.id = "352409"


    def show_intro(self):
        self.d.print('Weather provided by metoffice.gov.uk')

    def assign_na(self):
        # Assign the variables we are interested in
        self.data["Temperature"] = "N/A"
        self.data["Feel Like"] = "N/A"
        self.data["Weather Type"] = "N/A"
        self.data["Precipitation Probability"] = "N/A"
        self.data["Wind Speed"] = "N/A"
        self.data["Wind Gust"] = "N/A"
        self.data["Wind Direction"] = "N/A"
        self.data["Humidity"] = "N/A"
        self.data["Visability"] = "N/A"
        self.data["Max UV"] = "N/A"

# Work in refreshing the data later on
    def refresh_data(self):
        self.data = {'fetched_on':dt.datetime.now(),
                     'periods':[],
                     'hazards':[]}

        # Load the correct data
        url = f"http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/{self.id}?res=3hourly&key=53d263d4-fd13-4f65-a707-b7265601b092"
        response = urllib.request.urlopen(url)
        weather_data = (response.read()).decode("utf-8")
        
        # Convert the data to a dictionary
        weather = json.loads(weather_data)

        # Collect the data for the current day
        date0 = weather["SiteRep"]["DV"]["Location"]["Period"][0]["value"]

        # CONVERT DATE TO DT

        time0 = weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][0]["$"]
        # Count how many three hour spreads there are and add this to an array
        timelist = [180, 360, 540, 720, 900, 1080, 1260]
        timeNumbers = timelist.index(int(time0))
        timeArray = timelist[(timeNumbers):]

        # Initialise the appropriate arrays
        tempArray = []
        feelsArray = []
        typeArray = []
        precipArray = []
        windSpeedArray = []
        windGustArray = []
        windDirectionArray = []
        humidArray = []
        visabilityArray = []
        UVArray = []

        for i in range(len(timeArray)):
            # Add the temperatures
            tempArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["T"])
            # Add the feels like temperatures
            feelsArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["F"])
            # Add the weather type
            typeArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["W"])
            # Add the precipitation probability
            precipArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["Pp"])
            # Add the wind speed
            windSpeedArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["S"])
            # Add the wind gust speed
            windGustArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["G"])
            # Add the wind direction
            windDirectionArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["D"])
            # Add the screen relative humidity
            humidArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["H"])
            # Add the visibility
            visabilityArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["V"])
            # Add the UV index values
            UVArray.append(weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][i]["U"])
        
        # Initiate the descriptor arrays
        
        tempDescriptor = []
        feelsDescriptor = []
        typeDescriptor = []
        precipitationDescriptor = []
        windSpeedDescriptor = []
        windGustDescriptor = []
        # No need for wind direction descriptor
        humidityDescriptor = []
        visabilityDescriptor = []
        UVArrayDescriptor = []

        # for i in tempArray:
        #     tempDescriptor.append(i + u'\N{DEGREE SIGN}' + "C")

        # for i in feelsArray:
        #     feelsDescriptor.append(i + u'\N{DEGREE SIGN}' + "C")

        for i in typeArray:
            if i == 0:
                typeDescriptor.append("Clear night")
            if i == 1:
                typeDescriptor.append("Sunny day")
            if i == 2:
                typeDescriptor.append("Partly cloudy (night)")
            if i == 3:
                typeDescriptor.append("Partly cloudy (day)")
            if i == 5:
                typeDescriptor.append("Mist")
            if i == 6:
                typeDescriptor.append("Fog")
            if i == 7:
                typeDescriptor.append("Cloudy")
            if i == 8:
                typeDescriptor.append("Overcast")
            if i == 9:
                typeDescriptor.append("Light rain shower (night)")
            if i == 10:
                typeDescriptor.append("Light rain shower (day)")
            if i == 11:
                typeDescriptor.append("Drizzle")
            if i == 12:
                typeDescriptor.append("Light rain")
            if i == 13:
                typeDescriptor.append("Heavy rain shower (night)")
            if i == 14:
                typeDescriptor.append("Heavy rain shower (day)")
            if i == 15:
                typeDescriptor.append("Heavy rain")
            if i == 16:
                typeDescriptor.append("Sleet shower (night)")
            if i == 17:
                typeDescriptor.append("Sleet shower (day)")
            if i == 18:
                typeDescriptor.append("Sleet")
            if i == 19:
                typeDescriptor.append("Hail shower (night)")
            if i == 20:
                typeDescriptor.append("Hail shower (day)")
            if i == 21:
                typeDescriptor.append("Hail")
            if i == 22:
                typeDescriptor.append("Light snow shower (night)")
            if i == 23:
                typeDescriptor.append("Light snow shower (day)")
            if i == 24:
                typeDescriptor.append("Light snow")
            if i == 25:
                typeDescriptor.append("Heavy snow shower (night)")
            if i == 26:
                typeDescriptor.append("Heavy snow shower (day)")
            if i == 27:
                typeDescriptor.append("Heavy snow")
            if i == 28:
                typeDescriptor.append("Thunder shower (night)")
            if i == 29:
                typeDescriptor.append("Thunder shower (day)")
            if i == 30:
                typeDescriptor.append("Thunder")
            else:
                typeDescriptor.append("None")
        
        # for i in precipArray:
        #     precipitationDescriptor.append(i + "%")
        
        # for i in windSpeedArray:
        #     windSpeedDescriptor.append(i + " mph")
        
        # for i in windGustArray:
        #     windGustDescriptor.append(i + " mph")
        
        # for i in humidArray:
        #     humidityDescriptor.append(i + "%")
        
        for i in visabilityArray:
            if i == "VP":
                visabilityDescriptor.append("Very poor - less than 1km")
            if i == "PO":
                visabilityDescriptor.append("Poor - between 1-4km")
            if i == "MO":
                visabilityDescriptor.append("Moderate - between 4-10km")
            if i == "GO":
                visabilityDescriptor.append("Good - between 10-20km")
            if i == "VG":
                visabilityDescriptor.append("Very good - between 20-40km")
            if i == "EX":
                visabilityDescriptor.append("Excellent - more than 40km")
    
        for i in UVArray:
                if i <= 2:
                    UVArrayDescriptor.append("Low exposure. No protection required. You can safely stay outside")
                if 3 <= i <= 5:
                    typeDescriptor.append("Moderate exposure. Seek shade during midday hours, cover up and wear sunscreen")
                if 6 <= i <= 7:
                    typeDescriptor.append("High exposure. Seek shade during midday hours, cover up and wear sunscreen")
                if 8 <= i <= 10:
                    typeDescriptor.append("Very high. Avoid being outside during midday hours. Shirt, sunscreen and hat are essential")                        
                if i >= 11:
                    typeDescriptor.append("Extreme. Avoid being outside during midday hours. Shirt, sunscreen and hat essential.")
                else:
                    typeDescriptor.append("None")

        # CHECK WHEN THIS NEEDS TO BE DONE

        # Re-initialise the arrays
        timeArray.clear()
        tempArray.clear()
        feelsArray.clear()
        typeArray.clear()
        precipArray.clear()
        windSpeedArray.clear()
        windGustArray.clear()
        windDirectionArray.clear()
        humidArray.clear()
        visabilityArray.clear()
        UVArray.clear()

        # # Provide all the information for tomorrow if it is the evening
        # current_time = dt.utcnow().time()
        # if current_time > time(18,00):
        #     for i in weather["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"]:
        #         timeArray.append(i["$"])
        #         tempArray.append(i["T"])
        #         feelsArray.append(i["F"])
        #         typeArray.append(i["W"])
        #         precipArray.append(i["Pp"])
        #         windSpeedArray.append(i["S"])
        #         windGustArray.append(i["G"])
        #         windDirectionArray.append(i["D"])
        #         humidArray.append(i["H"])
        #         visabilityArray.append(i["V"])
        #         UVArray.append(i["U"])
        # else:
        #     # Provide most of the information for tomorrow if it is not the evening (for the hours 0am, 6am, 12pm, 6pm)
        #     for i in weather["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"]:
        #         timeArray.append(i["$"])
        #         tempArray.append(i["T"])
        #         feelsArray.append(i["F"])
        #         typeArray.append(i["W"])
        #         precipArray.append(i["Pp"])
        #         windSpeedArray.append(i["S"])
        #         windGustArray.append(i["G"])
        #         windDirectionArray.append(i["D"])
        #         humidArray.append(i["H"])
        #         visabilityArray.append(i["V"])
        #         UVArray.append(i["U"])    
        #         i = i + 1
        
        # # Re-initialise the arrays
        # timeArray.clear()
        # tempArray.clear()
        # feelsArray.clear()
        # typeArray.clear()
        # precipArray.clear()
        # windSpeedArray.clear()
        # windGustArray.clear()
        # windDirectionArray.clear()
        # humidArray.clear()
        # visabilityArray.clear()
        # UVArray.clear()

        # # Provide most of the information for the next day (for the hours 0am, 6am, 12pm, 6pm)
        # for i in weather["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"]:
        #     timeArray.append(i["$"])
        #     tempArray.append(i["T"])
        #     feelsArray.append(i["F"])
        #     typeArray.append(i["W"])
        #     precipArray.append(i["Pp"])
        #     windSpeedArray.append(i["S"])
        #     windGustArray.append(i["G"])
        #     windDirectionArray.append(i["D"])
        #     humidArray.append(i["H"])
        #     visabilityArray.append(i["V"])
        #     UVArray.append(i["U"])    
        #     i = i + 1
        
        # Even if not None, also check one element to make sure the site is
        # currently showing weather (i.e. isn't down but still returning soup)
        if self.get_soup(url) is None:
            self.assign_na()
            return


    # time - time0
    # Add percentage etc. on to metrics we are interested in

    # When we type weather, give the weather information briefly (next 3)
    # When we type weather detailed, give the weather information in more detail (next 5 in detail)
    # When we type weather tomorrow, give the weather information for the next few hours (weather for tomorrow)
    # When we type weather three day, give the weather information for the next two days too
    # Automatic alert when turned on and in the afternoon 

    def show(self, fmt):
        forecast_periods = fmt.get('forecast_periods', 5)
        if forecast_periods < 0:
            forecast_periods = 0

        if self.data_is_stale():
            self.d.print_update_msg('Checking for Weather Updates')
            self.refresh_data()

        self.d.print(f'Weather at {self.location}')
        self.d.print(f'As of {self.data["last_update"]}')
            
        self.d.newline()
        self.d.print(f'    Conditions   {self.data["currently"]}')
        self.d.print(f'    Temperature  {self.data["temp_f"]} ({self.data["temp_c"]})')
        self.d.print(f'    Wind         {self.data["wind_speed"]}')
        self.d.print(f'    Visibility   {self.data["visibility"]}')
        self.d.print(f'    Dewpoint     {self.data["dewpoint"]} {self.data["comfort"]}')
        # TODO: only show comfort if warm enough?

        forecast_periods == min(forecast_periods, len(self.data['periods']))
        if forecast_periods > 0:
            self.d.newline(self.d.beat_delay)
            if forecast_periods > 1:
                self.d.newline()
                self.d.print_header('Extended Forecast', '*')

            for period in self.data['periods'][0:forecast_periods]:
                self.d.newline(self.d.beat_delay)
                if forecast_periods > 1:
                    self.d.print(period['timeframe'])
                self.d.print(period['forecast'])


