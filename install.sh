#!/bin/bash

sudo apt-get install -y \
                     python-opencv \
                     python2.7-dev \
                     python-pillow \
                     python-pip \
                     libgraphicsmagick++-dev  \
                     libwebp-dev \
                     make \
                     gcc \
                     git

pip install -r requirements.txt

git clone https://github.com/hzeller/rpi-rgb-led-matrix.git ../rpi-rgb-led-matrix

cd ../rpi-rgb-led-matrix/bindings/python/

make build-python
sudo make install-python
