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

# query = (
#     SQLQueryBuilder("NetflixTVShowsAndMovies")
#     .select("type", ('AVG("imdb_score")', "avg_score"))
#     .where("type", False)  # Genre IS NOT NULL
#     .and_("imdb_score", (">=", 7))
#     .group_by("type")
#     .order_by("avg_score", desc=True)
#     .limit(5)
#     .build()
# )
# d = DataOutput("my_database.db", query,"results")
# c = d.get_csv()
# print(c)
#
# d.line_plot(kind="scatter")
#
# def test_demo():
#     assert 100 == 100

# class TestDome:
#
#     def test_demo1(self):
#         assert 11 == 11
#
#     def test_demo(self):
#         assert 22 == 21
# class TestDome:
#
#     def test_demo1(self):
#         print('\n----测试用例执行-----------')
#         assert 11 == 11

# query = (
# SQLQueryBuilder("NetflixTVShowsAndMovies")
# .select("release_year","imdb_score")
# .where("age_certification", "R")
# .build()
#
# )
#
# query1 = (
# SQLQueryBuilder("NetflixTVShowsAndMovies")
# .update(release_year=2026, imdb_score=8.5)
# .where("index", 3)
# .build()
# )


# UPDATE NetflixTVShowsAndMovies SET "release_year" = 2026,
# "imdb_score" = 8.5 WHERE "index" IS NULL;
# print(query1)


# d = DataOutput("./my_database.db", query1,"results4")
# c = d.get_csv()
# print(c)


# def test_plt():
#     p = plt.figure(figsize=(10, 6))
#     return p


# test_plt()
# p = test_plt()
# p.line_plot(kind="line", title="IMDB Score by Release Year for R Rated Movies")
# plt.xlabel("Release Year")
# plt.ylabel("IMDB Score")
# plt.title("IMDB Score by Release Year for R Rated Movies")
# plt.show()
