Project Zodiacy
===============



1) Fetch horoscope data
-----------------------
First you need to download the horoscope data:

```
dseq 01.08.2007 $(date +%d.%m.%Y) -i %d.%m.%Y | parallel --no-notice -j50 curl -s http://www.tarot.com/daily-horoscope/aquarius/{} | perl -nle 'if( /window.horoscopes = (.*);/m) { chomp($1); print $1 }' > zodiacs.json
```

Which you can then import into an sqlite database:

```
./import_to_sql.py -i zodiacs.json -s zodiac.sqlite
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
* sqlite3
