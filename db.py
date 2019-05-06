import pandas as pd
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder

from config import host, ssh_username, ssh_private_key, localhost, ssh_password, user, password, database


class DBConn:
    def __init__(self):
        self.port = 5432

        if config.ssh_tunel:
            self.server = SSHTunnelForwarder(
                (host, 22),
                ssh_username=ssh_username,
                ssh_private_key=ssh_private_key,
                remote_bind_address=(localhost, self.port),
                ssh_password=ssh_password,
            )
            self.server.start()
            self.port = self.server.local_bind_port

    def __enter__(self):
        self.server.__enter__()
        self.engine = create_engine(
            f'postgresql://{user}:{password}@{localhost}:{self.port}/{database}')
        return self

    def query(self, q):
        return pd.read_sql_query(q, con=self.engine)

    def insert_df(self, df, table):
        return df.to_sql(table, self.engine, if_exists='append', index=False)

    def insert(self, table, ignore=False, **params):
        keys = ",".join(params.keys())
        values = ",".join("\'" + str(value) + "\'" for value in params.values())
        return self.engine.execute(
                f'INSERT INTO {table} ({keys}) '
                f'VALUES ({values}) '
                f'{"ON CONFLICT DO NOTHING" if ignore else ""} '
                f'RETURNING id;'
        ).fetchall()[0][0]

    def __exit__(self, type, value, traceback):
        self.engine.dispose()
        self.server.__exit__()


def query(q):
    with DBConn() as conn:
        return conn.query(q)


def insert_df(df, table):
    with DBConn() as conn:
        return conn.insert_df(df, table)


def insert(table, **params):
    with DBConn() as conn:
        return conn.insert(table, **params)
