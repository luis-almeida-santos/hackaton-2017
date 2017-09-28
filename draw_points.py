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
import time
import signal
import sys
import cv2

panels_horizontal = 5
panels_vertical = 5

draw_panels_outline = False
draw_world_bg = True
draw_locations = True

output_gif = True
# world capitals, to test only
#locations = ["San Francisco, USA", "Los Angeles, USA", "Portland, Oregon, USA", "Las Vegas, Nevada, USA"]
locations = [
    "New York, USA", "Los Angeles, USA", "Chicago, USA", "Houston, USA", "Phoenix, USA", "Philadelphia, USA", "San Antonio, USA", "San Diego, USA", "Dallas, USA", "San Jose, USA", "Austin, USA", "Jacksonville, USA", "San Francisco, USA", "Columbus, USA", "Indianapolis, USA", "Fort Worth, USA", "Charlotte, USA", "Seattle, USA", "Denver, USA", "El Paso, USA", "Washington, USA", "Boston, USA", "Detroit, USA", "Nashville, USA", "Memphis, USA", "Portland, USA", "Oklahoma City, USA", "Las Vegas, USA", "Louisville, USA", "Baltimore, USA", "Milwaukee, USA", "Albuquerque, USA", "Tucson, USA", "Fresno, USA", "Sacramento, USA", "Mesa, USA", "Kansas City, USA", "Atlanta, USA", "Long Beach, USA", "Colorado Springs, USA", "Raleigh, USA", "Miami, USA", "Virginia Beach, USA", "Omaha, USA", "Oakland, USA", "Minneapolis, USA", "Tulsa, USA", "Arlington, USA", "New Orleans, USA", "Wichita, USA", "Cleveland, USA", "Tampa, USA", "Bakersfield, USA", "Aurora, USA", "Honolulu, USA", "Anaheim, USA", "Santa Ana, USA", "Corpus Christi, USA", "Riverside, USA", "Lexington, USA", "Stockton, USA", "Pittsburgh, USA", "Saint Paul, USA", "Cincinnati, USA", "Anchorage, USA", "Henderson, USA", "Greensboro, USA", "Plano, USA", "Newark, USA", "Lincoln, USA", "Toledo, USA", "Orlando, USA", "Chula Vista, USA", "Irvine, USA", "Fort Wayne, USA", "Jersey City, USA", "Durham, USA", "Laredo, USA", "Buffalo, USA", "Madison, USA", "Lubbock, USA", "Chandler, USA", "Scottsdale, USA", "Glendale, USA", "Reno, USA", "Norfolk, USA", "North Las Vegas, USA", "Irving, USA", "Chesapeake, USA", "Gilbert, USA", "Hialeah, USA", "Garland, USA", "Fremont, USA", "Baton Rouge, USA", "Richmond, USA", "Boise, USA", "San Bernardino, USA", "Spokane, USA", "Des Moines, USA", "Modesto, USA", "Birmingham, USA", "Tacoma, USA", "Fontana, USA", "Rochester, USA", "Oxnard, USA", "Moreno Valley, USA", "Fayetteville, USA", "Aurora, USA", "Glendale, USA", "Yonkers, USA", "Huntington Beach, USA", "Montgomery, USA", "Amarillo, USA", "Little Rock, USA", "Akron, USA", "Columbus, USA", "Augusta, USA", "Grand Rapids, USA", "Shreveport, USA", "Salt Lake City, USA", "Huntsville, USA", "Mobile, USA", "Tallahassee, USA", "Grand Prairie, USA", "Overland Park, USA", "Knoxville, USA", "Worcester, USA", "Brownsville, USA", "Tempe, USA", "Santa Clarita, USA", "Newport News, USA", "Cape Coral, USA", "Providence, USA", "Fort Lauderdale, USA", "Chattanooga, USA", "Rancho Cucamonga, USA", "Oceanside, USA", "Santa Rosa, USA", "Garden Grove, USA", "Vancouver, USA", "Sioux Falls, USA", "Ontario, USA", "McKinney, USA", "Elk Grove, USA", "Jackson, USA", "Pembroke Pines, USA", "Salem, USA", "Springfield, USA", "Corona, USA", "Eugene, USA", "Fort Collins, USA", "Peoria, USA", "Frisco, USA", "Cary, USA", "Lancaster, USA", "Hayward, USA", "Palmdale, USA", "Salinas, USA", "Alexandria, USA", "Lakewood, USA", "Springfield, USA", "Pasadena, USA", "Sunnyvale, USA", "Macon, USA", "Pomona, USA", "Hollywood, USA", "Kansas City, USA", "Escondido, USA", "Clarksville, USA", "Joliet, USA", "Rockford, USA", "Torrance, USA", "Naperville, USA", "Paterson, USA", "Savannah, USA", "Bridgeport, USA", "Mesquite, USA", "Killeen, USA", "Syracuse, USA", "McAllen, USA", "Pasadena, USA", "Bellevue, USA", "Fullerton, USA", "Orange, USA", "Dayton, USA", "Miramar, USA", "Thornton, USA", "West Valley City, USA", "Olathe, USA", "Hampton, USA", "Warren, USA", "Midland, USA", "Waco, USA", "Charleston, USA", "Columbia, USA", "Denton, USA", "Carrollton, USA", "Surprise, USA", "Roseville, USA", "Sterling Heights, USA", "Murfreesboro, USA", "Gainesville, USA", "Cedar Rapids, USA", "Visalia, USA", "Coral Springs, USA", "New Haven, USA", "Stamford, USA", "Thousand Oaks, USA", "Concord, USA", "Elizabeth, USA", "Lafayette, USA", "Kent, USA", "Topeka, USA", "Simi Valley, USA", "Santa Clara, USA", "Athens, USA", "Hartford, USA", "Victorville, USA", "Abilene, USA", "Norman, USA", "Vallejo, USA", "Berkeley, USA", "Round Rock, USA", "Ann Arbor, USA", "Fargo, USA", "Columbia, USA", "Allentown, USA", "Evansville, USA", "Beaumont, USA", "Odessa, USA", "Wilmington, USA", "Arvada, USA", "Independence, USA", "Provo, USA", "Lansing, USA", "El Monte, USA", "Springfield, USA", "Fairfield, USA", "Clearwater, USA", "Peoria, USA", "Rochester, USA", "Carlsbad, USA", "Westminster, USA", "West Jordan, USA", "Pearland, USA", "Richardson, USA", "Downey, USA", "Miami Gardens, USA", "Temecula, USA", "Costa Mesa, USA", "College Station, USA", "Elgin, USA", "Murrieta, USA", "Gresham, USA", "High Point, USA", "Antioch, USA", "Inglewood, USA", "Cambridge, USA", "Lowell, USA", "Manchester, USA", "Billings, USA", "Pueblo, USA", "Palm Bay, USA", "Centennial, USA", "Richmond, USA", "Ventura, USA", "Pompano Beach, USA", "North Charleston, USA", "Everett, USA", "Waterbury, USA", "West Palm Beach, USA", "Boulder, USA", "West Covina, USA", "Broken Arrow, USA", "Clovis, USA", "Daly City, USA", "Lakeland, USA", "Santa Maria, USA", "Norwalk, USA", "Sandy Springs, USA", "Hillsboro, USA", "Green Bay, USA", "Tyler, USA", "Wichita Falls, USA", "Lewisville, USA", "Burbank, USA", "Greeley, USA", "San Mateo, USA", "El Cajon, USA", "Jurupa Valley, USA", "Rialto, USA", "Davenport, USA", "League City, USA", "Edison, USA", "Davie, USA", "Las Cruces, USA", "South Bend, USA", "Vista, USA", "Woodbridge, USA", "Renton, USA", "Lakewood, USA", "San Angelo, USA", "Clinton, USA", 
    "Vancouver, Canada", "Porto, Portugal", "Kabul, Afghanistan", "Tirana, Albania", "Algiers, Algeria", "Andorra la Vella, Andorra", "Luanda, Angola", "Saint John's, Antigua and Barbuda", "Buenos Aires, Argentina", "Yerevan, Armenia", "Canberra, Australia", "Vienna, Austria", "Baku, Azerbaijan", "Nassau, Bahamas", "Manama, Bahrain", "Dhaka, Bangladesh", "Bridgetown, Barbados", "Minsk, Belarus", "Brussels, Belgium", "Belmopan, Belize", "Porto-Novo, Benin", "Thimphu, Bhutan", "La Paz, Bolivia", "Sarajevo, Bosnia and Herzegovina", "Gaborone, Botswana", "Brasilia, Brazil", "Bandar Seri, Begawan, Brunei", "Sofia, Bulgaria", "Ouagadougou, Burkina Faso", "Bujumbura, Burundi", "Praia, Cabo Verde", "Penh, Cambodia	Phnom", "Yaounde, Cameroon", "Ottawa, Canada", "Bangui, Central African Republic", "N'Djamena, Chad", "Santiago, Chile", "Beijing, China", "Bogotá, Colombia", "Moroni, Comoros", "Kinshasa, Democratic Republic of the Congo", "Brazzaville, Republic of the Congo", "Jose, Costa Rica	San", "Yamoussoukro, Cote d'Ivoire", "Zagreb, Croatia", "Havana, Cuba", "Nicosia, Cyprus", "Prague, Czech Republic", "Copenhagen, Denmark", "Djibouti, Djibouti", "Roseau, Dominica", "Santo Domingo, Dominican Republic", "Quito, Ecuador", "Cairo, Egypt", "San Salvador, El Salvador", "Asmara, Eritrea", "Tallinn, Estonia", "Addis Ababa, Ethiopia", "Suva, Fiji", "Helsinki, Finland", "Paris, France", "Libreville, Gabon", "Banjul, Gambia", "Tbilisi, Georgia", "Berlin, Germany", "Accra, Ghana", "Athens, Greece", "Saint George's, Grenada", "Guatemala City, Guatemala", "Conakry, Guinea", "Bissau, Guinea-Bissau", "Georgetown, Guyana", "Port-au-Prince, Haiti", "Tegucigalpa, Honduras", "Budapest, Hungary", "Reykjavik, Iceland", "Delhi, India	New", "Jakarta, Indonesia", "Tehran, Iran", "Baghdad, Iraq", "Dublin, Ireland", "Jerusalem, Israel", "Rome, Italy", "Kingston, Jamaica", "Tokyo, Japan", "Amman, Jordan", "Astana, Kazakhstan", "Nairobi, Kenya", "Tarawa, Kiribati", "Pristina, Kosovo", "Kuwait City, Kuwait", "Bishkek, Kyrgyzstan", "Vientiane, Laos", "Riga, Latvia", "Beirut, Lebanon", "Maseru, Lesotho", "Monrovia, Liberia", "Tripoli, Libya", "Vaduz, Liechtenstein", "Vilnius, Lithuania", "Luxembourg, Luxembourg", "Skopje, Macedonia (FYROM)", "Antananarivo, Madagascar", "Lilongwe, Malawi", "Lumpur, Malaysia	Kuala", "Male, Maldives", "Bamako, Mali", "Valletta, Malta", "Majuro, Marshall Islands", "Nouakchott, Mauritania", "Port Louis, Mauritius", "Mexico City, Mexico", "Palikir, Micronesia", "Chisinau, Moldova", "Monaco, Monaco", "Ulaanbaatar, Mongolia", "Podgorica, Montenegro", "Rabat, Morocco", "Maputo, Mozambique", "Naypyidaw, Myanmar (Burma)", "Windhoek, Namibia", "Kathmandu, Nepal", "Amsterdam, Netherlands", "Wellington, New Zealand", "Managua, Nicaragua", "Niamey, Niger", "Abuja, Nigeria", "Pyongyang, North Korea", "Oslo, Norway", "Muscat, Oman", "Islamabad, Pakistan", "Ngerulmud, Palau", "Panama City, Panama", "Port Moresby, Papua New Guinea", "Asunción, Paraguay", "Lima, Peru", "Manila, Philippines", "Warsaw, Poland", "Lisbon, Portugal", "Doha, Qatar", "Bucharest, Romania", "Moscow, Russia", "Kigali, Rwanda", "Basseterre, Saint Kitts and Nevis", "Castries, Saint Lucia", "Kingstown, Saint Vincent and the Grenadines", "Apia, Samoa", "San Marino, San Marino", "São Tomé, São Tome and Principe", "Riyadh, Saudi Arabia", "Dakar, Senegal", "Belgrade, Serbia", "Victoria, Seychelles", "Freetown, Sierra Leone", "Singapore, Singapore", "Bratislava, Slovakia", "Ljubljana, Slovenia", "Honiara, Solomon Islands", "Mogadishu, Somalia", "Pretoria, South Africa", "Seoul, South Korea", "Juba, South Sudan", "Madrid, Spain", "Sri Lanka, Sri JayawardenepuraKotte ", "Khartoum, Sudan", "Paramaribo, Suriname", "Mbabane, Swaziland", "Stockholm, Sweden", "Bern, Switzerland", "Damascus, Syria", "Taipei, Taiwan", "Dushanbe, Tajikistan", "Dodoma, Tanzania", "Bangkok, Thailand", "Dili, Timor-Leste", "Lomé, Togo", "Nukuʻalofa, Tonga", "Port of Spain, Trinidad and Tobago", "Tunis, Tunisia", "Ankara, Turkey", "Ashgabat, Turkmenistan", "Funafuti, Tuvalu", "Kampala, Uganda", "Kiev, Ukraine", "Abu Dhabi, United Arab Emirates", "London, United Kingdom", "Washington D.C., United States of America", "Montevideo, Uruguay", "Tashkent, Uzbekistan", "Vila, Vanuatu	Port", "Vatican City, Vatican", "Caracas, Venezuela", "Hanoi, Vietnam", "Sana'a, Yemen", "Lusaka, Zambia", "Harare, Zimbabwe"]


# -----------------------------
panel_columns = 64
panel_rows = 32
total_panels = panels_horizontal * panels_vertical
columns = panel_columns * panels_horizontal
rows = panel_rows * panels_vertical

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)-15s [%(levelname)s] (%(threadName)-10s) %(message)s',
                   )

def convert_geopoint_to_img_coordinates(latitude, longitude):
    x = int((columns/360.0) * (180 + longitude))
    y = int((rows/180.0) * (90 - latitude))
    return (x, y)

def fadeAndNormalizeColor(initial_color, percentage):
    faded_color = map(lambda v: v * 255, initial_color)
    faded_color_np = np.array(faded_color)
    faded_color = faded_color_np + (np.array([0, 0, 0, 0]) - faded_color_np) * percentage
    faded_color = map(lambda v: int(v), faded_color)
    return tuple(faded_color)

def rgba_to_rgb(color):
    return tuple(map(lambda v: int(v * 255), color))


# Configuration for the matrix
#options = RGBMatrixOptions()
#options.rows = 32
#options.chain_length = 1
#options.parallel = 1
#options.hardware_mapping = 'adafruit-hat'

#matrix = RGBMatrix(options = options)

# Note, only "RGB" mode is supported currently.
image = Image.new("RGB", (columns, rows))
draw = ImageDraw.Draw(image)

if draw_world_bg:
    bg_sf = shapefile.Reader("ne_10m_coastline/ne_10m_coastline")
    xdist = bg_sf.bbox[2] - bg_sf.bbox[0]
    ydist = bg_sf.bbox[3] - bg_sf.bbox[1]
    xratio = columns/xdist
    yratio = rows/ydist
    
    for shape in bg_sf.shapes():
        pixels = []
        for x, y in shape.points:
            px = int(columns - ((bg_sf.bbox[2] - x) * xratio))
            py = int((bg_sf.bbox[3] - y) * yratio)
            #print (px, py)
            pixels.append((px, py))
        draw.polygon(pixels, outline=(25, 25, 25), fill=(0, 0, 0))

#draw outline of panels
if draw_panels_outline:
    max_colors = panels_horizontal * panels_vertical
    color_map = plt.get_cmap('rainbow_r', max_colors)
    for v in range(0, panels_vertical):
        for h in range(0, panels_horizontal):
            x = (panel_columns * h)
            y = (panel_rows * v)
            cell_id = h + v  +  v * (panels_horizontal - 1 )
            color = color_map(cell_id)
            color_outline = fadeAndNormalizeColor(color, 0.25)
            color_fill = fadeAndNormalizeColor(color, 0.85)
            logging.debug("%3d: (%4d,%4d) -> (%4d,%4d) color: %s" % (cell_id, x, y, x + panel_columns, y + panel_rows, color_fill))
            draw.rectangle((x, y, x + panel_columns - 1 , y + panel_rows - 1), fill=None, outline=color_outline)

#shared datastore
class DrawState(object):
    def __init__(self,
                 current_frame_number = 0,
                 draw_orders = {}
                ):
        self.current_frame_number = current_frame_number
        self.draw_orders = draw_orders

class DrawOrder(object):
    def __init__(self,
                 frame_number,
                 x,
                 y,
                 color_map = "Blues",
                 duration = 1,
                 drawn_frames = 0
        ):
        self.frame_number = frame_number
        self.x = x
        self.y = y
        self.color_map = color_map
        self.duration = duration
        self.drawn_frames = drawn_frames

    def __str__(self):
     return "frame: %-10d x: %4d y:%4d duration: %3d drawn_frames: %3d color map: %s" % (self.frame_number, self.x, self.y, self.duration, self.drawn_frames, self.color_map)
    def get_point(self):
        return (self.x, self.y)


# Produce data and add to shared datastore
def produce_data(state, stop_event):
    logging.debug("Starting producing data")
    
    while not stop_event.isSet():
        
        if draw_locations:
            for location in sample(locations, 50):
                geopoint = geocode.geocode_location(location)
                key = (geopoint.latitude, geopoint.longitude)
                duration = randint(1, 1000)
                if key in state.draw_orders:
                    #just update the duration...
                    state.draw_orders[key].duration = duration
                else:
                    location_point = convert_geopoint_to_img_coordinates(geopoint.latitude, geopoint.longitude)
                    draw_order = DrawOrder(frame_number=state.current_frame_number,
                                        x=location_point[0], 
                                        y=location_point[1],
                                        color_map="rainbow",
                                        duration=duration)
                    state.draw_orders[key] = draw_order

        time.sleep(0.250)


# Cycle through shared datastore and draw
def draw_data(state, stop_event):
    logging.debug("Starting drawing")

    time.sleep(1)
    while not stop_event.isSet():
        frame_number = state.current_frame_number
        state.current_frame_number += 1
        #logging.debug("drawing frame %d", state.current_frame_number)
        start_time = time.time()
        orders = state.draw_orders.copy(    )
        for draw_order_item in orders.items():
            draw_order_key = draw_order_item[0]
            draw_order =  draw_order_item[1]
            if draw_order.frame_number > frame_number:
                continue

            if draw_order.duration <= draw_order.drawn_frames:
                #logging.debug("order: %s " % draw_order)
                draw.point(draw_order.get_point(), (0,0,0))
                state.draw_orders.pop(draw_order_key, None)
            else:
                color_map = color_map = plt.get_cmap(draw_order.color_map, draw_order.duration)
                color = rgba_to_rgb(color_map(draw_order.duration - draw_order.drawn_frames))
                # logging.debug("order: %s color: %s" % (draw_order, color))
                draw.point(draw_order.get_point(), color)
                draw_order.drawn_frames += 1

        if output_gif:
            video.write( np.array(image) )

        end_time = time.time()
        #print (end_time - start_time) * 1000
        #logging.debug("finished render frame %d (%fms %d points)" % (state.current_frame_number, (end_time - start_time) * 1000, len(orders)) )



draw_state = DrawState()
stop_event = threading.Event()
fourcc = cv2.VideoWriter_fourcc(*'X264')
video = cv2.VideoWriter("animation.avi", fourcc, 18.0, (columns * 1 ,rows * 1), 1)

producer_thread = threading.Thread(name='data-producer-thread', target=produce_data, args=(draw_state, stop_event, ) )
producer_thread.setDaemon(True)
producer_thread.start()

draw_thread = threading.Thread(name='data-draw-thread', target=draw_data, args=(draw_state, stop_event, ) )
draw_thread.start()

# to keep shell alive
raw_input('\n\nAny key to exit\n\n')
logging.info("Done! \n\n")
stop_event.set()


geocode.close()

if output_gif:
    logging.info("Saving animation.avi")
    cv2.destroyAllWindows()
    video.release()

# Then scroll image across matrix...
#for n in range(-columns, rows):  # Start off top-left, move off bottom-right
#    matrix.Clear()
#    matrix.SetImage(image, n, n)
#    time.sleep(0.001)

#matrix.Clear()
