from geopy import distance

class DistanceCalculator():

    def coordinates_in_range(self, base_coordinates: tuple, search_coordinates: tuple, min_distance: int, max_distance: int):
        calculated_distance = distance.distance(base_coordinates, search_coordinates).km
        in_range = False
        if min_distance >= 0:
            in_range = min_distance <= calculated_distance
        if max_distance > 0:
            in_range = in_range and (calculated_distance <= max_distance)
        return in_range