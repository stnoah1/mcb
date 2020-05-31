import pandas as pd
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder

from config import dbhost, user, password, database


class DBConn:
    def __init__(self):
        self.port = 5432

    def __enter__(self):
        self.engine = create_engine(
            f'postgresql://{user}:{password}@{dbhost}:{self.port}/{database}')
        return self

    def read(self, q):
        return pd.read_sql_query(q, con=self.engine)

    def insert_df(self, df, table):
        return df.to_sql(table, self.engine, if_exists='append', index=False)

    def insert(self, table, ignore=False, pk='id', **params):
        keys = ",".join(params.keys())
        values = ",".join("\'" + str(value) + "\'" for value in params.values())
        output = self.engine.execute(
            f'INSERT INTO {table} ({keys}) '
            f'VALUES ({values}) '
            f'{"ON CONFLICT DO NOTHING" if ignore else ""} '
            f'RETURNING {pk};'
        ).fetchall()
        if output:
            return output[0][0]
        else:
            return None

    def raw_query(self, q, multi=False):
        self.engine.execute(q, multi=multi)

    def delete(self, table, **params):
        condition = "AND".join(f"{key} = {value}" for key, value in params.items())
        self.engine.execute(
            f'DELETE FROM {table} '
            f'WHERE {condition};'
        )

    def __exit__(self, type, value, traceback):
        self.engine.dispose()


def read(q):
    with DBConn() as conn:
        return conn.read(q)


def insert_df(df, table):
    with DBConn() as conn:
        return conn.insert_df(df, table)


def insert(table, **params):
    with DBConn() as conn:
        return conn.insert(table, **params)


def query(q):
    with DBConn() as conn:
        conn.raw_query(q)


def multi_query(q):
    with DBConn() as conn:
        conn.raw_query(q, multi=True)


def delete(table, **params):
    with DBConn() as conn:
        conn.delete(table, **params)
