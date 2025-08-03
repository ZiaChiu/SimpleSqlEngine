import os
import sqlite3

import pandas as pd

def check_reserved_word(word):

    words = [reserved_words_sqlite]

    for w in words:
        if word.lower() in w:
            return f'"{words}"'
    return None


# SQLite

reserved_words_sqlite = [
    "ABORT", "ACTION", "ADD", "AFTER", "ALL", "ALTER", "ANALYZE",
    "AND", "AS", "ASC", "ATTACH", "AUTOINCREMENT",
    "BEFORE", "BEGIN", "BETWEEN", "BY", "CASCADE",
    "CASE", "CAST", "CHECK", "COLLATE", "COLUMN",
    "COMMIT", "CONFLICT", "CONSTRAINT", "CREATE", "CROSS",
    "CURRENT_DATE", "CURRENT_TIME", "CURRENT_TIMESTAMP",
    "DATABASE", "DEFAULT", "DEFERRABLE", "DEFERRED", "DELETE",
    "DESC", "DETACH", "DISTINCT", "DO", "DROP",
    "EACH", "ELSE", "END", "ESCAPE", "EXCEPT",
    "EXCLUSIVE", "EXISTS", "EXPLAIN", "FAIL", "FOR",
    "FOREIGN", "FROM", "FULL", "GLOB", "GROUP",
    "HAVING", "IF", "IGNORE", "IMMEDIATE", "IN",
    "INDEX", "INDEXED", "INITIALLY", "INNER", "INSERT",
    "INSTEAD", "INTERSECT", "INTO", "IS", "ISNULL",
    "JOIN", "KEY", "LEFT", "LIKE", "LIMIT",
    "MATCH", "NATURAL", "NO", "NOT", "NOTHING",
    "NULL", "OF", "OFFSET", "ON", "OR",
    "ORDER", "OUTER", "PLAN", "PRAGMA", "PRIMARY",
    "QUERY", "RAISE", "RECURSIVE", "REFERENCES", "REGEXP",
    "REINDEX", "RELEASE", "RENAME", "REPLACE",
    "RESTRICT", "RIGHT", "ROLLBACK", "ROW", "SAVEPOINT",
    "SELECT", "SET", "TABLE", "TEMP", "TEMPORARY",
    "THEN", "TIES", "TO", "TRANSACTION", "TRIGGER",
    "UNION", "UNIQUE", "UPDATE", "USING", "VACUUM",
    "VALUES", "VIEW", "VIRTUAL", "WHEN", "WHERE",
    "WITH", "WITHOUT"
]

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


class SQLiteDataEngine:
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
