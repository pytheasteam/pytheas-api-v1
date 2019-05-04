from api.models.attraction import Attraction
from trip_builder.routes_builder.route_builder_strategy_base import RoutesBuilderStrategyBase


class DFSRoutesBuilder(RoutesBuilderStrategyBase):

    def __init__(self):
        super().__init__()
        self.routes = []

    def build_routes(self, number_of_routes, attraction_list, attraction_distance_dict, max_km_per_route,
                     starting_point):
        all_attractions = list(attraction_distance_dict.keys())
        sorted_attraction = []
        min_radius = 1
        max_radius = 3
        radius = min_radius
        passed_attractions = []
        while all_attractions and self.routes < number_of_routes:
            current_attraction = all_attractions.pop()
            current_attraction_neighbors = self.get_all_attractions_in_radius(
                current_attraction,
                attraction_distance_dict,
                radius
            )
            if current_attraction_neighbors:
                sorted_attraction.append(current_attraction_neighbors)
                all_attractions = [e for e in all_attractions if e not in current_attraction_neighbors]
            else:
                passed_attractions.append(current_attraction)
            if not all_attractions and radius < max_radius:
                all_attractions = passed_attractions
                passed_attractions = []
                radius += 1
        return sorted_attraction

    def build_one_route(self, attraction_list, attraction_distance_dict, max_km_per_route, starting_point):
        # type: (list, dict, int, Attraction) -> dict
        total_time = 0
        return {
            'total_route_time': total_time
        }


"""
function DFS(Start, Goal)
        Color(Start, Grey)
        if Start = Goal
            return True
        for Child in Expand(Node)
            if not Colored(Child)
                if DFS(Child, Goal)=True
                    return True
        Color(Start, Black)
        return False
"""