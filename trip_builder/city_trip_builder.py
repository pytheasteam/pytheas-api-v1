import json
import requests
from trip_builder.routes_builder.route_builder_strategy_base import RoutesBuilderStrategyBase
from trip_builder.trip_builder_strategy_base import TripBuilderStrategyBase
from trip_builder.config import bing_api

MAX_HOURS_PER_DAY = 8  # Hours
KM_AVERAGE_WALKING_TIME = 0.25  # Hours
MAX_KM_PER_DAY = MAX_HOURS_PER_DAY / 2


class CityWalkTripBuilder(TripBuilderStrategyBase):

    def __init__(self, route_builder_strategy):
        # type: (RoutesBuilderStrategyBase, str) -> None
        self.route_type = bing_api.RouteType.WALKING
        self.route_builder = route_builder_strategy
        self.attractions_distance = None

    def build_trip(self, trip_duration, attraction_list, city, hotel=None):
        # type: (int, list, str) -> list
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

        if self.attractions_distance is None or len(self.attractions_distance) is 0:
            self.attractions_distance = self._get_distances_between_attractions(attraction_list, self.route_type)
        starting_point = hotel if hotel is not None else attraction_list.pop()
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
                r = requests.get(url=f'{bing_api.API_ENDPOINT}/Walking', params=params)
                data = json.loads(r.content)
                try:
                    distance = data['resourceSets'][0]['resources'][0]['travelDistance']
                except Exception as e:
                    pass
                else:
                    distances[attraction.id][other_attraction.id] = distance
                    distances[other_attraction.id][attraction.id] = distance
        return distances

