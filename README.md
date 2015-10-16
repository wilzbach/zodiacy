Project Zodiacy
===============

Install from tarball
--------------------

```
pip install --user <tarball>
```

Please note that due to copyright issues we can't distribute the tarball.
See the instructions below to build directly from source

Install from source
-------------------

```
git clone https://github.com/greenify/zodiacy
cd zodiacy
make
python setup.py clean && python setup.py sdist && python setup.py install --user
```

Possible routes
---------------

Select a random keyword (weighted):

[`http://zodiacy.parce.li/random-keywords`](http://zodiacy.parce.li/random-keywords)

See all available keywords:

[`http://zodiacy.parce.li/list-keywords`](http://zodiacy.parce.li/list-keywords)

Select a specific keyword

[`http://zodiacy.parce.li/keyword/patience`](http://zodiacy.parce.li/keyword/patience)

Generate a horoscope for you zodiac sign:

[`http://zodiacy.parce.li/sign/aries`](http://zodiacy.parce.li/sign/aries)

Build you own queries
---------------------

e.g.

- [`http://zodiacy.parce.li/q?keyword=pride&nr_horoscopes=5&format=json`](http://zodiacy.parce.li/q?keyword=pride&nr_horoscopes=5&format=json)

- [`http://zodiacy.parce.li/q?sign=aries&order=2`](http://zodiacy.parce.li/q?sign=aries&order=2)

- [`http://zodiacy.parce.li/q?sign=aries&use_ratings=1`](http://zodiacy.parce.li/q?sign=aries&use_ratings=1)

- [`http://zodiacy.parce.li/q?keyword=patience&markov_type=hmm_past`](http://zodiacy.parce.li/q?keyword=patience&markov_type=hmm_past)

- [`http://zodiacy.parce.li/q?sign=aries&order=2`](http://zodiacy.parce.li/q?sign=aries&order=2)

- [`http://zodiacy.parce.li/q?sign=aries&use_synonym_emissions=1`](http://zodiacy.parce.li/q?sign=aries&use_synonym_emissions=1)

- [`http://zodiacy.parce.li/q?keyword=patience&use_synonyms_generation=1`](http://zodiacy.parce.li/q?keyword=patience&use=synonyms_generation=1)

... and a lot more :)

Possible parameters
-------------------


```
  -s SIGN, --sign SIGN  zodiac sign to generate
  -k KEYWORD, --keyword KEYWORD
                        keyword for the horoscope
  -t THRESHOLD, --threshold THRESHOLD
                        minimum count of horoscopes for the given filters
  -o {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19}, --order {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19}
                        order of the used markov chain
  --order-emissions {1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19}
                        max. order to look back at prev. emissions (HMM)
  -n {1,2,3,4,5,6,7,8,9}, --horoscopes {1,2,3,4,5,6,7,8,9}
                        number of horoscopes
  -c, --synonyms-generation
                        additionally use synonyms of keywords for generation
  -m {markov,hmm,hmm_past}, --markov_type {markov,hmm,hmm_past}
                        Markov type to use (default: markov)
  --prob-hmm-states PROB_HMM_STATES
                        When using previous states and emissions, weight for
                        the previous states
  --prob-hmm-emissions PROB_HMM_EMISSIONS
                        When using previous states and emissions, weight for
                        the previous emissions
  -y, --synonyms-emission
                        use synonyms on emissions
  --prob-syn-emissions PROB_SYNONYMS_EMISSION
                        probability to emit synonyms
  --list-keywords       show all available keywords
  -r, --random-keyword  select keyword randomly (weighted on occurrence)
  --ratings             weight states according to ratings
```

Description of the acquired horoscopes
--------------------------------------

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

Dev Requirements
----------------

* bash
* coreutils
* dateutils
* GNU parallel
* GNU make
* perl
* python3
  * nltk
  * wordnik-py3
  * astral
  * SQLAlchemy
  * setuptools
* sqlite3
