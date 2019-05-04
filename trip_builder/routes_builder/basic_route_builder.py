from trip_builder.routes_builder.route_builder_strategy_base import RoutesBuilderStrategyBase


class BasicRoutesBuilder(RoutesBuilderStrategyBase):

    def __init__(self):
        super().__init__()
        self.routes = []

    def build_routes(self, number_of_routes, attraction_list, attraction_distance_dict, max_km_per_route,
                     starting_point):
        routes = [[starting_point] for i in range(0, number_of_routes)]
        for i, attraction in enumerate(attraction_list):
            routes[i % number_of_routes].append(attraction)
        return routes
