# BTC Ticker

A Python3 ePaper Bitcoin (BTC) price ticker that runs on a Raspberry Pi connected to a [Waveshare 2.7 inch monochrome ePaper display](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT). The script periodically takes data from coinapi.io and prints a summary to the ePaper.

A few minutes work gives you a desk ornament that will tastefully monitor BTC's journey moonward.

![Action Shot](/images/ANI.jpg)


# Getting started

(These instructions assume that your Raspberry Pi is already connected to the Internet, happily running pip and has Python3 installed)

If you are running the Pi headless, connect to your Raspberry Pi using ssh.

Copy the files from this repository onto the Pi, or clone using:

```
git clone https://github.com/AurelienZMN/btcticker.git
cd btcticker
```


Install the required modules:

```
sudo pip3 install -r requirements.txt
sudo python3 setup.py install
```

and install the Waveshare Python module following the instructions on their [Wiki](https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT).

If you'd like the script to persist once you close the session, use [screen](https://linuxize.com/post/how-to-use-linux-screen/).

Start a screen session:

```
screen bash
```

Run the script using:

```
python3 btcticker.py
```

Detatch from the screen session using CTRL-A followed by CTRL-D

The ticker will now pull data every 10 minutes and update the display. 

# Settings

Screen orientation and screen inversion can be toggled using the on-screen keys. Update frequency can be changed in the config.yaml file (default is 600 seconds).

# Licencing

The code in this project is licensed under MIT license.
