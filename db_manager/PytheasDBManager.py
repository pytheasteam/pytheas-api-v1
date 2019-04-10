from errno import errorcode

import mysql as mysql

from db_manager.db_manager_base import DBManagerBase


class PytheasDBManager(DBManagerBase):

    def __init__(self, app_config, crawler_config):
        self.app_db_client = None
        self.crawler_db_client = None
        self.app_config = app_config
        self.crawler_config = crawler_config

    def find(self, table_name, **kwargs):
        pass

    def delete(self, table_name, **kwargs):
        pass

    def insert(self, table_name, **kwargs):
        d = dict(kwargs)
        columns = ','.join(d.keys())
        placeholders = ','.join(['%s'] * len(d))
        values = tuple(d.values())
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
        self.cur.execute(query, values)
        self.db.commit()

    def connect(self):
        try:
            self.db = mysql.connector.connect(**self.app_config)
            self.cur = self.db.cursor()

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Bad username or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            print("db connected!")



