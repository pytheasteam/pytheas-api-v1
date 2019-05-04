import json
import requests
from trip_builder.routes_builder.route_builder_strategy_base import RoutesBuilderStrategyBase
from trip_builder.trip_builder_strategy_base import TripBuilderStrategyBase
from trip_builder.config import bing_api

MAX_HOURS_PER_DAY = 8  # Hours
KM_AVERAGE_WALKING_TIME = 0.25  # Hours
MAX_KM_PER_DAY = MAX_HOURS_PER_DAY / 2


class CityWalkTripBuilder(TripBuilderStrategyBase):

    def __init__(self, route_builder_strategy, hotel=None):
        # type: (RoutesBuilderStrategyBase, str) -> None
        self.route_type = bing_api.RouteType.WALKING
        self.hotel = hotel
        self.route_builder = route_builder_strategy

    def build_trip(self, trip_duration, attraction_list):
        # type: (int, list) -> list
        """
        Build trips for city walk based attractions
        best for Art, Families and friends
        :param trip_duration: trip duration in days (number)
        :param attraction_list:attraction list from agent
        :return: list of attractions sub lists. each sub list represent a day in a trip
        """

        # TODO: Check if there is enough attractions in attraction list.
        #  if there is more than duration * 6 -> takes the first duration * 6
        #  if there is less than duration * 6 -> return error

        attractions_distance_dict = self._get_distances_between_attractions(attraction_list, self.route_type)
        starting_point = self.hotel if self.hotel is not None else attraction_list.pop()
        routes = self.route_builder.build_routes(
            number_of_routes=trip_duration,
            attraction_list=attraction_list,
            attraction_distance_dict=attractions_distance_dict,
            max_km_per_route=MAX_KM_PER_DAY,
            starting_point=starting_point

        )
        return routes

    @staticmethod
    def _get_distances_between_attractions(attraction_list, route_type):
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
        while temp_attraction_list:
            attraction = temp_attraction_list.pop()
            if attraction.name not in distances:
                distances[attraction.name] = {}
            for other_attraction in temp_attraction_list:
                params = {
                    'wayPoint.1': attraction.address,
                    'wayPoint.2': other_attraction.address,
                    "wayPoint.n": number_of_locations,
                    'key': bing_api.API_KEY
                }
                r = requests.get(url=bing_api.API_ENDPOINT + route_type, params=params)
                data = json.loads(r.content)
                distance = data['resourceSets'][0]['resources'][0]['travelDistance']
                distances[attraction.id][other_attraction.id] = distance
                distance[other_attraction.id][attraction.id] = distance
        return distances

