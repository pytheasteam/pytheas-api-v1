import json
import requests
from trip_builder.trip_builder_strategy_base import TripBuilderStrategyBase
from trip_builder.config import bing_api


class CityWalkTripBuilder(TripBuilderStrategyBase):

    def __init__(self, hotel):
        self.route_type = bing_api.RouteType.WALKING
        self.hotel = hotel

    def build_trip(self, trip_duration, attraction_list):
        """
        Build trips for city walk based attractions
        best for Art, Families and friends
        :param trip_duration: trip duration in number
        :param attraction_list:attraction list
        :return: list of attractions sub lists. each sub list represent a day in a trip
        """

        # TODO: Check if there is enough attractions in attraction list.
        #  if there is more than duration * 6 -> takes the first duration * 6
        #  if there is less than duration * 6 -> return error

        attractions_distance_dict = self._get_route_between_attractions(attraction_list, self.route_type)
        all_attractions = list(attractions_distance_dict.keys())
        sorted_attraction = []
        min_radius = 1
        max_radius = 3
        radius = min_radius
        passed_attractions = []
        while all_attractions:
            current_attraction = all_attractions.pop()
            current_attraction_neighbors = self._get_all_neighbors(
                attraction_name=current_attraction,
                attraction_distance_dict=attractions_distance_dict[current_attraction],
                radius=radius
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

    def _get_route_between_attractions(self,
                                       attraction_list, route_type):
        #  type: (list, bing_api.RouteType) -> dict

        number_of_locations = 2  # Get location between 2 attractions each time
        distances = {}
        temp_attraction_list = list(attraction_list)
        while temp_attraction_list:
            attraction = temp_attraction_list.pop()
            if attraction['name'] not in distances:
                distances[attraction['name']] = {}
            for other_attraction in temp_attraction_list:
                params = {
                    'wayPoint.1': attraction['address'],
                    'wayPoint.2': other_attraction['address'],
                    "wayPoint.n": number_of_locations,
                    'key': bing_api.API_KEY
                }
                r = requests.get(url=bing_api.API_ENDPOINT + route_type, params=params)
                data = json.loads(r.content)
                distance = data['resourceSets'][0]['resources'][0]['travelDistance']
                distances[attraction][other_attraction] = distance
                distance[other_attraction][attraction] = distance
        return distances
        # print(json.dumps(distances, indent=4))

    def _get_all_neighbors(self, attraction_name, attraction_distance_dict, radius):
        neighbors = []
        for neighbor in attraction_distance_dict:
            if attraction_distance_dict[neighbor] <= radius:
                neighbors.append(neighbor)
                neighbors.append(attraction_name)
        return list(set(neighbors))


# if __name__ == '__main__':
#  attractions_distance_dict = get_route_between_attractions(attractions)
#  sorted_att = split_attractions_into_days(attractions_distance_dict, 2)
#  print(sorted_att)
