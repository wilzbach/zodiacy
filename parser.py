#!/usr/bin/env python
# encoding: utf-8

import lxml.html
from lxml.cssselect import CSSSelector

selector = CSSSelector('div.daily')


def parseHoroscope(eFile):
    tree = lxml.html.fromstring(eFile)
    selection = selector(tree)
    if len(selection) >= 1:
        parent = selection[0]
        if len(parent) >= 2:
            hText = parent[1]
            hText.remove(hText[0])
            print(hText.text_content())
    else:
        print("NOT FOUND")
