from db_connection import SQLiteDataEngine
from db import SQLQueryBuilder
from output import DataOutput

# build the db from csv files
engine = SQLiteDataEngine("my_database.db")

# Load from CSV and create table automatically
table = engine.import_csv("NetflixTVShowsAndMovies.csv")
engine.close()

# output the csv from query

DataOutput(
    db_file="my_database.db",
    query=SQLQueryBuilder("NetflixTVShowsAndMovies")
        .select(("AVG(index)", "avg_index"))
        .where("type", False)
        .and_("index", (">=", 7))
        .group_by("type")
        .order_by("avg_index", desc=True)
        .limit(5)
        .exists_(SQLQueryBuilder("NetflixTVShowsAndMovies").select("index").build(exists=True)),
    output_name="output_avg_index")
