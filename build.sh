#!/bin/bash

sudo docker build -t pastebin:latest .
sudo docker save pastebin:latest -o docker-image.tar
