#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
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
import math
from math import pi, tan, log
from time import sleep, time
from diskcache import FanoutCache
from sseclient import SSEClient
import json
import random


PANELS_HORIZONTAL = 1
PANELS_VERTICAL = 1

PLOT_PANELS_OUTLINE = False
PLOT_BACKGROUND_MAP = True

EVENTS_SOURCE_URL="http://192.168.1.7:9201/events"

CACHE_LOCATION='./pulse-led-matrix-cache'

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

led_pulse_cache = FanoutCache(CACHE_LOCATION, shards=20, timeout=1)

#@led_pulse_cache.memoize(typed=True, expire=None, tag='latlon_to_xy')
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
    faded_color = faded_color_np + (np.array([0, 0, 0, 0]) - faded_color_np) * percentage
    faded_color = [int(c) for c in faded_color]
    return tuple(faded_color)

#@led_pulse_cache.memoize(typed=True, expire=None, tag='rgba_to_rgb')
def rgba_to_rgb(color):
    return tuple([int(c * 255) for c in color])

def countdown(matrix):
    for value in reversed(range(0, 10)):
        draw_text(matrix, (COLUMNS / 2), (ROWS / 2), str(value), 20)
        sleep(0.25)

    matrix.Clear()

def draw_text(matrix, x, y, text, size = 20):
    font = ImageFont.truetype('fonts/FiraCode-Regular.ttf', size)
    image = Image.new("RGB", (COLUMNS, ROWS))
    draw = ImageDraw.Draw(image)

    text_width, text_height = font.getsize(text)

    draw.text((x - text_width/2 ,y - text_height/2), text, font=font, fill=(41,161,228,0))

    matrix.SetImage(image.convert('RGB'))

def draw_logo(matrix):
    logging.info("Display TS logo...")
    logo_image = Image.open("images/tradeshift.jpg")
    logo_image.thumbnail((COLUMNS, ROWS), Image.ANTIALIAS)
    logo_image_width, logo_image_height = logo_image.size

    x = (COLUMNS - logo_image_width) / 2
    y = (ROWS - logo_image_height) / 2

    led_matrix.SetImage(logo_image.convert('RGB'), x, y)

    logging.info("Done displaying logo")

#shared datastore
class DrawState(object):
    def __init__(self,
                 current_frame_number=0,
                 draw_orders={}
                ):
        self.current_frame_number = current_frame_number
        self.draw_orders = draw_orders

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
        return fadeColor(self.color[0], fade_percentage)

# Produce data and add to shared datastore
def produce_data(state, stop_event):
    logging.debug("Starting producing data")

    while not stop_event.isSet():

        events = SSEClient(EVENTS_SOURCE_URL)
        for event in events:
            logging.debug("Event received!")
            if event.data is None or not event.data:
                continue

            data = json.loads(event.data)
            source_iso_code = data['source']['iso']
            dest_iso_code = data['dest']['iso']
            volume = int(data['volume'])

            source_lat = float(data['source']['lat'])
            source_lon = float(data['source']['lon'])
            dest_lat = float(data['dest']['lat'])
            dest_lon = float(data['dest']['lon'])

            source_point = convert_geopoint_to_img_coordinates(source_lat, source_lon, COLUMNS, ROWS)
            dest_point = convert_geopoint_to_img_coordinates(dest_lat, dest_lon, COLUMNS, ROWS)

            logging.debug("new point at: %d,%d)" % (source_point[0] , source_point[1]) )
            logging.debug("new point at: %d,%d)" % (dest_point[0] , dest_point[1]) )

            source_key = source_point
            dest_key = dest_point

            source_duration = TARGET_FPS * 5
            dest_duration = TARGET_FPS * 5

            volume = int(max(1, min(10000, math.floor(math.log10(volume)))))

            color_wash_value = int(normalize_value(volume, 5, 10))
            source_color = fadeColor((30, 177, 252, 0), color_wash_value/100.)
            dest_color = fadeColor((251, 190, 50, 0), color_wash_value/100.)

            logging.debug("%s -> %s # %d (%d,%d)" % (source_iso_code, dest_iso_code, volume, source_duration, dest_duration))

            if source_key in state.draw_orders:
                state.draw_orders[source_key].quantity += volume
            else:
                draw_order = DrawOrder(frame_number=state.current_frame_number,
                                       x=source_point[0],
                                       y=source_point[1],
                                       color=source_color,
                                       duration=source_duration,
                                       quantity=volume)
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

def normalize_value(value, min_value, max_value):
    order = math.ceil(math.log10(value))
    maximum = math.pow(10, order)
    minimum = math.pow(10, order - 3) if order > 3  else order
    return ((max_value-min_value)*(value-minimum)/(maximum-minimum)) + min_value

def draw_panel_outline(draw, color_map, horizontal_number, vertical_number, panel_columns, panel_rows):
    if PLOT_PANELS_OUTLINE:
        for v in range(0, vertical_number):
            for h in range(0, horizontal_number):
                x = panel_columns * h
                y = panel_rows * v
                cell_id = h + v + v * (horizontal_number - 1)
                color = color_map(cell_id)
                color_outline = fadeAndNormalizeColor(color, 0.05)
                draw.rectangle((x, y, x + panel_columns - 1, y + panel_rows - 1), fill=None, outline=color_outline)

def load_background_pixels(image_width, image_height):
    result = []
    if PLOT_BACKGROUND_MAP:
        bg_sf = shapefile.Reader("ne_110m_coastline/ne_110m_coastline.shp")
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
            draw.polygon(pixels, outline=(40, 25, 25), fill=None)

# Cycle through shared datastore and draw image
def draw_data(state, led_matrix, stop_event):
    logging.debug("Starting drawing")

    bg_pixels_list = load_background_pixels(COLUMNS, ROWS)
    panel_outline_max_colors = PANELS_HORIZONTAL * PANELS_VERTICAL
    panel_outline_color_map = plt.get_cmap('rainbow_r', panel_outline_max_colors)

    image = Image.new("RGB", (COLUMNS, ROWS))
    draw = ImageDraw.Draw(image)

    draw_background(draw, bg_pixels_list)
    draw_panel_outline(draw,
                       panel_outline_color_map,
                       PANELS_HORIZONTAL,
                       PANELS_VERTICAL,
                       PANEL_COLUMNS,
                       PANEL_ROWS)

    double_buffer = led_matrix.CreateFrameCanvas()

    while not stop_event.isSet():
        start_time = time()
        frame_number = state.current_frame_number
        state.current_frame_number += 1

        draw_orders = state.draw_orders.copy().items()

        [draw_frame_order(draw, frame_number, do, state) for do in draw_orders]
        logging.debug("Frame %d drawn" % frame_number)

        if image is not None:
            led_matrix.SetImage(image)
            double_buffer = led_matrix.SwapOnVSync(double_buffer)

        end_time = time()
        duration = (end_time - start_time) * 1000
        logging.debug("finished render frame %d (%fms)" % (state.current_frame_number, duration) )
        delta = TIME_PER_FRAME_MS - duration
        if delta >= 0 and delta < 0.250:
            continue
        else:
            if delta > 0:
                sleep(delta / 1000)
            else:
                logging.info("Slow frame! %d took %dms " % (frame_number, duration))

def draw_frame_order(draw,frame_number,draw_order_item, state):
    draw_order_key = draw_order_item[0]
    draw_order = draw_order_item[1]
    point = (draw_order.x, draw_order.y)
    if draw_order.frame_number > frame_number:
        return

    if draw_order.duration <= draw_order.drawn_frames:
        logging.debug("order: %s " % draw_order)
        draw.point(point, (0, 0, 0))
        state.draw_orders.pop(draw_order_key, None)
    else:
        quantity_step = draw_order.quantity / draw_order.duration
        draw_order.quantity_used += quantity_step
        color = draw_order.get_color_for_quantity_used()
        logging.debug("order: %s color: %s" % (draw_order, color))
        draw.point(point, color)
        draw_order.drawn_frames += 1


logging.info("Initializing internals...")
draw_state = DrawState()
stop_event = threading.Event()

logging.info("Initializing LED matrix...")

# LED matrix
## Configuration for the matrix
options = RGBMatrixOptions()
options.rows = 32
options.chain_length = 2
options.parallel = 1
options.hardware_mapping = 'adafruit-hat'
led_matrix = RGBMatrix(options = options)
led_matrix.Clear()
logging.info("Done intializing LED matrix")

producer_thread = threading.Thread(name='data-producer-thread',
                                   target=produce_data,
                                   args=(draw_state, stop_event,))
producer_thread.setDaemon(True)
producer_thread.start()

logging.info("Drawing startup sequence")
draw_logo(led_matrix)
sleep(2)
countdown(led_matrix)

led_matrix.Clear()

draw_thread = threading.Thread(name='data-draw-thread',
                               target=draw_data,
                               args=(draw_state, led_matrix, stop_event,))
draw_thread.setDaemon(True)
draw_thread.start()

# to keep shell alive
raw_input('\n\nAny key to exit\n\n')
logging.info("Done! \n\n")
stop_event.set()

producer_thread.join()
draw_thread.join()

led_matrix.Clear()