
# Simple SQL Engine


This simple tool helps me process a CSV file using SQL statements.

It is not a full-fledged SQL engine, but rather a simple wrapper to help me with my data processing tasks.

I created it just for my convenience. In the future, I may add more features.

## Environment Requirements
- ### Python 3.12 or higher
- ### Dependency packages
- matplotlib
- pandas
- sqlite3
- scikit-learn
- pytest
- numpy
- seaborn


## Features 

- Support traditional SQL statements.

- Support Cross-file join

- Support img output

- Support MySQL, SQLite, PostgreSQL, and MS SQL Server.

- Support SQL <- db -> CSV transformation

## Unsupported SQL features
 
    MIN() - returns the smallest value within the selected column
    MAX() - returns the largest value within the selected column
    COUNT() - returns the number of rows in a set
    SUM() - returns the total sum of a numerical column
    AVG() - returns the average value of a numerical column
Please just use them as a string of SQL arguments in the query.

## Usage

- ### SQLiteDataEngine

SQLiteDataEngine is a simple SQLite database engine that allows you to execute SQL queries on a SQLite database file, which was transformed from CSV files into SQLite databases.

arguments:
- `db_path`: The name of the db file you will create at the current location.

functions:

- import_csv(): This method will import a CSV file into the SQLite database.
  - arguments:
    - `csv_path`: The path to the CSV file you want to import.
    - `table_name`: The name of the table to create in the database. If not provided, it will use the CSV file name without extension.
```python
from db import *

engine = SQLiteDataEngine("my_database.db")

# Load from CSV and create a table automatically
table = engine.import_csv("NetflixTVShowsAndMovies.csv")
engine.close()


```

- ### SQLQueryBuilder
SQLQueryBuilder is a query statement generator. 
You can use it to build SQL queries in a more structured way.

arguments:
- `db_path`: The name of the db file to query.
- `query`: the query statements which will be executed in the DB.

```python
from db import *

SQLQueryBuilder("NetflixTVShowsAndMovies")
    .select("type", ('AVG("imdb_score")', "avg_score"))
    .where("type", False)  # Genre IS NOT NULL
    .and_("imdb_score", (">=", 7))
    .group_by("type")
    .order_by("avg_score", desc=True)
    .limit(5)
    .build()
```
This will generate the following SQL query:
```sql
SELECT * FROM NetflixTVShowsAndMovies WHERE "type" IS NOT NULL AND "imdb_score" IS NULL GROUP BY type ORDER BY avg_score DESC LIMIT 5;
```

- build(): This method will return the SQL query string.

example:
```python
from db import *

query = (
SQLQueryBuilder("NetflixTVShowsAndMovies")
.select("release_year","imdb_score")
.where("age_certification", "R")
.build()

)
d = DataOutput("./my_database.db", query,"results4")
c = d.get_csv()
print(c)
```


