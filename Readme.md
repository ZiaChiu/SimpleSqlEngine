
# Simple SQL Engine(SSE)


This simple tool helps me process a CSV file using SQL statements.

It is not a full-fledged SQL engine, but rather a simple wrapper to help me with my data processing tasks.

I created it just for my convenience. In the future, I may add more features.

## Environment Requirements
- ### Python 3.12 or higher
- ### Dependency packages
- matplotlib
- pandas
- sqlite3
- pytest
- numpy

## Build the dependency to your project

1. copy the different package content from requirement.txt to your project directory's requirement.txt .

2. run the command below under your venv to install the package and its dependencies in your project directory.

```bash
pip install . -r requirements.txt
```
### 
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
- ### DataOutput
- DataOutput is a class that allows you to export the results of a SQL query to a CSV file.
- arguments:
- `db_file`: The name of the SQLite database file.
- `query`: The SQL query to execute.
- `output_name`: The name of the output CSV file (without extension).
- functions:
- `get_csv()`: This method will execute the SQL query and return the results as a CSV file.
  - file will be saved in the current directory with the name specified in `output_name`.

```python
from db import *
from output import DataOutput
# Initialize database and import CSV
engine = SQLiteDataEngine("my_database.db")
engine.import_csv("NetflixTVShowsAndMovies.csv")
engine.close()
# Build a query to compute average index per type
sql = (
    SQLQueryBuilder("NetflixTVShowsAndMovies")
      .select(("AVG(index)", "avg_index"))
      .where("type", False)
      .and_("index", (">=", 7))
      .group_by("type")
      .order_by("avg_index", desc=True)
      .limit(5)
      .build()
)
# Export results to CSV
DataOutput(
    db_file="my_database.db",
    query=sql,
    output_name="output_avg_index"
)
```


