
fetchings data
--------------

```
cat aquarius | xargs wget --wait=10 --random-wait -q -O - | perl -nle 'print $1 if /window.horoscopes = (.*);/m' > zodias.json
```
