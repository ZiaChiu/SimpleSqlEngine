import sqlite3

from db import *
import matplotlib.pyplot as plt

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

