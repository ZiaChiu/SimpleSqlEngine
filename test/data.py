from time import sleep
import pytest

from numpy.version import release

from db import *


engine = SQLiteDataEngine("my_database.db")

# Load from CSV and create table automatically
table = engine.import_csv("NetflixTVShowsAndMovies.csv")
engine.close()


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

query = (
SQLQueryBuilder("NetflixTVShowsAndMovies")
.select("release_year","imdb_score")
.where("age_certification", "R")
.build()

)

query1 = (
SQLQueryBuilder("NetflixTVShowsAndMovies")
.update(release_year=2026, imdb_score=8.5)
.where("index", 3)
.build()
)



print(query1)


d = DataOutput("./my_database.db", query1,"results4")
c = d.get_csv()
print(c)


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
