START_DATE = 01.08.2007
PROCESSES = 50

all:	zodiac.sqlite

zodiacs.json:
		dseq ${START_DATE} $(date +%d.%m.%Y) -i %d.%m.%Y | parallel --no-notice -j${PROCESSES} curl -s http://www.tarot.com/daily-horoscope/aquarius/{} | perl -nle 'if( /window.horoscopes = (.*);/m) { chomp($$1); print $$1 }' > $@

zodiac.sqlite:	zodiacs.json
		./import_to_sql.py -i $< -s $@

clean:
		${RM} zodiacs.json
		${RM} zodiac.sqlite
