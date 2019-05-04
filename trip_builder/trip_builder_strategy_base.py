from abc import ABCMeta, abstractmethod


class TripBuilderStrategyBase:
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_trip(self, trip_duration, attraction_list):
        # type: (int, list) -> list

        """
        Build trip according to the strategy
        :param trip_duration: Duration of the trip in days
        :param attraction_list: List of optional attractions
        :return: list of attraction sub lists separated by days
        """
        pass
