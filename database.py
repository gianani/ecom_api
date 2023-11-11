import psycopg2
import config


class Pgsql:
    def __init__(self):
        pgsql_config = config.pgsql
        self.conn = psycopg2.connect(
            host=pgsql_config["host"],
            database=pgsql_config["database"],
            user=pgsql_config["username"],
            password=pgsql_config["password"],
        )
        self.cur = self.conn.cursor()

    def query(self, query, args=None):
        self.cur.execute(query, args)

    def close(self):
        self.conn.close()
        self.cur.close()
