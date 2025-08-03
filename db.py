import os
import sqlite3
import pandas as pd


# Description: A simple SQL data engine for SQLite with automatic schema inference from DataFrames and CSV files.


class SQLQueryBuilder:
    def __init__(self, db_table, db_type="sqlite"):
        self.__type = db_type
        if db_type not in ["sqlite", "mysql", "postgresql"]:
            raise ValueError(f"Unsupported database type: {db_type}. Supported types are 'sqlite', 'mysql', 'postgresql'.")
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
    def delete(self, *columns):

        parts = []
        for col in columns:
            if isinstance(col, tuple):
                expr, alias = col
                parts.append(f"{expr} AS {alias}")
            else:
                parts.append(col)
        self._select = ", ".join(parts)
        self._query = f"DELETE FROM {self.table} "

        return self
    def select(self, *columns,top=False,top_count=None):
        parts = []
        for col in columns:
            if isinstance(col, tuple):
                expr, alias = col
                parts.append(f"{expr} AS {alias}")
            else:
                parts.append(col)
        self._select = ", ".join(parts)

        match top:
            case True:
                if top_count is None:
                    raise ValueError("top_count must be specified when top is True.")
                self._query = f"SELECT TOP {top_count} {self._select} FROM {self.table} "
            case False:
                if top_count is not None:
                    raise ValueError("top_count should not be specified when top is False.")
                self._query = f"SELECT {self._select} FROM {self.table} "


        return self

    @staticmethod
    def _parse_condition(col, value):
        # 1) NULL‐check
        if value is None:
            return f'"{col}" IS NULL'
          # 1b) interpret False as “IS NOT NULL”
        if value is False:

            return f'"{col}" IS NOT NULL'

        # 2) tuple for operators, including NULL/not‐NULL if you want
        if isinstance(value, tuple) and len(value) == 2:
            op, val = value
            # e.g. ("!=", None) → IS NOT NULL
            if val is None:
                if op in ("!=", "<>"):
                    return f'"{col}" IS NOT NULL'
                elif op == "=":
                    return f'"{col}" IS NULL'
                else:
                    raise ValueError(f"Unsupported NULL operator: {op}")
            # non‐NULL tuple
            if isinstance(val, str):
                return f'"{col}" {op} "{val}"'
            else:
                return f'"{col}" {op} {val}'

        # 3) simple scalar equality
        if isinstance(value, (int, float, bool)):
            # bools map to SQL TRUE/FALSE if you like, or as 1/0
            return f'"{col}" = {value!r}'  # repr(True)->'True', repr(3)->'3'

        if isinstance(value, str):
            return f'"{col}" = "{value}"'

        raise ValueError(f"Unsupported condition type: {value!r}")

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
    def like_(self, col, pattern):
        if not isinstance(pattern, str):
            raise ValueError("LIKE pattern must be a string.")
        self._where_conditions.append(f'"{col}" LIKE "{pattern}"')
        return self

    def exists_(self, query):
        if not isinstance(query, str):
            raise ValueError("EXISTS query must be a string.")
        self._where_conditions.append(f'EXISTS ({query})')
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



