#!/usr/bin/bash
cp requirements.txt /tmp/
cd /tmp/
sudo apt update

# install python dependencies
pip3 install --upgrade pip
pip3 install --user -r requirements.txt