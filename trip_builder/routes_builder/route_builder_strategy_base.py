import re
import sys
from abc import ABCMeta, abstractmethod
from api.models.attraction import Attraction

CANNOT_CALCULATE_TIME_ERROR = sys.maxsize


class RoutesBuilderStrategyBase:
    __metaclass__ = ABCMeta

    @staticmethod
    def get_attraction_suggested_duration(attraction):
        # type: (Attraction) -> float
        description = attraction.description

        try:
            suggested_duration = description.splite('Suggested duration')[1]
        except KeyError:
            return CANNOT_CALCULATE_TIME_ERROR

        suggested_duration = [int(s) for s in re.findall(r'-?\d+\.?\d*', suggested_duration)]
        if len(suggested_duration) > 1:
            return -1 * (suggested_duration[0]*suggested_duration[1] / 2)
        elif len(suggested_duration) > 0:
            return suggested_duration[0]
        return CANNOT_CALCULATE_TIME_ERROR

    @abstractmethod
    def build_routes(self, number_of_routes, attraction_list, max_km_per_route, starting_point):
        # type: (int, list, int, Attraction) -> list
        """
        Build routes according to the build routes strategy
        :param number_of_routes: number of different wanted routes
        :param attraction_list: list of attractions that the routes will based on them
        :param max_km_per_route: max km between all the attractions in route
        :param starting_point: the first attraction in the route
        :return: list of number_of_routes sub lists, each list contains a route
        """
        pass
