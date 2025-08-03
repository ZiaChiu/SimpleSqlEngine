from time import sleep
import pytest

from numpy.version import release

from db import *
from db_connection import *
from output import *

#
# args = ['-v','-s','./']
#
# pytest.main(args)


engine = SQLiteDataEngine("my_database.db")

# Load from CSV and create table automatically
table = engine.import_csv("NetflixTVShowsAndMovies.csv")
engine.close()

class TestSQLite:
    def test_query_select(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select("index")
        print("Q:",query)
        assert query.build() == 'SELECT "index" FROM NetflixTVShowsAndMovies;'
    def test_query_select_with_alias(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select("index", ("imdb_score", "score"))
        assert query.build() == 'SELECT "index", imdb_score AS score FROM NetflixTVShowsAndMovies;'
    def test_query_select_with_function(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select(("AVG(imdb_score)", "avg_score"))
        assert query.build() == 'SELECT AVG(imdb_score) AS avg_score FROM NetflixTVShowsAndMovies;'
    def test_query_select_with_function_and_alias(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select(("AVG(imdb_score)", "avg_score"), ("MIN(imdb_score)", "min_score"))
        assert query.build() == 'SELECT AVG(imdb_score) AS avg_score, MIN(imdb_score) AS min_score FROM NetflixTVShowsAndMovies;'
    def test_query_select_with_function_and_alias_and_where(self):
        query = (SQLQueryBuilder("NetflixTVShowsAndMovies")
                 .select(("AVG(imdb_score)", "avg_score"))
                 .where("type", False)
                 .and_("imdb_score", (">=", 7))
                 .group_by("type")
                 .order_by("avg_score", desc=True)
                 .limit(5))

        assert query.build() == 'SELECT AVG(imdb_score) AS avg_score FROM NetflixTVShowsAndMovies WHERE type IS NOT NULL AND imdb_score >= 7 GROUP BY type ORDER BY avg_score DESC LIMIT 5;'
    def test_query_update(self):
        query = (SQLQueryBuilder("NetflixTVShowsAndMovies")
                 .update(release_year=2026, imdb_score=8.5)
                 .where("index", 3))

        assert query.build() == 'UPDATE NetflixTVShowsAndMovies SET "release_year" = 2026, "imdb_score" = 8.5 WHERE "index" = 3;'
    def test_query_select_with_reserved_word(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select("index")
        assert query.build() == 'SELECT "index" FROM NetflixTVShowsAndMovies;'

    def test_query_select_with_reserved_word_in_function(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select(("AVG(index)", "avg_index"))
        assert query.build() == 'SELECT AVG("index") AS avg_index FROM NetflixTVShowsAndMovies;'
    def test_query_select_with_reserved_word_in_function_and_alias(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select(("AVG(index)", "avg_index"), ("MIN(index)", "min_index"))
        assert query.build() == 'SELECT AVG("index") AS avg_index, MIN("index") AS min_index FROM NetflixTVShowsAndMovies;'
    def test_query_select_with_reserved_word_in_function_and_alias_and_where(self):
        query = (SQLQueryBuilder("NetflixTVShowsAndMovies")
                 .select(("AVG(index)", "avg_index"))
                 .where("type", False)
                 .and_("index", (">=", 7))
                 .group_by("type")
                 .order_by("avg_index", desc=True)
                 .limit(5))

        assert query.build() == 'SELECT AVG("index") AS avg_index FROM NetflixTVShowsAndMovies WHERE type IS NOT NULL AND "index" >= 7 GROUP BY type ORDER BY avg_index DESC LIMIT 5;'
    def test_query_exists(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select("index") \
            .exists_(SQLQueryBuilder("NetflixTVShowsAndMovies").select("index").build())

        assert query.build() == 'SELECT "index" FROM NetflixTVShowsAndMovies WHERE EXISTS (SELECT "index" FROM NetflixTVShowsAndMovies);'
    def test_query_exists_with_reserved_word(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select("index") \
            .exists_(SQLQueryBuilder("NetflixTVShowsAndMovies").select("index").build())

        assert query.build() == 'SELECT "index" FROM NetflixTVShowsAndMovies WHERE EXISTS (SELECT "index" FROM NetflixTVShowsAndMovies);'
    def test_query_exists_with_reserved_word_in_function(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select(("AVG(index)", "avg_index")) \
            .exists_(SQLQueryBuilder("NetflixTVShowsAndMovies").select("index").build())

        assert query.build() == 'SELECT AVG("index") AS avg_index FROM NetflixTVShowsAndMovies WHERE EXISTS (SELECT "index" FROM NetflixTVShowsAndMovies);'
    def test_query_exists_with_reserved_word_in_function_and_alias(self):
        query = SQLQueryBuilder("NetflixTVShowsAndMovies") \
            .select(("AVG(index)", "avg_index"), ("MIN(index)", "min_index")) \
            .exists_(SQLQueryBuilder("NetflixTVShowsAndMovies").select("index").build())

        assert query.build() == 'SELECT AVG("index") AS avg_index, MIN("index") AS min_index FROM NetflixTVShowsAndMovies WHERE EXISTS (SELECT "index" FROM NetflixTVShowsAndMovies);'
    def test_query_exists_with_reserved_word_in_function_and_alias_and_where(self):
        query = (SQLQueryBuilder("NetflixTVShowsAndMovies")
                 .select(("AVG(index)", "avg_index"))
                 .where("type", False)
                 .and_("index", (">=", 7))
                 .group_by("type")
                 .order_by("avg_index", desc=True)
                 .limit(5)
                 .exists_(SQLQueryBuilder("NetflixTVShowsAndMovies").select("index").build()))

        assert query.build() == 'SELECT AVG("index") AS avg_index FROM NetflixTVShowsAndMovies WHERE type IS NOT NULL AND "index" >= 7 GROUP BY type ORDER BY avg_index DESC LIMIT 5 AND EXISTS (SELECT "index" FROM NetflixTVShowsAndMovies);'

