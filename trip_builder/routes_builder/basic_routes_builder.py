from api.models.attraction import Attraction
from trip_builder.routes_builder.route_builder_strategy_base import RoutesBuilderStrategyBase

MAX_HOURS_PER_DAY = 8  # Hours
KM_AVERAGE_WALKING_TIME = 0.25  # Hours


class BasicRoutesBuilder(RoutesBuilderStrategyBase):

    @staticmethod
    def _build_one_route(attraction_list, max_km_per_route, starting_point):
        # type: (list, int, Attraction) -> dict
        total_time = 0
        return {
            'total_route_time': total_time
        }

    def build_routes(self, number_of_routes, attraction_list, max_km_per_route, starting_point):
        pass
