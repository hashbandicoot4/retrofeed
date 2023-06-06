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
    
    # utc_offsets = {'EST':'-0500', 'CST':'-0600', 'MST':'-0700', 'PST':'-0800', 'AKST':'-0900', 'HST':'-1000',
    #                'EDT':'-0400', 'CDT':'-0500', 'MDT':'-0600', 'PDT':'-0700', 'AKDT':'-0800', 'HDT':'-0900' }
                  
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


# CONTINUE FROM HERE ...

    # @classmethod
    # def get_comfort_from_dewpoint(cls, dp_text):
    #     dp = int(dp_text.split('F')[0])
    #     if dp < 50:
    #         return 'Dry'
    #     if dp <= 60:
    #         return 'Pleasant'
    #     if dp <= 65:
    #         return 'A Bit Humid'
    #     if dp <= 70:
    #         return 'Humid'
    #     if dp <= 75:
    #         return 'Very Humid'
    #     return 'Oppressive'


    def assign_na(self):
        # self.data['conditions_location'] = 'N/A'
        # self.data['currently'] = 'N/A'
        # self.data['temp_f'] = 'N/A'
        # self.data['temp_c'] = 'N/A'
        # self.data['humidity'] = 'N/A'
        # self.data['barometer'] = 'N/A'
        # self.data['comfort'] = ''
        # self.data['last_update'] = 'N/A'
        # self.data['wind_speed'] = 'N/A'
        # self.data['visibility'] = 'N/A'
        # self.data['dewpoint'] = 'N/A'
        # self.data['periods'] = [{'timeframe':'Forecast Not Available',
        #                          'forecast':''}]

        # UNDERSTAND HOW SELF.DATA WORKS AND HOW TO THINGS ARE PRINTED BY IT

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


    @classmethod
    def string_to_dt(cls, s):
        # Convert a string in weather.gov's "last update" format to
        # a timezone-aware datetime object
        dt_string = s.strip()
        # Assume year is current year (possibly inaccurate just after
        # midnight on New Year's Eve... oh well)
        dt_string = f"{dt.datetime.now().year} {dt_string}"
        # Pull out the last word (presumably the time zone code)
        tz = dt_string[dt_string.rfind(' ')+1:]
        # If it matches an offset, replace code with offset and convert
        if tz in cls.utc_offsets:
            dt_string = dt_string.replace(tz, cls.utc_offsets[tz])
            dt_object = dt.datetime.strptime(dt_string, '%Y %d %b %I:%M %p %z')
        else:
            # Otherwise, convert with local timezone info
            dt_string = dt_string.replace(tz, '').strip()
            dt_object = dt.datetime.strptime(dt_string, '%Y %d %b %I:%M %p').astimezone()
        return dt_object

# Work in refreshing the data later on
    def refresh_data(self):
        self.data = {'fetched_on':dt.datetime.now(),
                     'periods':[],
                     'hazards':[]}

        # Load the correct data
        # url = f'https://forecast.weather.gov/MapClick.php?lat={self.lat}&lon={self.lon}'
        url = f"http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/{self.id}?res=3hourly&key=53d263d4-fd13-4f65-a707-b7265601b092"
        response = urllib.request.urlopen(url)
        weather_data = (response.read()).decode("utf-8")
        
        # Convert the data to a dictionary
        weather = json.loads(weather_data)

        # Collect the data for the current day
        date0 = weather["SiteRep"]["DV"]["Location"]["Period"][0]
        time0 = weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"][0]["$"]
        timeArray = []
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

        # Provide all the information for the current day
        for i in weather["SiteRep"]["DV"]["Location"]["Period"][0]["Rep"]:
            timeArray.append(i["$"] - time0)
            tempArray.append(i["T"])
            feelsArray.append(i["F"])
            typeArray.append(i["W"])
            precipArray.append(i["Pp"])
            windSpeedArray.append(i["S"])
            windGustArray.append(i["G"])
            windDirectionArray.append(i["D"])
            humidArray.append(i["H"])
            visabilityArray.append(i["V"])
            UVArray.append(i["U"])
        
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

        # Provide all the information for tomorrow if it is the evening
        current_time = dt.utcnow().time()
        if current_time > time(18,00):
            for i in weather["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"]:
                timeArray.append(i["$"])
                tempArray.append(i["T"])
                feelsArray.append(i["F"])
                typeArray.append(i["W"])
                precipArray.append(i["Pp"])
                windSpeedArray.append(i["S"])
                windGustArray.append(i["G"])
                windDirectionArray.append(i["D"])
                humidArray.append(i["H"])
                visabilityArray.append(i["V"])
                UVArray.append(i["U"])
        else:
            # Provide most of the information for tomorrow if it is not the evening (for the hours 0am, 6am, 12pm, 6pm)
            for i in weather["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"]:
                timeArray.append(i["$"])
                tempArray.append(i["T"])
                feelsArray.append(i["F"])
                typeArray.append(i["W"])
                precipArray.append(i["Pp"])
                windSpeedArray.append(i["S"])
                windGustArray.append(i["G"])
                windDirectionArray.append(i["D"])
                humidArray.append(i["H"])
                visabilityArray.append(i["V"])
                UVArray.append(i["U"])    
                i = i + 1
        
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

        # Provide most of the information for the next day (for the hours 0am, 6am, 12pm, 6pm)
        for i in weather["SiteRep"]["DV"]["Location"]["Period"][1]["Rep"]:
            timeArray.append(i["$"])
            tempArray.append(i["T"])
            feelsArray.append(i["F"])
            typeArray.append(i["W"])
            precipArray.append(i["Pp"])
            windSpeedArray.append(i["S"])
            windGustArray.append(i["G"])
            windDirectionArray.append(i["D"])
            humidArray.append(i["H"])
            visabilityArray.append(i["V"])
            UVArray.append(i["U"])    
            i = i + 1
        
        # soup = self.get_soup(url)
        # # Even if not None, also check one element to make sure the site is
        # # currently showing weather (i.e. isn't down but still returning soup)
        # if soup is None or soup.find('h2', 'panel-title') is None:
        #     self.assign_na()
        #     return

        # # Parse away...
        # self.data['conditions_location'] = self.d.clean_chars(soup.find('h2', 'panel-title').string)
        # # If object wasn't instantiated with a location, set it to whatever came back from fetch
        # if self.location == None or self.location.strip() == '':
        #     self.location = self.data['conditions_location']
        # self.data['currently'] = self.d.clean_chars(soup.find('p', 'myforecast-current').string)
        # self.data['temp_f'] = self.d.clean_chars(soup.find('p', 'myforecast-current-lrg').string)
        # self.data['temp_c'] = self.d.clean_chars(soup.find('p', 'myforecast-current-sm').string)

        # # Various weather stats are stored as table data in the sole table
        # cells = soup.find_all('td')
        # key = None
        # for cell in cells:
        #     if key is None:
        #         key = cell.string.lower().replace(' ', '_')
        #     else:
        #         self.data[key] = self.d.clean_chars(cell.string)
        #         key = None

        # # Try to convert the "last_update" text to a real datetime value
        # if 'last_update' in self.data:
        #     self.data['last_update_dt'] = self.string_to_dt(self.data['last_update'])

        # # Text description of the dewpoint
        # self.data['comfort'] = self.get_comfort_from_dewpoint(self.data['dewpoint'])

        # # Get period forecast from the alt-text of the weather icons
        # icons = soup.find_all('img', 'forecast-icon')
        # for icon in icons:
        #     alt_text = icon['alt']
        #     if alt_text is None or alt_text.strip() == '':
        #         continue
        #     split_text = alt_text.split(':', 1)
        #     if len(split_text) == 2:
        #         period = {'timeframe':self.d.clean_chars(split_text[0]),
        #                   'forecast':self.d.clean_chars(split_text[1])}
        #         self.data['periods'].append(period)

        # # Any hazard headlines?
        # hazards = soup.find_all('a', 'anchor-hazards')
        # for hazard in hazards:
        #     stripped_haz = hazard.contents[0].strip()
        #     if stripped_haz != 'Hazardous Weather Outlook' and stripped_haz != '':
        #         self.data['hazards'].append(self.d.clean_chars(stripped_haz))


    # Override to add one more stale condition
    def data_is_stale(self):
        # Start witht the usual check:  Data is stale if we don't have any
        # weather yet (self.data still None) or refresh time has elapsed:
        if super().data_is_stale():
            return True
        else:
            # Data is always stale if (slightly) more than an hour has gone by
            now = dt.datetime.now()
            return 'last_update_dt' in self.data and now.astimezone() - self.data['last_update_dt'] >= dt.timedelta(minutes=62)



    def show(self, fmt):
        forecast_periods = fmt.get('forecast_periods', 5)
        if forecast_periods < 0:
            forecast_periods = 0

        if self.data_is_stale():
            self.d.print_update_msg('Checking for Weather Updates')
            self.refresh_data()

        self.d.print(f'Weather at {self.location}')
        self.d.print(f'As of {self.data["last_update"]}')
    
        if len(self.data['hazards']) > 0:
            for hazard in self.data['hazards']:
                self.d.newline()
                self.d.print('!!! ' + hazard)
            
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


