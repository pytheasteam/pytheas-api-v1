import datetime
import json
import os
import requests
from trip_builder.routes_builder.route_builder_strategy_base import RoutesBuilderStrategyBase
from trip_builder.trip_builder_strategy_base import TripBuilderStrategyBase
from trip_builder.config import bing_api
import googlemaps
from math import sin, cos, sqrt, atan2, radians

MAX_HOURS_PER_DAY = 8  # Hours
KM_AVERAGE_WALKING_TIME = 0.25  # Hours
MAX_KM_PER_DAY = MAX_HOURS_PER_DAY / 2


class Hotel:
    def __init__(self, hotel):
        self.id = 'hotel'
        self.address = hotel['address']
        self.hotel = hotel


class CityWalkTripBuilder(TripBuilderStrategyBase):

    def __init__(self, route_builder_strategy):
        # type: (RoutesBuilderStrategyBase) -> None
        self.route_type = bing_api.RouteType.WALKING
        self.route_builder = route_builder_strategy
        self.attractions_distance = None

    def build_trip(self, trip_duration, attraction_list, city, hotel=None):
        # type: (int, list, str, str) -> list
        """
        Build trips for city walk based attractions
        best for Art, Families and friends
        :param trip_duration: trip duration in days (number)
        :param attraction_list:attraction list from agent
        :param city: destination
        :param hotel: trip hotel's  details
        :return: list of attractions sub lists. each sub list represent a day in a trip
        """

        # TODO: Check if there is enough attractions in attraction list.
        #  if there is more than duration * 6 -> takes the first duration * 6
        #  if there is less than duration * 6 -> return error
        starting_point = Hotel(hotel) if hotel is not None else attraction_list.pop()
        attraction_list.append(starting_point)
        if self.attractions_distance is None or len(self.attractions_distance) is 0:
            self.attractions_distance = self._get_distances_between_attractions(attraction_list, self.route_type)
            print(self.attractions_distance)
        routes = self.route_builder.build_routes(
            number_of_routes=int(trip_duration),
            attraction_list=attraction_list,
            attraction_distance_dict=self.attractions_distance,
            max_km_per_route=MAX_KM_PER_DAY,
            starting_point=starting_point,
            city=city
        )
        return routes

    @staticmethod
    def _get_distances_between_attractions(attraction_list, route_type):
        distances = {}
        attraction_coord = {}  # { id: { lat: lng: } }
        google = googlemaps.Client(key=os.environ.get('GOOGLE_API'))
        print(datetime.datetime.now())
        for attraction in attraction_list:
            res = google.geocode(attraction.address)
            attraction_coord[attraction.id] = res[0]['geometry']['location']
        for attraction in attraction_coord:
            distances[attraction] = {}
            for other_attraction in attraction_coord:
                if attraction != other_attraction:

                    R = 6373.0

                    lat1 = radians(attraction_coord[attraction]["lat"])
                    lon1 = radians(attraction_coord[attraction]["lng"])
                    lat2 = radians(attraction_coord[other_attraction]["lat"])
                    lon2 = radians(attraction_coord[other_attraction]["lng"])

                    dlon = lon2 - lon1
                    dlat = lat2 - lat1

                    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
                    c = 2 * atan2(sqrt(a), sqrt(1 - a))

                    distance = R * c
                    distances[attraction][other_attraction] = distance
        print(datetime.datetime.now())
        return distances


    @staticmethod
    def _get_distances_between_attractions_old(attraction_list, route_type):
        #  type: (list, bing_api.RouteType) -> dict
        """

        :param attraction_list: list of all attraction
        :param route_type: Route type like walking / driving etc..
        :return: dictionary where the keys are attraction_id and value is the distances from attraction to other
        attractions in list
        """

        number_of_locations = 2  # Get location between 2 attractions each time
        distances = {}
        temp_attraction_list = list(attraction_list)
        match_counter = 0
        while temp_attraction_list:
            print(match_counter)
            match_counter = 0
            attraction = temp_attraction_list.pop()
            print(f"{len(temp_attraction_list)} left")
            if attraction.id not in distances:
                distances[attraction.id] = {}
            for other_attraction in temp_attraction_list:
                params = {
                    'wayPoint.1': attraction.address,
                    'wayPoint.2': other_attraction.address,
                    "wayPoint.n": number_of_locations,
                    'key': bing_api.API_KEY
                }
                if other_attraction.id not in distances:
                    distances[other_attraction.id] = {}
                try:
                    distances[attraction.id][other_attraction.id]
                except:
                    r = requests.get(url=f'{bing_api.API_ENDPOINT}/Walking', params=params)
                    data = json.loads(r.content)
                    try:
                        distance = data['resourceSets'][0]['resources'][0]['travelDistance']
                    except Exception as e:
                        pass
                    else:
                        distances[attraction.id][other_attraction.id] = distance
                        distances[other_attraction.id][attraction.id] = distance
                        match_counter += 1
        return distances

