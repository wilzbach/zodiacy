Project Zodiacy
===============



1) Fetch horoscope data
-----------------------
To generate the zodiac-database just run

```
make
```


2) Description of the acquired horoscopes
-----------------------------------------

* there are four horoscopes dates with less than 12 horoscopes ("2007-10-13": 11, "2007-10-15":11, "2007-10-18": 7, "2007-10-22": 11)
* there are 22 horoscopes without a general horoscope (=12)
* there are 2969 horoscopes with an general horoscope (=13)

= 38901 horoscopes

### Numeric mapping of zodiac signs

```
0: general
1: aries
2: taurus
3: gemini
4: cancer
5: leo
6: virgo
7: libra
8: scorpio
9: sagittarius
10: capricorn
11: aquarius
12: pisces
```

Analysis
--------


Requirements
------------

* bash
* coreutils
* dateutils
* GNU parallel
* perl
* python3
  * nltk
  * wordnik-py3
* sqlite3
