START_DATE = 01.08.2007
PROCESSES = 50
ZODIACS_JSON = "data/zodiac.json"
ZODIACS_DB = "data/zodiac.sqlite"

all:	$(ZODIACS_DB)
		python3 setup.py clean && python setup.py sdist && python setup.py install --user

$(ZODIACS_JSON):
		dseq ${START_DATE} $(date +%d.%m.%Y) -i %d.%m.%Y | parallel --no-notice -j${PROCESSES} curl -s http://www.tarot.com/daily-horoscope/aquarius/{} | perl -nle 'if( /window.horoscopes = (.*);/m) { chomp($$1); print $$1 }' > $<

$(ZODIACS_DB):	$(ZODIACS_JSON)
		./bin/import_to_sql.py -i ${ZODIACS_JSON} -s $<

nltk_download:
		python3 -c "from nltk import download; download('wordnet'); download('punkt')"

clean:
		${RM} ${ZODIACS_JSON}
		${RM} ${ZODIACS_DB}
