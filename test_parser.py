#!/usr/bin/env python
# encoding: utf-8

from parser import parseHoroscope


with open("test.html", "r") as file:
    eFile = file.read()
    parseHoroscope(eFile)
