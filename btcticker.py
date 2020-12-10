#!/usr/bin/python
import yaml
import json
import urllib
import socket
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import requests
import time
from waveshare_epd import epd2in7
import RPi.GPIO as GPIO
import logging
import sys
import os
from PIL import Image, ImageOps
from PIL import ImageFont
from PIL import ImageDraw
from dotenv import load_dotenv
load_dotenv()


COINAPI_KEY = os.getenv("COINAPI_KEY")

libdir = os.path.join(os.path.dirname(
    os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

mpl.use('Agg')
picdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'images')
fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'fonts')
configfile = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), 'config.yaml')
font = ImageFont.truetype(os.path.join(
    fontdir, 'googlefonts/Roboto-Medium.ttf'), 40)
fontHorizontal = ImageFont.truetype(os.path.join(
    fontdir, 'googlefonts/Roboto-Medium.ttf'), 50)
font_date = ImageFont.truetype(os.path.join(
    fontdir, 'PixelSplitter-Bold.ttf'), 11)


def internet(host="8.8.8.8", port=53, timeout=3):
    """
    Host: 8.8.8.8 (google-public-dns-a.google.com)
    OpenPort: 53/tcp
    Service: domain (DNS/TCP)
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error as ex:
        print(ex)
        return False


def getData():
    """
    The function to update the ePaper display. There are two versions of the layout. One for portrait aspect ratio, one for landscape.
    """
    logging.info("Updating Display")
    logging.info("Getting Historical Data From CoinAPI")

    try:
        url = "https://rest.coinapi.io/v1/exchangerate/BTC/CAD?apikey=" + COINAPI_KEY
        response = requests.get(url).json()
        VALUE = float(response['rate'])
        logging.info("Got Live Data From CoinAPI")
    except:
        logging.info("Failed to load data from CoinAPI")

    try:
        url = "https://rest.coinapi.io/v1/ohlcv/BTC/CAD/latest?period_id=7DAY&apikey=" + COINAPI_KEY
        rawtimeseries = requests.get(url).json()
        logging.info("Got Historic Data For Last Week")
    except:
        logging.info("Failed to 7 days data from CoinAPI")

    timeseriesstack = []
    length = len(rawtimeseries)

    i = 0
    while i < length:
        timeseriesstack.append(float(rawtimeseries[i]['price_close']))
        i += 1
    # Get the live price from coinapi

    # Add live price to timeseriesstack
    timeseriesstack.append(VALUE)
    return timeseriesstack


def makeSpark(pricestack):

    # Subtract the mean from the sparkline to make the mean appear on the plot (it's really the x axis)
    x = pricestack-np.mean(pricestack)

    fig, ax = plt.subplots(1, 1, figsize=(10, 3))
    plt.plot(x, color='k', linewidth=6)
    plt.plot(len(x)-1, x[-1], color='r', marker='o')

    # Remove the Y axis
    for k, v in ax.spines.items():
        v.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axhline(c='k', linewidth=4, linestyle=(0, (5, 2, 1, 2)))

    # Save the resulting bmp file to the images directory
    plt.savefig(os.path.join(picdir, 'spark.png'), dpi=17)
    imgspk = Image.open(os.path.join(picdir, 'spark.png'))
    file_out = os.path.join(picdir, 'spark.bmp')
    imgspk.save(file_out)


def updateDisplay(config, pricestack):

    BTC = pricestack[-1]
    bmp = Image.open(os.path.join(picdir, 'BTC.bmp'))
    bmp2 = Image.open(os.path.join(picdir, 'spark.bmp'))

    epd = epd2in7.EPD()
    epd.Init_4Gray()
    # 255: clear the image with white
    image = Image.new('L', (epd.width, epd.height), 255)
    draw = ImageDraw.Draw(image)
    draw.text((110, 80), "7day :", font=font_date, fill=0)
    draw.text((110, 95), str(
        "%+d" % round((pricestack[-1]-pricestack[1])/pricestack[-1]*100, 2))+"%", font=font_date, fill=0)
    draw.text((5, 200), "$"+format(int(round(BTC)), ","), font=font, fill=0)
    draw.text((0, 10), str(time.strftime("%c")), font=font_date, fill=0)
    image.paste(bmp, (10, 25))
    image.paste(bmp2, (10, 125))


#   If the display is inverted, invert the image usinng ImageOps
    if config['display']['inverted'] == True:
        image = ImageOps.invert(image)
#   Send the image to the screen
    epd.display_4Gray(epd.getbuffer_4Gray(image))
    epd.sleep()


def main():

    logging.basicConfig(level=logging.DEBUG)

    try:
        logging.info("epd2in7 BTC Frame")
#       Get the configuration from config.yaml

        with open(configfile) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        logging.info(config)
        GPIO.setmode(GPIO.BCM)
        config['display']['orientation'] = int(
            config['display']['orientation'])

        key1 = 5
        key2 = 6
        key3 = 13
        key4 = 19

        GPIO.setup(key1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(key4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


#       Note that there has been no data pull yet
        datapulled = False
#       Time of start
        lastcoinfetch = time.time()

        while True:
            key1state = GPIO.input(key1)
            key2state = GPIO.input(key2)
            key3state = GPIO.input(key3)
            key4state = GPIO.input(key4)

            if internet():
                if key1state == False:
                    logging.info('Force Refresh')
                    # get data
                    pricestack = getData()
                    # save time of last data update
                    lastcoinfetch = time.time()
                    # generate sparkline
                    makeSpark(pricestack)
                    # update display
                    updateDisplay(config, pricestack)
                    time.sleep(0.2)
                if (time.time() - lastcoinfetch > float(config['ticker']['updatefrequency'])) or (datapulled == False):
                    # get data
                    pricestack = getData()
                    # save time of last data update
                    lastcoinfetch = time.time()
                    # generate sparkline
                    makeSpark(pricestack)
                    # update display
                    updateDisplay(config, pricestack)
                    # Note that we've visited the internet
                    datapulled = True
                    lastcoinfetch = time.time()
                    time.sleep(0.2)

    except IOError as e:
        logging.info(e)

    except KeyboardInterrupt:
        logging.info("ctrl + c:")
        epd2in7.epdconfig.module_exit()
        exit()


if __name__ == '__main__':
    main()
