from api.models.city import City
from trip_builder.routes_builder.route_builder_strategy_base import RoutesBuilderStrategyBase


class BasicRoutesBuilder(RoutesBuilderStrategyBase):

    def __init__(self):
        super().__init__()
        self.routes = []

    def _serialize_attraction(self, attraction):
        return {
                    'id': attraction.id,
                    'name': attraction.name,
                    'rate': attraction.rate,
                    'address': attraction.address,
                    'price': attraction.price,
                    'description': attraction.description,
                    'phone number': attraction.phone_number,
                    'website': attraction.website,
                    'city': City.query.get(attraction.city_id).name,
                    'image_url': ''
                }

    def _serialize_hotel(self, hotel, city):
        return {
            'id': -1,
            'name': hotel['name'],
            'rate': 5,
            'address': hotel['address'],
            'price': hotel['price_per_night'],
            'description': '',
            'phone number': '',
            'website': hotel['url'],
            'city': city,
            'image_url': ''
        }

    def build_routes(self, number_of_routes, attraction_list, attraction_distance_dict, max_km_per_route,
                     starting_point, city):
        routes = [[self._serialize_hotel(starting_point, city)] for i in range(0, number_of_routes)]
        for i, attraction in enumerate(attraction_list):
            routes[i % number_of_routes].append(
                self._serialize_attraction(attraction)
            )
        return routes
