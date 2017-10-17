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
import argparse


def fadeColor(initial_color, percentage):
    faded_color_np = np.array(initial_color)
    faded_color = faded_color_np + (np.array([0, 0, 0, 0]) - faded_color_np) * percentage
    faded_color = [int(c) for c in faded_color]
    return tuple(faded_color)

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
                 duration=10,
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

class PulseDataProducer(object):
    def __init__(self, state, stop_event, source_url, target_fps, map_width, map_height):
        self.state = state
        self.stop_event = stop_event
        self.source_url = source_url
        self.target_fps = target_fps
        self.map_width = map_width
        self.map_height = map_height

    def run(self):
        while not self.stop_event.isSet():
            events = SSEClient(self.source_url)
            for event in events:
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

                source_point = self.convert_geopoint_to_img_coordinates(source_lat, source_lon, self.map_width, self.map_height)
                dest_point = self.convert_geopoint_to_img_coordinates(dest_lat, dest_lon, self.map_width, self.map_height)

                source_key = source_point
                dest_key = dest_point

                source_duration = self.target_fps * 5
                dest_duration = self.target_fps * 5

                volume = int(max(1, min(10000, math.floor(math.log10(volume)))))

                color_wash_value = int(self.normalize_value(volume, 5, 10))
                source_color = fadeColor((30, 177, 252, 0), color_wash_value/100.)
                dest_color = fadeColor((251, 190, 50, 0), color_wash_value/100.)

                frame_number = self.state.current_frame_number
                if source_key in self.state.draw_orders:
                    self.state.draw_orders[source_key].quantity += volume
                else:
                    draw_order = DrawOrder(frame_number=frame_number,
                                           x=source_point[0],
                                           y=source_point[1],
                                           color=source_color,
                                           duration=source_duration,
                                           quantity=volume)
                    self.state.draw_orders[source_key] = draw_order

                if dest_key in self.state.draw_orders:
                    self.state.draw_orders[dest_key].duration = volume
                else:
                    draw_order = DrawOrder(frame_number=frame_number,
                                           x=dest_point[0],
                                           y=dest_point[1],
                                           color=dest_color,
                                           duration=dest_duration,
                                           quantity=volume)
                    self.state.draw_orders[dest_key] = draw_order

    def convert_geopoint_to_img_coordinates(self, latitude, longitude, width, height):
        x = int((width/360.0) * (180 + longitude))
        #convert from degrees to radians
        latRad = latitude*pi/180
        mercN = log(tan((pi/4)+(latRad/2)))
        y = int((height/2)-(width*mercN/(2*pi)))
        return (x, y)

    def normalize_value(self, value, min_value, max_value):
        order = math.ceil(math.log10(value))
        maximum = math.pow(10, order)
        minimum = math.pow(10, order - 3) if order > 3  else order
        return ((max_value-min_value)*(value-minimum)/(maximum-minimum)) + min_value

class PulseLedPanelOutput(object):
    def __init__(self, state, stop_event, led_matrix, target_fps, map_width, map_height):
        self.state = state
        self.stop_event = stop_event
        self.led_matrix = led_matrix
        self.target_fps = target_fps
        self.map_width = map_width
        self.map_height = map_height
        self.time_per_frame_ms = (1 / self.target_fps) * 1000.

    def run(self):
        image = Image.new("RGB", (self.map_width, self.map_height))
        draw = ImageDraw.Draw(image)

        double_buffer = self.led_matrix.CreateFrameCanvas()

        while not self.stop_event.isSet():
            start_time = time()
            frame_number = self.state.current_frame_number
            self.state.current_frame_number += 1

            draw_orders = self.state.draw_orders.copy().items()

            [self.draw_frame_order(draw, frame_number, do, self.state) for do in draw_orders]

            if image is not None:
                self.led_matrix.SetImage(image)
                double_buffer = self.led_matrix.SwapOnVSync(double_buffer)

            end_time = time()
            duration = (end_time - start_time) * 1000

            delta = self.time_per_frame_ms - duration
            if delta >= 0 and delta < 0.250:
                continue
            else:
                if delta > 0:
                    sleep(delta / 1000)
                else:
                    print("Slow frame! %d took %dms " % (frame_number, duration))


    def draw_frame_order(self, draw,frame_number,draw_order_item, state):
        draw_order_key = draw_order_item[0]
        draw_order = draw_order_item[1]
        point = (draw_order.x, draw_order.y)
        if draw_order.frame_number > frame_number:
            return

        if draw_order.duration <= draw_order.drawn_frames:
            draw.point(point, (0, 0, 0))
            state.draw_orders.pop(draw_order_key, None)
        else:
            quantity_step = draw_order.quantity / draw_order.duration
            draw_order.quantity_used += quantity_step
            color = draw_order.get_color_for_quantity_used()
            draw.point(point, color)
            draw_order.drawn_frames += 1

class PulseLedView(object):
    def __init__(self, *args, **kwargs):
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument("-r", "--led-rows", action="store", help="Display rows. 16 for 16x32, 32 for 32x32. Default: 32", default=32, type=int)
        self.parser.add_argument("-c", "--led-chain", action="store", help="Daisy-chained boards. Default: 2.", default=2, type=int)
        self.parser.add_argument("-P", "--led-parallel", action="store", help="For Plus-models or RPi2: parallel chains. 1..3. Default: 1", default=1, type=int)
        self.parser.add_argument("-p", "--led-pwm-bits", action="store", help="Bits used for PWM. Something between 1..11. Default: 11", default=11, type=int)
        self.parser.add_argument("-b", "--led-brightness", action="store", help="Sets brightness level. Default: 100. Range: 1..100", default=100, type=int)
        self.parser.add_argument("-m", "--led-gpio-mapping", help="Hardware Mapping: regular, adafruit-hat, adafruit-hat-pwm Default: adafruit-hat" , choices=['regular', 'adafruit-hat', 'adafruit-hat-pwm'], default="adafruit-hat", type=str)
        self.parser.add_argument("--led-scan-mode", action="store", help="Progressive or interlaced scan. 0 Progressive, 1 Interlaced (default)", default=1, choices=range(2), type=int)
        self.parser.add_argument("--led-pwm-lsb-nanoseconds", action="store", help="Base time-unit for the on-time in the lowest significant bit in nanoseconds. Default: 130", default=130, type=int)
        self.parser.add_argument("--led-show-refresh", action="store_true", help="Shows the current refresh rate of the LED panel")
        self.parser.add_argument("--led-slowdown-gpio", action="store", help="Slow down writing to GPIO. Range: 1..100. Default: 1", choices=range(3), type=int)
        self.parser.add_argument("--led-no-hardware-pulse", action="store", help="Don't use hardware pin-pulse generation")
        self.parser.add_argument("--led-rgb-sequence", action="store", help="Switch if your matrix has led colors swapped. Default: RGB", default="RGB", type=str)
        self.parser.add_argument("--cache-location", action="store", help="Location of the cache folder Default: ./pulse-cache", default="./pulse-cache", type=str)
        self.parser.add_argument("--log-level", action="store", help="Log level Default: DEBUG", default="DEBUG", type=str)

    def initialize_and_run(self):
        self.args = self.parser.parse_args()

        logging_level = logging.getLevelName(self.args.log_level)
        self.logging = logging.basicConfig(level=logging_level, format='%(asctime)-15s [%(levelname)s] (%(threadName)-10s) %(message)s', )

        logging.info("Initializing LED matrix...")
        options = RGBMatrixOptions()

        if self.args.led_gpio_mapping != None:
          options.hardware_mapping = self.args.led_gpio_mapping

        options.rows = self.args.led_rows
        options.chain_length = self.args.led_chain
        options.parallel = self.args.led_parallel
        options.pwm_bits = self.args.led_pwm_bits
        options.brightness = self.args.led_brightness
        options.pwm_lsb_nanoseconds = self.args.led_pwm_lsb_nanoseconds
        options.led_rgb_sequence = self.args.led_rgb_sequence

        if self.args.led_show_refresh:
          options.show_refresh_rate = 1

        if self.args.led_slowdown_gpio != None:
            options.gpio_slowdown = self.args.led_slowdown_gpio

        if self.args.led_no_hardware_pulse:
          options.disable_hardware_pulsing = True

        self.matrix = RGBMatrix(options = options)

        #self.led_pulse_cache = FanoutCache(self.args.cache_location, shards=20, timeout=1)
        self.columns = self.args.led_rows * self.args.led_chain
        self.rows = 32

        # TODO: configure me
        self.pulse_events_url = "http://192.168.1.7:9201/events"

        # TODO: configure me
        self.target_fps = 24.
        self.time_per_frame_ms = (1 / self.target_fps) * 1000.

        self.draw_state = DrawState()
        self.stop_event = threading.Event()

        try:
            # Start loop
            print("Press CTRL-C to stop sample")
            self.run()
        except KeyboardInterrupt:
            print("Exiting\n")
            self.stop_event.set()
            sys.exit(0)

        return True

    def draw_text(self, matrix, x, y, text, size = 20):
        font = ImageFont.truetype('fonts/FiraCode-Regular.ttf', size)
        image = Image.new("RGB", (self.columns, self.rows))
        draw = ImageDraw.Draw(image)

        text_width, text_height = font.getsize(text)

        draw.text((x - text_width/2 ,y - text_height/2), text, font=font, fill=(41,161,228,0))

        self.matrix.SetImage(image.convert('RGB'))

    def draw_logo(self):
        logging.info("Display TS logo...")
        logo_image = Image.open("images/tradeshift.jpg")
        logo_image.thumbnail((self.columns, self.rows), Image.ANTIALIAS)
        logo_image_width, logo_image_height = logo_image.size

        x = (self.columns - logo_image_width) / 2
        y = (self.rows - logo_image_height) / 2

        self.matrix.SetImage(logo_image.convert('RGB'), x, y)

    def countdown(self):
        for value in reversed(range(0, 10)):
            self.draw_text(self.matrix, (self.columns / 2), (self.rows / 2), str(value), 20)
            sleep(0.125)

        self.matrix.Clear()

    def run(self):
        self.draw_logo()
        sleep(2)
        self.countdown()

        pulse_data_producer = PulseDataProducer(self.draw_state,
                                                self.stop_event,
                                                self.pulse_events_url,
                                                self.target_fps,
                                                self.columns,
                                                self.rows
                                               )

        pulse_led_panel_output = PulseLedPanelOutput( self.draw_state,
                                                self.stop_event,
                                                self.matrix,
                                                self.target_fps,
                                                self.columns,
                                                self.rows
                                               )

        producer_thread = threading.Thread(name='data-producer-thread',
                                   target=pulse_data_producer.run)
        producer_thread.setDaemon(True)
        producer_thread.start()

        draw_thread = threading.Thread(name='data-draw-thread',
                                       target=pulse_led_panel_output.run,)
        draw_thread.setDaemon(True)
        draw_thread.start()

        producer_thread.join()
        draw_thread.join()

# Main function
if __name__ == "__main__":
    pulse_led_view = PulseLedView()
    if (not pulse_led_view.initialize_and_run()):
        pulse_led_view.print_help()
