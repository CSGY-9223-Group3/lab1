#!/bin/bash
docker build -t pastebin:latest .
docker save pastebin:latest -o docker-image.tar
