Project Zodiacy
===============

Requirements
------------

* python3
* *nix system
* perl


1) Generate horoscope URLs
----------------------------

```
./generate_urls -o urls
```


2) Fetch horoscope data
-----------------------

```
cat urls | xargs wget --wait=10 --random-wait -q -O - | perl -nle 'print $1 if /window.horoscopes = (.*);/m' > zodiacs.json
```

3) Import horoscopes into database
----------------------------------

```
./import_to_sql.py -i zodiacs.json -s zodiac.sqlite
```
