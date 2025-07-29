
# Simple SQL Engine


This simple tool helps me process a CSV file using SQL statements.

It is not a full-fledged SQL engine, but rather a simple wrapper to help me with my data processing tasks.

I created it just for my convenience. In the future, I may add more features.



## Features 

- Support traditional SQL statements.

- Support Cross-file join

- Support img output

- Support MySQL, SQLite, PostgreSQL, and MS SQL Server.

- Support SQL <- db -> CSV transformation

## usage

- ### SQLQueryBuilder
SQLQueryBuilder is a query statement generator. 
You can use it to build SQL queries in a more structured way.

arguments:
- `db_path`: The name of the db file to query.

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


