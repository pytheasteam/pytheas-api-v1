from abc import ABCMeta, abstractmethod


class TripBuilderStrategyBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_trip(self, trip_duration, attraction_list, city, hotel=None):
        # type: (int, list, str, list) -> list

        """
        Build trip according to the strategy
        :param city: destination
        :param trip_duration: Duration of the trip in days
        :param attraction_list: List of optional attractions
        :param hotel: trip hotel's  details
        :return: list of attraction sub lists separated by days
        """
        pass
