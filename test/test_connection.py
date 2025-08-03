import pytest
from db_connection import SQLiteDataEngine

args = ['-v', '-s', './']
pytest.main(args)

engine = SQLiteDataEngine("my_database.db")

# Load from CSV and create table automatically
table = engine.import_csv("NetflixTVShowsAndMovies.csv")
engine.close()
