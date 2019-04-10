from abc import ABCMeta, abstractmethod
import mysql.connector



class DBManagerBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def insert(self, table_name, **kwargs):
        pass

    @abstractmethod
    def find(self, table_name, **kwargs):
        pass

    @abstractmethod
    def delete(self, table_name, **kwargs):
        pass

    def connect(self):
        pass




