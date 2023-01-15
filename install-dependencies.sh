#!/bin/bash

apt-get update
apt-get install --assume-yes --no-install-recommends \
    build-essential \
    libmagic-dev \
    wget

apt-get clean
rm -rf /var/lib/apt/lists/*
