import re
from abc import ABCMeta, abstractmethod
from api.models.attraction import Attraction
from trip_builder.routes_builder.consts import CANNOT_CALCULATE_TIME_ERROR, ONLY_DIGIT_REGEX, \
    DURATION_IDENTIFIER_IN_DESCRIPTION


class RoutesBuilderStrategyBase:
    __metaclass__ = ABCMeta

    @staticmethod
    def get_all_attractions_in_radius(pivot_attraction_id, attraction_distance_dict, radius):
        # type: (Attraction, dict, int) -> list
        """
        :param pivot_attraction_id: The attraction which we want to get the distance from
        :param attraction_distance_dict: dictionary with distances between the pivot attractions to other attractions
        :param radius: the radius from pivot attraction to other attractions
        :return: list of all attractions that in radius from pivot
        """
        neighbors = []
        for potential_neighbor in attraction_distance_dict[pivot_attraction_id]:
            if attraction_distance_dict[potential_neighbor] <= radius:
                neighbors.append(potential_neighbor)
        return list(set(neighbors))

    @staticmethod
    def get_attraction_suggested_duration(attraction):
        # type: (Attraction) -> float
        description = attraction.description

        try:
            suggested_duration = description.splite(DURATION_IDENTIFIER_IN_DESCRIPTION)[1]
        except KeyError:
            return CANNOT_CALCULATE_TIME_ERROR

        suggested_duration = [int(s) for s in re.findall(ONLY_DIGIT_REGEX, suggested_duration)]
        if len(suggested_duration) > 1:
            duration_time = (suggested_duration[0]*suggested_duration[1]) / 2  # Average time between X-Y expression
            return duration_time if duration_time > 0 else -1*duration_time
        elif len(suggested_duration) > 0:
            return suggested_duration[0]
        return CANNOT_CALCULATE_TIME_ERROR

    @abstractmethod
    def build_routes(self, number_of_routes, attraction_list, attraction_distance_dict, max_km_per_route, starting_point):
        # type: (int, list, dict, float, Attraction) -> list
        """
        Build routes according to the build routes strategy
        :param number_of_routes: number of different wanted routes
        :param attraction_list: list of attractions that the routes will based on them
        :param max_km_per_route: max km between all the attractions in route
        :param starting_point: the first attraction in the route
        :param attraction_distance_dict: dictionary with distances between attractions
        :return: list of number_of_routes sub lists, each list contains a route
        """
        pass
