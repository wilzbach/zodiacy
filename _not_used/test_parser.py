#!/usr/bin/env python
# encoding: utf-8

from parser_dom import parseHoroscope


with open("test.html", "r") as file:
    eFile = file.read()
    parseHoroscope(eFile)
