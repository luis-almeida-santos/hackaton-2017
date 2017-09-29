#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image
from PIL import ImageDraw
import time
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from random import randint, sample
import numpy as np
import shapefile
import geocode
import logging
import threading
import signal
import sys
import cv2
from math import pi, tan, log
from time import sleep, time
from diskcache import FanoutCache
from sseclient import SSEClient
import json
import random

PANELS_HORIZONTAL = 2
PANELS_VERTICAL = 2

PLOT_PANELS_OUTLINE = False
PLOT_BACKGROUND_MAP = True
PLOT_FAKE_LOCATIONS = False

OUTPUT_VIDEO = True

EVENTS_SOURCE_URL="http://localhost:8080/events"

# world cities, to test only
LOCATIONS = [
    "Toronto, Ontario, Canada", "Montreal, Quebec, Canada", "Vancouver, British Columbia, Canada", "Calgary, Alberta, Canada", "Ottawa, Ontario, Canada", "Edmonton, Alberta, Canada", "Quebec City, Quebec, Canada", "Winnipeg, Manitoba, Canada", "Hamilton, Ontario, Canada", "Kitchener, Ontario, Canada", "London, Ontario, Canada", 
    "Cairo, Egypt", "Lagos, Nigeria", "Kinshasa-Brazzaville, Democratic Republic of the Congo", "Greater Johannesburg, South Africa", "Luanda, Angola", "Khartoum-Omdurman, Sudan", "Dar es Salaam, Tanzania", "Abidjan, Ivory Coast", "Alexandria, Egypt", "Nairobi, Kenya", "Cape Town, South Africa", "Kano, Nigeria", "Dakar, Senegal", "Casablanca, Morocco", "Addis Ababa, Ethiopia", "Ibadan, Nigeria", "Yaoundé, Cameroon", "Douala, Cameroon", "Durban, South Africa", "Ouagadougou, Burkina Faso", "Antananarivo, Madagascar", "Kumasi, Ghana", "Algiers, Algeria", "Bamako, Mali", "Abuja, Nigeria", "Port Harcourt, Nigeria", "Accra, Ghana", "Lusaka, Zambia", "Mogadishu, Somalia", "Pretoria, South Africa", "Lubumbashi, Democratic Republic of the Congo", "Mbuji-Mayi, Democratic Republic of the Congo", "Tunis, Tunisia", "Rabat, Morocco", "Conakry, Guinea", "Kampala, Uganda", "Harare, Zimbabwe", "Benin City, Nigeria", "Huambo, Angola", "Monrovia, Liberia", "Ndjamena, Chad", "Kigali, Rwand", "Maputo, Mozambique", "Port Elizabeth, South Africa", "Fès, Morocco", "Kananga, Democratic Republic of the Congo", "Vereeniging, South Africa", "Marrakech, Morocco", "Tripoli, Libya", "Onitsha, Nigeria", "Mombasa, Kenya", "Niamey, Niger", "Kaduna, Nigeria", "Kisangani, Democratic Republic of the Congo", "Freetown, Sierra Leone", 
    "Sydney, Australia", "Melbourne, Australia", "Brisbane, Australia", "Perth, Australia", "Auckland, New Zealand", "Adelaide, Australia", "Gold Coast, Australia", "Wellington, New Zealand", "Christchurch, New Zealand", "Canberra, Australia", "Port Moresby, Papua New Guinea", "Central Coast, Australia", "Newcastle, Australia", "Sunshine Coast, Australia", "Wollongong, Australia", "Dili, East Timor", "Hamilton, New Zealand", "Noumea, New Caledonia", 
    "Moscow, Russia", "Saint, Russia", "Novosibirsk, Russia", "Yekaterinburg, Russia", "Nizhny, Russia", "Kazan, Russia", "Chelyabinsk, Russia", "Omsk, Russia", "Samara, Russia", "Rostov, Russia", "Ufa, Russia", "Krasnoyarsk, Russia", "Perm, Russia", "Voronezh, Russia", "Volgograd, Russia", "Krasnodar, Russia", "Saratov, Russia", "Tyumen, Russia", "Tolyatti, Russia", "Izhevsk, Russia", "Barnaul, Russia", "Ulyanovsk, Russia", "Irkutsk, Russia", "Khabarovsk, Russia", "Yaroslavl, Russia", "Vladivostok, Russia", "Makhachkala, Russia", "Tomsk, Russia", "Orenburg, Russia", "Kemerovo, Russia", "Novokuznetsk, Russia", "Ryazan, Russia", "Astrakhan, Russia", "Naberezhnye, Russia", "Penza, Russia", "Lipetsk, Russia", "Kirov, Russia", "Cheboksary, Russia", "Tula, Russia", "Kaliningrad, Russia", "Balashikha, Russia", "Kursk, Russia", "Stavropol, Russia", "Ulan, Russia", "Tver, Russia", "Magnitogorsk, Russia", "Sochi, Russia", "Ivanovo, Russia", "Bryansk, Russia", "Belgorod, Russia", "Surgut, Russia", "Vladimir, Russia", "Nizhny, Russia", "Arkhangelsk, Russia", "Chita, Russia", "Kaluga, Russia", "Smolensk, Russia", "Volzhsky, Russia", "Kurgan, Russia", "Cherepovets, Russia", "Oryol, Russia", "Saransk, Russia", "Vologda, Russia", "Yakutsk, Russia", "Vladikavkaz, Russia", "Podolsk, Russia", "Murmansk, Russia", "Grozny, Russia", "Tambov, Russia", "Sterlitamak, Russia", "Petrozavodsk, Russia", "Kostroma, Russia", "Nizhnevartovsk, Russia", "Novorossiysk, Russia", "Yoshkar, Russia", "Taganrog, Russia", "Komsomolsk, Russia", "Khimki, Russia", "Syktyvkar, Russia", "Nalchik, Russia", "Nizhnekamsk, Russia", "Shakhty, Russia", "Dzerzhinsk, Russia", "Bratsk, Russia", "Orsk, Russia", "Angarsk, Russia", "Engels, Russia", "Blagoveshchensk, Russia", "Stary, Russia", "Veliky, Russia", "Korolyov, Russia", "Pskov, Russia", "Mytishchi, Russia", "Biysk, Russia", "Lyubertsy, Russia", "Prokopyevsk, Russia", "Yuzhno, Russia", "Balakovo, Russia", "Armavir, Russia", "Rybinsk, Russia", "Severodvinsk, Russia", "Abakan, Russia", "Petropavlovsk, Russia", "Norilsk, Russia", "Syzran, Russia", "Volgodonsk, Russia", "Ussuriysk, Russia", "Kamensk, Russia", "Novocherkassk, Russia", "Zlatoust, Russia", "Elektrostal, Russia", "Almetyevsk, Russia", "Krasnogorsk, Russia", "Salavat, Russia", "Miass, Russia", "Nakhodka, Russia", "Kopeysk, Russia", "Pyatigorsk, Russia", "Rubtsovsk, Russia", "Berezniki, Russia", "Kolomna, Russia", "Maykop, Russia", "Odintsovo, Russia", "Khasavyurt, Russia", "Kovrov, Russia", "Kislovodsk, Russia", "Neftekamsk, Russia", "Nefteyugansk, Russia", "Novocheboksarsk, Russia", "Serpukhov, Russia", "Shchyolkovo, Russia", "Novomoskovsk, Russia", "Bataysk, Russia", "Pervouralsk, Russia", "Domodedovo, Russia", "Derbent, Russia", 
    "Tokyo, Japan", "Jakarta, Indonesia", "Delhi, India", "Karachi, Pakistan", "Seoul, South Korea", "Shanghai, China", "Manila, Philippines", "Mumbai, India", "Beijing, China", "Guangzhou-Foshan, China", "Osaka-Kobe-Kyoto, Japan", "Dhaka, Bangladesh", "Bangkok, Thailand", "Kolkata, India", "Tehran, Iran", "Chongqing, China", "Tianjin, China", "Shenzhen, China", "Chengdu, China", "Bengaluru, India", "Lahore, Pakistan", "Nagoya, Japan", "Ho Chi Minh City, Vietnam", "Chennai, India", "Hyderabad, India", "Taipei, Taiwan", "Hangzhou, China", "Dongguan, China", "Wuhan, China", "Shenyang, China", "Hanoi, Vietnam", "Ahmedabad, India", "Kuala Lumpur, Malaysia", "Hong Kong, China", "Nanjing, China", "Zhengzhou-Xingyang, China", "Baghdad, Iraq", "Singapore, Singapore", "Riyadh, Saudi Arabia", "Quanzhou-Shishi-Jinjiang, China", 
    "São Paulo, Brazil", "Lima, Peru", "Bogotá, Colombia", "Rio de Janeiro, Brazil", "Santiago, Chile", "Caracas, Venezuela", "Buenos Aires, Argentina", "Salvador, Brazil", "Brasília, Brazil", "Fortaleza, Brazil", "Guayaquil, Ecuador", "Quito, Ecuador", "Belo Horizonte, Brazil", "Medellín, Colombia", "Cali, Colombia", "Manaus, Brazil", "Curitiba, Brazil", "Maracaibo, Venezuela", "Recife, Brazil", "Santa Cruz de la Sierra, Bolivia", "Porto Alegre, Brazil", "Belém, Brazil", "Goiânia, Brazil", "Córdoba, Argentina", "Montevideo, Uruguay", "Guarulhos, Brazil", "Barranquilla, Colombia", "Campinas, Brazil", "Barquisimeto, Venezuela", "São Luís, Brazil", "São Gonçalo, Brazil", "Maceió, Brazil", "Callao, Peru", "Rosario, Argentina", "Cartagena, Colombia", "Valencia, Venezuela", "El Alto, Bolivia", "Duque de Caxias, Brazil", "Ciudad Guayana, Venezuela", "Natal, Brazil", "Arequipa, Peru", "Campo Grande, Brazil", "Teresina, Brazil", "São Bernardo do Campo, Brazil", "Nova Iguaçu, Brazil", "Trujillo, Peru", "João Pessoa, Brazil", "La Paz, Bolivia", "Santo André, Brazil", "Osasco, Brazil", "São José dos Campos, Brazil", "La Plata, Argentina", "Jaboatão dos Guararapes, Brazil", "Cochabamba, Bolivia", "Ribeirão Preto, Brazil", "Uberlândia, Brazil", "Contagem, Brazil", "Sorocaba, Brazil", "Mar del Plata, Argentina", "Aracaju, Brazil", "Cúcuta, Colombia", "Feira de Santana, Brazil", "Soledad, Colombia", "Puente Alto, Chile", "Chiclayo, Peru", "Salta, Argentina", "San Miguel de Tucumán, Argentina", "Maturín, Venezuela", "Cuenca, Ecuador", "Cuiabá, Brazil", "Joinville, Brazil", "Juiz de Fora, Brazil", "Londrina, Brazil", "Asunción, Paraguay", "Ibagué, Colombia", "Aparecida de Goiânia, Brazil", "Bucaramanga, Colombia", "Ananindeua, Brazil", "Soacha, Colombia", "Porto Velho, Brazil", 
    "New York, USA", "Los Angeles, USA", "Chicago, USA", "Houston, USA", "Phoenix, USA", "Philadelphia, USA", "San Antonio, USA", "San Diego, USA", "Dallas, USA", "San Jose, USA", "Austin, USA", "Jacksonville, USA", "San Francisco, USA", "Columbus, USA", "Indianapolis, USA", "Fort Worth, USA", "Charlotte, USA", "Seattle, USA", "Denver, USA", "El Paso, USA", "Washington, USA", "Boston, USA", "Detroit, USA", "Nashville, USA", "Memphis, USA", "Portland, USA", "Oklahoma City, USA", "Las Vegas, USA", "Louisville, USA", "Baltimore, USA", "Milwaukee, USA", "Albuquerque, USA", "Tucson, USA", "Fresno, USA", "Sacramento, USA", "Mesa, USA", "Kansas City, USA", "Atlanta, USA", "Long Beach, USA", "Colorado Springs, USA", "Raleigh, USA", "Miami, USA", "Virginia Beach, USA", "Omaha, USA", "Oakland, USA", "Minneapolis, USA", "Tulsa, USA", "Arlington, USA", "New Orleans, USA", "Wichita, USA", "Cleveland, USA", "Tampa, USA", "Bakersfield, USA", "Aurora, USA", "Honolulu, USA", "Anaheim, USA", "Santa Ana, USA", "Corpus Christi, USA", "Riverside, USA", "Lexington, USA", "Stockton, USA", "Pittsburgh, USA", "Saint Paul, USA", "Cincinnati, USA", "Anchorage, USA", "Henderson, USA", "Greensboro, USA", "Plano, USA", "Newark, USA", "Lincoln, USA", "Toledo, USA", "Orlando, USA", "Chula Vista, USA", "Irvine, USA", "Fort Wayne, USA", "Jersey City, USA", "Durham, USA", "Laredo, USA", "Buffalo, USA", "Madison, USA", "Lubbock, USA", "Chandler, USA", "Scottsdale, USA", "Glendale, USA", "Reno, USA", "Norfolk, USA", "North Las Vegas, USA", "Irving, USA", "Chesapeake, USA", "Gilbert, USA", "Hialeah, USA", "Garland, USA", "Fremont, USA", "Baton Rouge, USA", "Richmond, USA", "Boise, USA", "San Bernardino, USA", "Spokane, USA", "Des Moines, USA", "Modesto, USA", "Birmingham, USA", "Tacoma, USA", "Fontana, USA", "Rochester, USA", "Oxnard, USA", "Moreno Valley, USA", "Fayetteville, USA", "Aurora, USA", "Glendale, USA", "Yonkers, USA", "Huntington Beach, USA", "Montgomery, USA", "Amarillo, USA", "Little Rock, USA", "Akron, USA", "Columbus, USA", "Augusta, USA", "Grand Rapids, USA", "Shreveport, USA", "Salt Lake City, USA", "Huntsville, USA", "Mobile, USA", "Tallahassee, USA", "Grand Prairie, USA", "Overland Park, USA", "Knoxville, USA", "Worcester, USA", "Brownsville, USA", "Tempe, USA", "Santa Clarita, USA", "Newport News, USA", "Cape Coral, USA", "Providence, USA", "Fort Lauderdale, USA", "Chattanooga, USA", "Rancho Cucamonga, USA", "Oceanside, USA", "Santa Rosa, USA", "Garden Grove, USA", "Vancouver, USA", "Sioux Falls, USA", "Ontario, USA", "McKinney, USA", "Elk Grove, USA", "Jackson, USA", "Pembroke Pines, USA", "Salem, USA", "Springfield, USA", "Corona, USA", "Eugene, USA", "Fort Collins, USA", "Peoria, USA", "Frisco, USA", "Cary, USA", "Lancaster, USA", "Hayward, USA", "Palmdale, USA", "Salinas, USA", "Alexandria, USA", "Lakewood, USA", "Springfield, USA", "Pasadena, USA", "Sunnyvale, USA", "Macon, USA", "Pomona, USA", "Hollywood, USA", "Kansas City, USA", "Escondido, USA", "Clarksville, USA", "Joliet, USA", "Rockford, USA", "Torrance, USA", "Naperville, USA", "Paterson, USA", "Savannah, USA", "Bridgeport, USA", "Mesquite, USA", "Killeen, USA", "Syracuse, USA", "McAllen, USA", "Pasadena, USA", "Bellevue, USA", "Fullerton, USA", "Orange, USA", "Dayton, USA", "Miramar, USA", "Thornton, USA", "West Valley City, USA", "Olathe, USA", "Hampton, USA", "Warren, USA", "Midland, USA", "Waco, USA", "Charleston, USA", "Columbia, USA", "Denton, USA", "Carrollton, USA", "Surprise, USA", "Roseville, USA", "Sterling Heights, USA", "Murfreesboro, USA", "Gainesville, USA", "Cedar Rapids, USA", "Visalia, USA", "Coral Springs, USA", "New Haven, USA", "Stamford, USA", "Thousand Oaks, USA", "Concord, USA", "Elizabeth, USA", "Lafayette, USA", "Kent, USA", "Topeka, USA", "Simi Valley, USA", "Santa Clara, USA", "Athens, USA", "Hartford, USA", "Victorville, USA", "Abilene, USA", "Norman, USA", "Vallejo, USA", "Berkeley, USA", "Round Rock, USA", "Ann Arbor, USA", "Fargo, USA", "Columbia, USA", "Allentown, USA", "Evansville, USA", "Beaumont, USA", "Odessa, USA", "Wilmington, USA", "Arvada, USA", "Independence, USA", "Provo, USA", "Lansing, USA", "El Monte, USA", "Springfield, USA", "Fairfield, USA", "Clearwater, USA", "Peoria, USA", "Rochester, USA", "Carlsbad, USA", "Westminster, USA", "West Jordan, USA", "Pearland, USA", "Richardson, USA", "Downey, USA", "Miami Gardens, USA", "Temecula, USA", "Costa Mesa, USA", "College Station, USA", "Elgin, USA", "Murrieta, USA", "Gresham, USA", "High Point, USA", "Antioch, USA", "Inglewood, USA", "Cambridge, USA", "Lowell, USA", "Manchester, USA", "Billings, USA", "Pueblo, USA", "Palm Bay, USA", "Centennial, USA", "Richmond, USA", "Ventura, USA", "Pompano Beach, USA", "North Charleston, USA", "Everett, USA", "Waterbury, USA", "West Palm Beach, USA", "Boulder, USA", "West Covina, USA", "Broken Arrow, USA", "Clovis, USA", "Daly City, USA", "Lakeland, USA", "Santa Maria, USA", "Norwalk, USA", "Sandy Springs, USA", "Hillsboro, USA", "Green Bay, USA", "Tyler, USA", "Wichita Falls, USA", "Lewisville, USA", "Burbank, USA", "Greeley, USA", "San Mateo, USA", "El Cajon, USA", "Jurupa Valley, USA", "Rialto, USA", "Davenport, USA", "League City, USA", "Edison, USA", "Davie, USA", "Las Cruces, USA", "South Bend, USA", "Vista, USA", "Woodbridge, USA", "Renton, USA", "Lakewood, USA", "San Angelo, USA", "Clinton, USA", 
    "Vancouver, Canada", "Porto, Portugal", "Kabul, Afghanistan", "Tirana, Albania", "Algiers, Algeria", "Andorra la Vella, Andorra", "Luanda, Angola", "Saint John's, Antigua and Barbuda", "Buenos Aires, Argentina", "Yerevan, Armenia", "Canberra, Australia", "Vienna, Austria", "Baku, Azerbaijan", "Nassau, Bahamas", "Manama, Bahrain", "Dhaka, Bangladesh", "Bridgetown, Barbados", "Minsk, Belarus", "Brussels, Belgium", "Belmopan, Belize", "Porto-Novo, Benin", "Thimphu, Bhutan", "La Paz, Bolivia", "Sarajevo, Bosnia and Herzegovina", "Gaborone, Botswana", "Brasilia, Brazil", "Bandar Seri, Begawan, Brunei", "Sofia, Bulgaria", "Ouagadougou, Burkina Faso", "Bujumbura, Burundi", "Praia, Cabo Verde", "Penh, Cambodia	Phnom", "Yaounde, Cameroon", "Ottawa, Canada", "Bangui, Central African Republic", "N'Djamena, Chad", "Santiago, Chile", "Beijing, China", "Bogotá, Colombia", "Moroni, Comoros", "Kinshasa, Democratic Republic of the Congo", "Brazzaville, Republic of the Congo", "Jose, Costa Rica	San", "Yamoussoukro, Cote d'Ivoire", "Zagreb, Croatia", "Havana, Cuba", "Nicosia, Cyprus", "Prague, Czech Republic", "Copenhagen, Denmark", "Djibouti, Djibouti", "Roseau, Dominica", "Santo Domingo, Dominican Republic", "Quito, Ecuador", "Cairo, Egypt", "San Salvador, El Salvador", "Asmara, Eritrea", "Tallinn, Estonia", "Addis Ababa, Ethiopia", "Suva, Fiji", "Helsinki, Finland", "Paris, France", "Libreville, Gabon", "Banjul, Gambia", "Tbilisi, Georgia", "Berlin, Germany", "Accra, Ghana", "Athens, Greece", "Saint George's, Grenada", "Guatemala City, Guatemala", "Conakry, Guinea", "Bissau, Guinea-Bissau", "Georgetown, Guyana", "Port-au-Prince, Haiti", "Tegucigalpa, Honduras", "Budapest, Hungary", "Reykjavik, Iceland", "Delhi, India	New", "Jakarta, Indonesia", "Tehran, Iran", "Baghdad, Iraq", "Dublin, Ireland", "Jerusalem, Israel", "Rome, Italy", "Kingston, Jamaica", "Tokyo, Japan", "Amman, Jordan", "Astana, Kazakhstan", "Nairobi, Kenya", "Tarawa, Kiribati", "Pristina, Kosovo", "Kuwait City, Kuwait", "Bishkek, Kyrgyzstan", "Vientiane, Laos", "Riga, Latvia", "Beirut, Lebanon", "Maseru, Lesotho", "Monrovia, Liberia", "Tripoli, Libya", "Vaduz, Liechtenstein", "Vilnius, Lithuania", "Luxembourg, Luxembourg", "Skopje, Macedonia (FYROM)", "Antananarivo, Madagascar", "Lilongwe, Malawi", "Lumpur, Malaysia	Kuala", "Male, Maldives", "Bamako, Mali", "Valletta, Malta", "Majuro, Marshall Islands", "Nouakchott, Mauritania", "Port Louis, Mauritius", "Mexico City, Mexico", "Palikir, Micronesia", "Chisinau, Moldova", "Monaco, Monaco", "Ulaanbaatar, Mongolia", "Podgorica, Montenegro", "Rabat, Morocco", "Maputo, Mozambique", "Naypyidaw, Myanmar (Burma)", "Windhoek, Namibia", "Kathmandu, Nepal", "Amsterdam, Netherlands", "Wellington, New Zealand", "Managua, Nicaragua", "Niamey, Niger", "Abuja, Nigeria", "Pyongyang, North Korea", "Oslo, Norway", "Muscat, Oman", "Islamabad, Pakistan", "Ngerulmud, Palau", "Panama City, Panama", "Port Moresby, Papua New Guinea", "Asunción, Paraguay", "Lima, Peru", "Manila, Philippines", "Warsaw, Poland", "Lisbon, Portugal", "Doha, Qatar", "Bucharest, Romania", "Moscow, Russia", "Kigali, Rwanda", "Basseterre, Saint Kitts and Nevis", "Castries, Saint Lucia", "Kingstown, Saint Vincent and the Grenadines", "Apia, Samoa", "San Marino, San Marino", "São Tomé, São Tome and Principe", "Riyadh, Saudi Arabia", "Dakar, Senegal", "Belgrade, Serbia", "Victoria, Seychelles", "Freetown, Sierra Leone", "Singapore, Singapore", "Bratislava, Slovakia", "Ljubljana, Slovenia", "Honiara, Solomon Islands", "Mogadishu, Somalia", "Pretoria, South Africa", "Seoul, South Korea", "Juba, South Sudan", "Madrid, Spain", "Sri Lanka, Sri JayawardenepuraKotte ", "Khartoum, Sudan", "Paramaribo, Suriname", "Mbabane, Swaziland", "Stockholm, Sweden", "Bern, Switzerland", "Damascus, Syria", "Taipei, Taiwan", "Dushanbe, Tajikistan", "Dodoma, Tanzania", "Bangkok, Thailand", "Dili, Timor-Leste", "Lomé, Togo", "Nukuʻalofa, Tonga", "Port of Spain, Trinidad and Tobago", "Tunis, Tunisia", "Ankara, Turkey", "Ashgabat, Turkmenistan", "Funafuti, Tuvalu", "Kampala, Uganda", "Kiev, Ukraine", "Abu Dhabi, United Arab Emirates", "London, United Kingdom", "Washington D.C., United States of America", "Montevideo, Uruguay", "Tashkent, Uzbekistan", "Vila, Vanuatu	Port", "Vatican City, Vatican", "Caracas, Venezuela", "Hanoi, Vietnam", "Sana'a, Yemen", "Lusaka, Zambia", "Harare, Zimbabwe"
]


# -----------------------------
PANEL_COLUMNS = 64
PANEL_ROWS = 32
TOTAL_PANELS = PANELS_HORIZONTAL * PANELS_VERTICAL
COLUMNS = PANEL_COLUMNS * PANELS_HORIZONTAL
ROWS = PANEL_ROWS * PANELS_VERTICAL

TARGET_FPS = 24.
TIME_PER_FRAME_MS = (1 / TARGET_FPS) * 1000.

VIDEO_FPS = 24.
TIME_PER_VIDEO_FRAME_MS = (1 / VIDEO_FPS) * 1000.

VIDEO_HEIGHT = 1080
VIDEO_WIDTH = (COLUMNS * VIDEO_HEIGHT) / ROWS

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s [%(levelname)s] (%(threadName)-10s) %(message)s',
                   )

led_pulse_cache = FanoutCache('/tmp/pulse-led-matrix-cache', shards=20, timeout=1)

@led_pulse_cache.memoize(typed=True, expire=None, tag='latlon_to_xy')
def convert_geopoint_to_img_coordinates(latitude, longitude, map_width, map_height):
    x = int((map_width/360.0) * (180 + longitude))
    #convert from degrees to radians
    latRad = latitude*pi/180
    mercN = log(tan((pi/4)+(latRad/2)))
    y = int((map_height/2)-(map_width*mercN/(2*pi)))
    return (x, y)

def fadeAndNormalizeColor(initial_color, percentage):
    faded_color = [c * 255 for c in initial_color]
    faded_color_np = np.array(faded_color)
    faded_color = faded_color_np + (np.array([0, 0, 0, 0]) - faded_color_np) * percentage
    faded_color = [int(c) for c in faded_color]
    return tuple(faded_color)

#@led_pulse_cache.memoize(typed=True, expire=None, tag='fade_color')
def fadeColor(initial_color, percentage):
    faded_color_np = np.array(initial_color)
    faded_color = faded_color_np + (np.array([0, 0, 0]) - faded_color_np) * percentage
    faded_color = [int(c) for c in faded_color]
    return tuple(faded_color)

@led_pulse_cache.memoize(typed=True, expire=None, tag='rgba_to_rgb')
def rgba_to_rgb(color):
    return tuple([int(c * 255) for c in color])

# Configuration for the matrix
#options = RGBMatrixOptions()
#options.rows = 32
#options.chain_length = 1
#options.parallel = 1
#options.hardware_mapping = 'adafruit-hat'

#matrix = RGBMatrix(options = options)

# Note, only "RGB" mode is supported currently.

#shared datastore
class DrawState(object):
    def __init__(self,
                 current_frame_number=0,
                 draw_orders={},
                 current_image=None
                ):
        self.current_frame_number = current_frame_number
        self.draw_orders = draw_orders
        self.current_image = current_image

class DrawOrder(object):
    def __init__(self,
                 frame_number,
                 x,
                 y,
                 color,
                 duration=TARGET_FPS,
                 quantity=0,
                 quantity_used=0,
                 drawn_frames=0
                ):
        self.frame_number = frame_number
        self.x = x
        self.y = y
        self.color = color,
        self.duration = duration
        self.drawn_frames = drawn_frames
        self.quantity = quantity
        self.quantity_used = quantity_used

    def __str__(self):
        return "frame: %-10d x: %4d y:%4d duration: %3d drawn_frames: %3d quantity: %6d / %6d color: %s" % (self.frame_number, self.x, self.y, self.duration, self.drawn_frames, self.quantity, self.quantity_used, self.color)

    def get_point(self):
        return (self.x, self.y)

    def get_color_for_quantity_used(self):
        fade_percentage = self.quantity_used / self.quantity
        # ?!?!?! WTF!!!
        return fadeColor(self.color[0], fade_percentage)


# Produce data and add to shared datastore
def produce_data(state, stop_event):
    logging.debug("Starting producing data")

    color_maps = ["Blues_r","Greens_r"]

    while not stop_event.isSet():

        events = SSEClient(EVENTS_SOURCE_URL)
        for event in events:
            data = json.loads(event.data)
            source_iso_code = data['source']['iso']
            dest_iso_code = data['dest']['iso']
            volume = int(data['volume'])

            geopoint_source = geocode.geocode_location(source_iso_code)
            geopoint_dest = geocode.geocode_location(dest_iso_code)

            # source_lat = geopoint_source.latitude
            # source_lon = geopoint_source.longitude
            # dest_lat =   geopoint_dest.latitude
            # dest_lon =   geopoint_dest.longitude

            source_lat = float(data['source']['lat'])
            source_lon = float(data['source']['lon'])
            dest_lat =   float(data['dest']['lat'])
            dest_lon =   float(data['dest']['lon'])

            fuzzy_source_lat = source_lat + random.uniform(-0.00001, 0.00001)
            fuzzy_source_lon = source_lon + random.uniform(-0.00001, 0.00001)
            fuzzy_dest_lat   = dest_lat   + random.uniform(-0.00001, 0.00001)
            fuzzy_dest_lon   = dest_lon   + random.uniform(-0.00001, 0.00001)

            source_point = convert_geopoint_to_img_coordinates(fuzzy_source_lat, fuzzy_source_lon, COLUMNS, ROWS)
            dest_point = convert_geopoint_to_img_coordinates(fuzzy_dest_lat, fuzzy_dest_lon, COLUMNS, ROWS)

            source_key = source_point
            dest_key = dest_point

            source_duration = TARGET_FPS * 5
            dest_duration = TARGET_FPS * 5

            source_color = (30, 177, 252)
            dest_color   = (251, 190, 50) 

            #print "%s -> %s # %d (%d,%d)" % (source_iso_code, dest_iso_code, volume, source_duration, dest_duration)
            if source_key in state.draw_orders:
                state.draw_orders[source_key].quantity += volume
            else:
                draw_order = DrawOrder(frame_number=state.current_frame_number,
                                       x=source_point[0], 
                                       y=source_point[1],
                                       color=source_color,
                                       duration=source_duration,
                                       quantity=volume )
                state.draw_orders[source_key] = draw_order

            if dest_key in state.draw_orders:
                state.draw_orders[dest_key].duration = volume
            else:
                draw_order = DrawOrder(frame_number=state.current_frame_number,
                                       x=dest_point[0], 
                                       y=dest_point[1],
                                       color=dest_color,
                                       duration=dest_duration,
                                       quantity=volume)
                state.draw_orders[dest_key] = draw_order

       # if PLOT_FAKE_LOCATIONS:
       #     for location in sample(LOCATIONS, 350):
       #         geopoint = geocode.geocode_location(location)
       #         key = (geopoint.latitude, geopoint.longitude)
       #         duration = randint(1, TARGET_FPS * 20)
       #         if key in state.draw_orders:
       #             #just update the duration...
       #             state.draw_orders[key].duration = duration
       #         else:
       #             location_point = convert_geopoint_to_img_coordinates(geopoint.latitude, geopoint.longitude, COLUMNS, ROWS)
       #             draw_order = DrawOrder(frame_number=state.current_frame_number,
       #                                    x=location_point[0], 
       #                                    y=location_point[1],
       #                                    color_map=sample(color_maps, 1)[0],
       #                                    duration=duration)
       #             state.draw_orders[key] = draw_order

        #sleep(0.500)


def draw_panel_outline(draw, color_map, horizontal_number, vertical_number, panel_columns, panel_rows):
    if PLOT_PANELS_OUTLINE:
        for v in range(0, vertical_number):
            for h in range(0, horizontal_number):
                x = panel_columns * h
                y = panel_rows * v
                cell_id = h + v + v * (horizontal_number - 1)
                color = color_map(cell_id)
                color_outline = fadeAndNormalizeColor(color, 0.05)
                #logging.debug("%3d: (%4d,%4d) -> (%4d,%4d) color: %s" % (cell_id, x, y, x + panel_columns, y + panel_rows, color_fill))
                draw.rectangle((x, y, x + panel_columns - 1, y + panel_rows - 1), fill=None, outline=color_outline)

def load_background_pixels(image_width, image_height):
    result = []
    if PLOT_BACKGROUND_MAP:
        bg_sf = shapefile.Reader("ne_110m_coastline/ne_110m_coastline")
        xdist = bg_sf.bbox[2] - bg_sf.bbox[0]
        ydist = bg_sf.bbox[3] - bg_sf.bbox[1]
        xratio = image_width/xdist
        yratio = image_height/ydist
        for shape in bg_sf.shapes():
            pixels = []
            for x, y in shape.points:
                px = int(COLUMNS - ((bg_sf.bbox[2] - x) * xratio))
                py = int((bg_sf.bbox[3] - y) * yratio)
                pixels.append((px, py))
            result.append(pixels)
    return result

def draw_background(draw, pixels_list):
    if PLOT_BACKGROUND_MAP:
        for pixels in pixels_list:
            draw.polygon(pixels, outline=(21,12,12), fill=None)

# Cycle through shared datastore and draw image
def draw_data(state, stop_event):
    logging.debug("Starting drawing")

    bg_pixels_list = load_background_pixels(COLUMNS, ROWS)
    panel_outline_max_colors = PANELS_HORIZONTAL * PANELS_VERTICAL
    panel_outline_color_map = plt.get_cmap('rainbow_r', panel_outline_max_colors)

    image = Image.new("RGB", (COLUMNS, ROWS))
    draw = ImageDraw.Draw(image)

    draw_background(draw, bg_pixels_list)
    draw_panel_outline(draw, panel_outline_color_map, PANELS_HORIZONTAL, PANELS_VERTICAL, PANEL_COLUMNS, PANEL_ROWS)

    while not stop_event.isSet():
        start_time = time()
        frame_number = state.current_frame_number
        state.current_frame_number += 1

        draw_orders = state.draw_orders.copy().items()

        [draw_frame_order(draw, frame_number, do, state) for do in draw_orders]

        state.current_image = image.copy()

        end_time = time()
        duration = (end_time - start_time) * 1000
        #logging.debug("finished render frame %d (%fms)" % (state.current_frame_number, duration) )
        delta = TIME_PER_FRAME_MS - duration
        if delta > 0 and delta < 0.250:
            continue
        else:
            if delta > 0:
                sleep(delta / 1000)
            else:
                if delta != 0:
                    logging.info("Slow frame! %d took %dms " % (frame_number, duration))

def draw_frame_order(draw,frame_number,draw_order_item, state):
    draw_order_key = draw_order_item[0]
    draw_order = draw_order_item[1]
    point = (draw_order.x, draw_order.y)
    if draw_order.frame_number > frame_number:
        return

    if draw_order.duration <= draw_order.drawn_frames:
        #logging.debug("order: %s " % draw_order)
        draw.point(point, (0,0,0))
        state.draw_orders.pop(draw_order_key, None)
    else:
        quantity_step = draw_order.quantity / draw_order.duration
        draw_order.quantity_used += quantity_step
        color = draw_order.get_color_for_quantity_used() 
        #logging.debug("order: %s color: %s" % (draw_order, color))
        draw.point(point, color)
        draw_order.drawn_frames += 1

def output_data(state, stop_event):
    logging.debug("Starting to push data to output")

    video_size = (VIDEO_WIDTH, VIDEO_HEIGHT)
    fourcc = cv2.VideoWriter_fourcc(*'X264')
    video = cv2.VideoWriter("animation.avi", fourcc, VIDEO_FPS, video_size, 1)

    last_frame_time = 0
    while not stop_event.isSet():
        # tight loop to refresh the led matrix as fast as possible!
        # matrix.SetImage(state.current_image, n, n)

        # only 24 frame every s
        if OUTPUT_VIDEO:
            since_last_frame = (time() - last_frame_time) * 1000
            if since_last_frame >= TIME_PER_VIDEO_FRAME_MS and state.current_image is not None:
                video_image = state.current_image.resize(video_size, Image.BOX)
                video.write(np.array(video_image))
                last_frame_time = time()

    video.release()

draw_state = DrawState()
stop_event = threading.Event()

producer_thread = threading.Thread(name='data-producer-thread', 
                                   target=produce_data, 
                                   args=(draw_state, stop_event,))
producer_thread.setDaemon(True)

draw_thread = threading.Thread(name='data-draw-thread', 
                               target=draw_data, 
                               args=(draw_state, stop_event,))
draw_thread.setDaemon(True)

output_thread = threading.Thread(name='output-thread', 
                                 target=output_data, 
                                 args=(draw_state, stop_event,))
output_thread.setDaemon(True)


producer_thread.start()
draw_thread.start()
output_thread.start()

sleep(2)
# to keep shell alive
raw_input('\n\nAny key to exit\n\n')
logging.info("Done! \n\n")
stop_event.set()

geocode.close()

producer_thread.join()
draw_thread.join()

if OUTPUT_VIDEO:
    logging.info("Saving animation.avi")
    cv2.destroyAllWindows()

# Then scroll image across matrix...
#for n in range(-COLUMNS, ROWS):  # Start off top-left, move off bottom-right
#    matrix.Clear()
#    matrix.SetImage(image, n, n)
#    sleep(0.001)

#matrix.Clear()
