from abc import ABCMeta, abstractmethod


class PytheasDBManagerBase:
    __metaclass__ = ABCMeta

    def __init__(self, db):
        self.db = db

    #  CREATES FUNCTIONS
    @abstractmethod
    def create_user(self, username, full_name, email, google_token):
        pass

    @abstractmethod
    def create_tag(self, tag_name):
        pass

    @abstractmethod
    def create_attraction(self, name, rate, address, price, description, phone, website, city_id, attraction_id=None):
        pass

    @abstractmethod
    def create_city(self, name, country, city_id=None):
        pass

    @abstractmethod
    def create_profile(self, username, profile_name, tags):
        pass

    @abstractmethod
    def get_cities(self):
        pass

    @abstractmethod
    def get_tags(self):
        pass

    @abstractmethod
    def get_attractions(self, **kwargs):
        pass

    @abstractmethod
    def get_explore_trips(self, city, username, profile, days):
        pass

    @abstractmethod
    def get_profile(self, username):
        pass

