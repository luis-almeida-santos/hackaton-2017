import json
import sys

from diskcache import FanoutCache

from geopy.geocoders import ArcGIS
from geopy.geocoders import DataBC
from geopy.geocoders import GoogleV3
from geopy.geocoders import Nominatim
from geopy.geocoders import Yandex
import logging

geocoders = [
    Nominatim(),
    GoogleV3(),
    DataBC(),
    ArcGIS(),
    Yandex(),
    #Baidu(),
    #Bing(),
    ##GeocoderDotUS(),
    ##GeocodeFarm(),
    #GeoNames(),
    #OpenCage(),
    ##OpenMapQuest(),
    ##NaviData(),
    #YahooPlaceFinder(),
    #LiveAddress(),
    #What3Words(),
    #IGNFrance(),
    #Phot()
]

location_cache = FanoutCache('/tmp/geo-location-cache', shards=4, timeout=1)

def geocode_location(location_string):

    #logging.debug("Looking for: %s; Cached: %s" % (location_string, location_string in location_cache))

    location = None
    
    if location_string in location_cache:
        return location_cache[location_string]
    else:
        for geolocator in geocoders:
            if location is None:
                location = geolocator.geocode(location_string)
            else:
                break

    if location is None:
        print "%d NOT found in any geo location service" % location_string
    else:
        print "address: %s " % location.address
        print "lat/long: %f - %f " % (location.latitude, location.longitude)
        location_cache[location_string] = location

    return location

def close():
    location_cache.close()
'''
input_location_str = sys.argv[1]
print "input: %s" %  input_location_str

location = geocode_location(input_location_str)


if location is not None:
    columns = 64 * 1
    rows = 32 * 1
    print (columns, rows)
    #img_point = ( (location.longitude*(columns/2)/360), (location.latitude*(rows/2)/180))
    img_point = ( ((columns/360.0) * (180 + location.longitude)), ((rows/180.0) * (90 - location.latitude)) )
    print map(lambda x: int(x) ,img_point)
''' 