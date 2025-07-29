import os
import seaborn as sns
import matplotlib.pyplot as plt
import sqlite3

import pandas as pd
from sklearn.conftest import pyplot

# Description: A simple SQL data engine for SQLite with automatic schema inference from DataFrames and CSV files.


def infer_sql_type(value):
    if pd.isnull(value):
        return "TEXT"
    if isinstance(value, int):
        return "INTEGER"
    elif isinstance(value, float):
        return "REAL"
    elif isinstance(value, str):
        return "TEXT"
    return "TEXT"


class SimpleSQLDataEngine:
    def __init__(self, db_path="my_database.db"):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.schemas = {}
        print(f"Connected to SQLite DB at: {db_path}")

    def create_table_from_df(self, table_name, df: pd.DataFrame):
        # Infer types from first non-null row
        sample_row = df.dropna().iloc[0] if not df.dropna().empty else df.iloc[0]
        schema = {
            col: infer_sql_type(sample_row[col])
            for col in df.columns
        }
        self.create_table(table_name, schema)

    def import_csv(self, file_path, table_name=None):
        df = pd.read_csv(file_path)
        if table_name is None:
            table_name = os.path.splitext(os.path.basename(file_path))[0].replace(" ", "_")

        if table_name not in self.schemas:
            self.create_table_from_df(table_name, df)

        df.to_sql(table_name, self.conn, if_exists="replace", index=False)
        print(f"Imported {len(df)} rows into '{table_name}'")
        return table_name

    def create_table(self, table_name, columns: dict):
        self.schemas[table_name] = columns
        col_defs = ", ".join([f'"{col}" {typ}' for col, typ in columns.items()])
        sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({col_defs})'
        self.cursor.execute(sql)
        self.conn.commit()
        print(f"Created table '{table_name}' with schema: {columns}")

    def get_schema(self, table_name):
        if table_name in self.schemas:
            return self.schemas[table_name]
        self.cursor.execute(f"PRAGMA table_info('{table_name}')")
        return {row[1]: row[2] for row in self.cursor.fetchall()}

    def list_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return [row[0] for row in self.cursor.fetchall()]

    def close(self):
        self.conn.close()
        print("Database connection closed.")


class SQLQueryBuilder:
    def __init__(self, db_table):
        self.table = db_table
        self._select = "*"
        self._where_conditions = []
        self._group_by = ""
        self._order_by = ""
        self._limit = ""
        self._query = ""

    def update(self, **kwargs):
        parts = []

        for key, val in kwargs.items():
            # Auto-quote plain strings that are not already quoted or SQL functions
            if isinstance(val, str) and not (
                    val.startswith("'") or val.startswith('"') or val.upper().endswith("()")
            ):
                val = f"'{val}'"
            parts.append(f'"{key}" = {val}')

        print(parts)

        if not parts:
            raise ValueError("No columns to update provided.")

        self._select = ", ".join(parts)
        print(self._select)
        self._query = f"UPDATE {self.table} SET {self._select} "
        return self


    def select(self, *columns):
        self._query = f"SELECT {self._select} FROM {self.table} "
        parts = []
        for col in columns:
            if isinstance(col, tuple):
                expr, alias = col
                parts.append(f"{expr} AS {alias}")
            else:
                parts.append(col)
        self._select = ", ".join(parts)
        return self

    @staticmethod
    def _parse_condition(col, value):
        if not value:
            return f'"{col}" IS NOT NULL'
        elif value:
            return f'"{col}" IS NULL'
        elif isinstance(value, (int, float)):
            return f'"{col}" = {value}'
        elif isinstance(value, str):
            return f'"{col}" = "{value}"'
        elif isinstance(value, tuple) and len(value) == 2:
            op, val = value
            if isinstance(val, str):
                return f'"{col}" {op} "{val}"'
            else:
                return f'"{col}" {op} {val}'
        else:
            raise ValueError(f"Unsupported condition: {value}")

    def where(self, col, value):
        self._where_conditions = [self._parse_condition(col, value)]
        return self

    def and_(self, col, value):
        self._where_conditions.append("AND " + self._parse_condition(col, value))
        return self

    def or_(self, col, value):
        self._where_conditions.append("OR " + self._parse_condition(col, value))
        return self

    def in_(self, col, values):
        self._where_conditions.append("IN" + self._parse_condition(col, values))
        return self
    def not_in_(self, col, values):
        self._where_conditions.append("NOT IN" + self._parse_condition(col, values))
        return self
    def between_(self, col, start, end):
        self._where_conditions.append(f'"{col}" BETWEEN {start} AND {end}')
        return self
    def not_between_(self, col, start, end):
        self._where_conditions.append(f'"{col}" NOT BETWEEN {start} AND {end}')
        return self
    def like(self, col, pattern):
        if not isinstance(pattern, str):
            raise ValueError("LIKE pattern must be a string.")
        self._where_conditions.append(f'"{col}" LIKE "{pattern}"')
        return self

    def group_by(self, *fields):
        self._group_by = f"GROUP BY {', '.join(fields)}"
        return self

    def order_by(self, *fields, desc=False):
        order = "DESC" if desc else "ASC"
        self._order_by = f"ORDER BY {', '.join(fields)} {order}"
        return self

    def limit(self, n):
        self._limit = f"LIMIT {n}"
        return self

    def build(self):
        # query = f"SELECT {self._select} FROM {self.table} "
        query = self._query
        if self._where_conditions:
            query += "WHERE " + " ".join(self._where_conditions) + " "
        if self._group_by:
            query += self._group_by + " "
        if self._order_by:
            query += self._order_by + " "
        if self._limit:
            query += self._limit
        return query.strip() + ";"

class DataOutput:
    def __init__(self, db_file, query=None, output_name=""):
        self.__output_name = output_name
        self.__csv = f"./{self.__output_name}.csv"
        # self.__db = sqlite3.connect(db_file)
        try:
            self.__db = sqlite3.connect(db_file)
            print(f"[OK] Connected to SQLite DB: {db_file}")
        except sqlite3.Error as e:
            print(f"[ERROR] Failed to connect to DB: {e}")
            raise

        self.__cursor = self.__db.cursor()
        self.__query = query

        self.__rows = []
        self.__columns = []

        if query:
            self.__execute_query()
            self.__export_to_csv()

        self.__db.close()

    def __execute_query(self):
        self.__cursor.execute(self.__query)
        self.__rows = self.__cursor.fetchall()
        print(self.__cursor.description)

        if self.__cursor.description is None:
            print("[Info] Query executed: no result set (likely UPDATE/INSERT/DELETE).")

            table = self.__query.split()[1]
            self.__cursor.execute(
                SQLQueryBuilder(table).select().build()
            )
            self.__rows = self.__cursor.fetchall()
            self.__columns = [desc[0] for desc in self.__cursor.description]
        else:
            self.__columns = [desc[0] for desc in self.__cursor.description]
        print(self.__columns)

    def __export_to_csv(self):
        df = pd.DataFrame(self.__rows, columns=self.__columns)
        df.to_csv(f"{self.__output_name}.csv", index=False)
        print(f"Exported to {self.__output_name}.csv")

    def set_figsize(self, figsize=(10, 6)):
        plt.figure(figsize=figsize)

    def get_csv(self):
        df = pd.read_csv(self.__csv)
        return df

    def line_plot(self, kind="line", title=None):
        df = self.get_csv()

        if len(df.columns) < 2:
            raise ValueError("Expected at least two columns for plotting.")

        x_col, y_col = str(df.columns[0]), str(df.columns[1])
        title = title or f"{y_col} vs {x_col}"

        plt.figure(figsize=(10, 6))

        if kind == "bar":
            plt.bar(df[x_col], df[y_col])
        elif kind == "scatter":
            plt.scatter(df[x_col], df[y_col])
        elif kind == "line":  # default: line
            plt.plot(df[x_col], df[y_col], marker='o')
        else:
            raise ValueError(f"Unsupported plot kind: {kind}, supported kinds are 'line', 'bar', 'scatter'.")

        plt.xlabel(x_col)
        plt.ylabel(y_col)
        plt.title(title)
        plt.grid(True)
        plt.tight_layout()
        plt.show()




