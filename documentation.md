# Documentation for SSE

## Simple SQL Engine (SSE)

### A simple SQL data engine for SQLite with automatic schema inference from CSV files and DataFrames, featuring a fluent Python-based SQLQueryBuilder and easy CSV import/export.

### limitations
- Only supports SQLite databases.
- Only supports single table queries.
- Does not support complex SQL features like joins, unions.
- Does not support advanced SQL functions like MIN, MAX, COUNT, SUM, AVG directly in the query builder (use them as strings).
- Does not support Any, All, Distinct in the query builder.
- Does not support multiple databases joins.
- Does not support multiple databases joins with different db types.

### future features
- Support multiple tables of the same db
- Support join with multiple tables
- Support Union
- Support Any, All, Distinct
- Support multiple databases joins
- Support multiple databases joins with different db types
- Support reserved words checking
- Support subqueries for WHERE and HAVING.

### Unsupported SQL features
- MIN() - returns the smallest value within the selected column
- MAX() - returns the largest value within the selected column
- COUNT() - returns the number of rows in a set
- SUM() - returns the total sum of a numerical column
- AVG() - returns the average value of a numerical column 
##### Please just use them as a string of SQL arguments in the query.


## Installation

Refer the example code of [setup.py](setup.py) to know how to apply this package in your project.

```bash
pip install .
# or
python setup.py install
```

Ensure you have Python 3.8+ and SQLite installed.

## Quick Start

```python
from db_connection import SQLiteDataEngine
from db import SQLQueryBuilder
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

## API Reference

### `SQLQueryBuilder(table: str, db_type: str = "sqlite")`

Fluent interface for building SQL queries.

#### Examples

* **select**

  ```python
  sql = (
      SQLQueryBuilder("products")
        .select("id", "name", ("COUNT(*)", "total"))
        .group_by("name")
        .build()
  )
  # => SELECT id, name, COUNT(*) AS total FROM products GROUP BY name;
  ```

* **select** with `TOP`

  ```python
  sql = (
      SQLQueryBuilder("orders")
        .select("order_id", top=True, top_count=5)
        .build()
  )
  # => SELECT TOP 5 order_id FROM orders;
  ```

* **update**

  ```python
  sql = (
      SQLQueryBuilder("users")
        .update(("status", "'active'"), ("last_login", "CURRENT_TIMESTAMP"))
        .where("id", 42)
        .build()
  )
  # => UPDATE users SET status = 'active', last_login = CURRENT_TIMESTAMP WHERE id = 42;
  ```

* **delete**

  ```python
  sql = (
      SQLQueryBuilder("sessions")
        .delete("*")
        .where("expires_at", ("<", "'2025-01-01'"))
        .build()
  )
  # => DELETE FROM sessions WHERE expires_at < '2025-01-01';
  ```

* **where / and\_ / or\_**

  ```python
  sql = (
      SQLQueryBuilder("products")
        .select("*")
        .where("category", "electronics")
        .and_("price", (">", 100))
        .or_("stock", ("<", 5))
        .build()
  )
  # => SELECT * FROM products WHERE category = 'electronics' AND price > 100 OR stock < 5;
  ```

* **between\_ / not\_between\_**

  ```python
  sql = (
      SQLQueryBuilder("orders")
        .select("order_id")
        .between_("order_date", "'2025-01-01'", "'2025-06-30'")
        .not_between_("total", 50, 200)
        .build()
  )
  # => SELECT order_id FROM orders WHERE order_date BETWEEN '2025-01-01' AND '2025-06-30' AND total NOT BETWEEN 50 AND 200;
  ```

* **like\_**

  ```python
  sql = (
      SQLQueryBuilder("employees")
        .select("name")
        .like_("email", "%@example.com")
        .build()
  )
  # => SELECT name FROM employees WHERE email LIKE '%@example.com';
  ```

* **exists\_**

- #### when exists is `True`, that means the query will build a subquery for `EXISTS` clause, which will not add ";" at the end of the query.

  ```python
  sub = SQLQueryBuilder("orders").select("1").where("customer_id", 5).build(exists=True)
  sql = (
      SQLQueryBuilder("customers")
        .select("*")
        .exists_(sub)
        .build()
  )
  # => SELECT * FROM customers WHERE EXISTS (SELECT 1 FROM orders WHERE customer_id = 5)
  ```

* **group\_by / having / and\_having**
- #### `having` and `and_having` are used for filtering aggregated results, not for normal columns. They should be used after `group_by`.)

  ```python
  sql = (
      SQLQueryBuilder("sales")
        .select("region", ("SUM(amount)", "total_sales"))
        .group_by("region")
        .having("total_sales", (">", 10000))
        .and_having("region", "North")
        .build()
  )
  # => SELECT region, SUM(amount) AS total_sales FROM sales GROUP BY region HAVING total_sales > 10000 AND region = 'North';
  ```

* **having\_exists / and\_exist\_having**

- #### this exists is following a `HAVING` clause, which is different from the `exists_` method.
  ```python
  sub = SQLQueryBuilder("reviews").select("1").where("product_id", 10).build(exists=True)
  sql = (
      SQLQueryBuilder("products")
        .select("id", "name")
        .group_by("id")
        .having_exists(sub)
        .build()
  )
  # => SELECT id, name FROM products GROUP BY id HAVING EXISTS (SELECT 1 FROM reviews WHERE product_id = 10)
  ```

* **order\_by**
- #### when `desc` is `True`, it will order by descending.

  ```python
  sql = (
      SQLQueryBuilder("posts")
        .select("title", "views")
        .order_by("views", desc=True)
        .limit(3)
        .build()
  )
  # => SELECT title, views FROM posts ORDER BY views DESC LIMIT 3;
  ```

* **limit**

  ```python
  sql = SQLQueryBuilder("comments").select("*").limit(10).build()
  # => SELECT * FROM comments LIMIT 10;
  ```

* **build**

  * `build()` appends `;`, unless `exists=True` for subqueries.

(db\_file: str)\`

* `import_csv(csv_file: str) -> str` – imports a CSV as a table.
* `close()`

### `DataOutput(db_file: str, query: str, output_name: str)`

Executes the query and writes results to `output_name.csv`.


## License

AGPL-3.0
This project is licensed under the GNU Affero General Public License v3.0 (AGPL-3.0). See the [LICENSE](LICENSE) file for details.

