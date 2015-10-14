Project Zodiacy
===============



1) Fetch horoscope data
-----------------------
First you need to download the horoscope data:
```
dseq 01.01.2007 $(date +%d.%m.%Y) -i %d.%m.%Y | parallel --no-notice -j50 curl -s http://www.tarot.com/daily-horoscope/aquarius/{} | perl -nle 'print $1 if /window.horoscopes = (.*);/m' > zodiacs.json
```
Which you can then import into an sqlite database:
```
./import_to_sql.py -i zodiacs.json -s zodiac.sqlite
```

Requirements
------------

* bash
* coreutils
* dateutils
* GNU parallel
* perl
* python3
* sqlite3
