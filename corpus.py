import collections
import logging
from math import sqrt
from wordnik import swagger, WordApi

"""corpus.py: Generates horoscopes based provided corpuses"""

__author__ = "Project Zodiacy"
__copyright__ = "Copyright 2015, Project Zodiacy"

logger = logging.getLogger('root')


class Corpus():

    """
        Generates a corpus from the provided database

        Args:
            zodiac_sign: select only entries for a specific zodiac sign
            keyword: select only entries for a specific keyword
            with_rating: weight entries after a predefined rating
            threshold: minimal amount of entries needed for a valid corpus
            with_synonyms: query wordnik for synonyms
            wordnik_api_url: Wordnik API URL
            wordnik_api_key: Wordnik API Key
    """

    def __init__(self, conn, with_rating=False, with_synonyms=False,
                 zodiac_sign=None, keyword=None, threshold=5,
                 wordnik_api_url=None, wordnik_api_key=None):
        kws = locals()
        for key, val in kws.items():
            if key != "conn":
                self.__dict__[key] = val
        assert conn is not None
        self.cursor = conn.cursor()
        self.synonym_influence = 0.2
        self.zodiac_sign_ordinal = self._get_zodiac_sign(self.zodiac_sign)
        self._filters = []
        self._filters_values = []
        self._table_name = "horoscopes"
        self._build()

    def __str__(self):
        return str(self.__dict__)

    def _get_zodiac_sign(self, zodiac_sign=None):
        """ converts the string representation of a zodiac sign into a ordinal one
        Arguments:
            zodiac_sign: sign as string
        Returns:
            ordinal zodiac sign (from 0 to 12)
        """
        zodiac_signs = dict(zip(['general', 'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
                                 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'], range(13)))
        if zodiac_sign not in zodiac_signs:
            if zodiac_sign is not None:
                raise ValueError('Invalid zodiac sign')
        else:
            return zodiac_signs[zodiac_sign]

    def _add_filter(self, filter_sql, filter_value):
        """ help method to add a new filter
        Arguments:
            filter_sql: SQL string (with '?' for parameters)
            filter_value: parameters to bind to the SQL string (either a single value or list)
        """
        self._filters.append(filter_sql)
        if isinstance(filter_value, collections.MutableSequence):
            assert filter_sql.count("?") == len(filter_value)
            self._filters_values += filter_value
        else:
            assert filter_sql.count("?") == 1
            self._filters_values.append(filter_value)

    def _create_filters(self):
        """ builds all filters """
        if self.zodiac_sign is not None:
            self._add_filter("sign=?", self.zodiac_sign_ordinal)

        if self.with_synonyms:
            present_synonyms = self.get_present_synonyms()
            if len(present_synonyms) == 0:
                logger.warn("No related synonyms found")

            present_synonyms.append(self.keyword)
            synonyms_sql_array = ','.join(('?' for _ in present_synonyms))
            self._add_filter('keyword in (%s)' %
                             synonyms_sql_array, present_synonyms)

        elif self.keyword is not None:
            # synonyms is already filtering on keyword
            self._add_filter("keyword=?", self.keyword)

    def _build_filters(self):
        """ concatenates all available filter to SQL """
        filters = ""
        if len(self._filters) > 0:
            filters += " WHERE "
            filters += " AND ".join(self._filters)
        return filters

    def _execute_and_log(self, base_stmt, values):
        """ execute logs the entire SQL string
        This is expensive as we need to make a request to our SQLite database.
        Hence it is only performed when the debugging is enabled - the level
        of the root logger needs to be logging.DEBUG or less"""
        if logger.getEffectiveLevel() <= logging.DEBUG:
            sql_with_vals = base_stmt
            if len(values) > 0:
                self.cursor.execute(
                    "SELECT " + ", ".join(["quote(?)" for i in values]), values)
                quoted_values = self.cursor.fetchone()
                for quoted_value in quoted_values:
                    sql_with_vals = sql_with_vals.replace('?', str(quoted_value), 1)

            logger.debug("query: %s", sql_with_vals)

        self.cursor.execute(base_stmt, values)

    def _execute_query(self):
        """ Builds and executes the SQL query to fetch the corpus """
        columns = 'interp'
        columns += ',rating' if self.with_rating or self.with_synonyms else ''
        columns += ',keyword' if self.keyword else ''
        base_stmt = 'SELECT %s from %s' % (columns, self._table_name)
        base_stmt += self._build_filters()
        self._execute_and_log(base_stmt, self._filters_values)

    def _count_entries(self):
        """ Returns the number of found entries in the database
            Reason:
                cursor.rowcount returns -1 until all results have been fetched
        """
        base_stmt = 'SELECT COUNT(*) from %s' % self._table_name
        base_stmt += self._build_filters()
        self.cursor.execute(base_stmt, self._filters_values)
        return self.cursor.fetchone()[0]

    def _build(self):
        """ Returns a cursor with all horoscopes for the given parameters """

        self._create_filters()

        nr_entries = self._count_entries()
        if nr_entries < self.threshold:
            raise ValueError("Found %d matches" % nr_entries)

        logger.debug("%d entries found in corpus db", nr_entries)
        self._execute_query()

    def __iter__(self):
        """ Lazy corpus iterator """
        return self

    def __next__(self):
        """ returns the corpus lazy """
        row = next(self.cursor, None)
        if row is None:
            raise StopIteration

        rating = None
        if self.with_rating:
            rating = row[1]
        if self.with_synonyms:
            if row[0] == self.keyword:
                rating = row[1]
            else:
                rating = self.synonym_influence * \
                    row[1] * sqrt(len(self.synonyms))

        return (row[0], rating)

    def _get_synonyms(self, keyword):
        """ Queries Wordnik for synonyms """
        client = swagger.ApiClient(self.wordnik_api_key, self.wordnik_api_url)
        word_api = WordApi.WordApi(client)
        return word_api.getRelatedWords(keyword, relationshipTypes='synonym')[0].words

    def get_present_synonyms(self):
        """ Compares Wordnik result with present synonyms in DB
        Returns:
            List of synonyms occurring in the database
        """
        self.synonyms = self._get_synonyms(self.keyword)
        logger.debug("found %d synonyms", len(self.synonyms))
        self._execute_and_log('SELECT keyword FROM horoscopes WHERE keyword IN (%s) GROUP BY keyword' %
                              ','.join('?' for _ in self.synonyms), tuple(self.synonyms))
        return [row[0] for row in self.cursor if row is not None]
