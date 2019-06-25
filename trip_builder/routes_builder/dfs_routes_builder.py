from api.models.attraction import Attraction
from trip_builder.routes_builder.route_builder_strategy_base import RoutesBuilderStrategyBase

MAX_ATTRACTIONS_PER_DAY = 5
MAX_KM_PER_ROUTE = 5
MAX_KM_PER_ATTRACTIONS = 3


class DFSRoutesBuilder(RoutesBuilderStrategyBase):

    def __init__(self):
        super().__init__()
        self.routes = []

    def build_routes(self, number_of_routes, attraction_list, attraction_distance_dict, max_km_per_route,
                     starting_point, city):
        all_attractions = list(attraction_distance_dict.keys())
        radius = 1
        selected_attractions = []
        hotel = all_attractions[0] # Always the first attraction is the hotel
        all_attractions = all_attractions[1:]
        while all_attractions and len(self.routes) < number_of_routes:
            route, attraction_list = self.build_one_route(all_attractions, attraction_distance_dict, MAX_KM_PER_ROUTE, radius, hotel, [], selected_attractions)
            selected_attractions.extend(route)
            full_attraction_routes = [self.serialize_attraction(Attraction.query.get(attraction)) for attraction in route]
            hotel_route = [self.serialize_hotel(starting_point.hotel, city)]
            hotel_route.extend(full_attraction_routes)
            self.routes.append(hotel_route)
        return self.routes

    def build_one_route(self, attraction_list, attraction_distance_dict, max_km_per_route, radius, starting_point, route, selected_attractions):
        next_attractions = self.get_all_attractions_in_radius(
            starting_point,
            attraction_distance_dict[starting_point],
            radius
        )
        next_attractions = [attraction for attraction in next_attractions if attraction not in selected_attractions]
        if not next_attractions and radius < MAX_KM_PER_ATTRACTIONS:
            return self.build_one_route(
                attraction_list,
                attraction_distance_dict,
                max_km_per_route,
                radius+1,
                starting_point,
                route,
                selected_attractions
            )
        if len(route) < MAX_ATTRACTIONS_PER_DAY and len(next_attractions) > 0:
            next_attraction = next_attractions.pop()
            while next_attraction in route:
                if next_attractions:
                    next_attraction = next_attractions.pop()
                else:
                    return route, attraction_list
            try:
                attraction_list.remove(next_attraction)
            except:
                pass
            route.append(next_attraction)
            self.build_one_route(attraction_list, attraction_distance_dict, max_km_per_route, radius, next_attraction, route, selected_attractions)
        return route, attraction_list


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