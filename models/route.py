from datetime import timedelta, datetime

from helpers.distances import distances
from helpers.functions import generate_id
from models.location import Location
from models.vehicle import Vehicle
from models.location import Location
import time

class Route:
    id_list = []

    def __init__(self, packages=None, locations=None, departure_time=None):
        self._route_id = generate_id(existing_ids=self.id_list)
        if locations:
            self.locations = locations
        elif packages:
            self.locations = self.generate_locations_from_packages(packages)
        else:
            raise ValueError("Either packages or locations must be provided.")

        if isinstance(departure_time, datetime):
            self.departure_time = departure_time
        else:
            self.departure_time = datetime.strptime(departure_time, '%d-%m-%Y %H:%M')
        self.truck = None

    @property
    def id(self):
        return self._route_id

    def generate_locations_from_packages(self, packages):
        location_order = []
        for package in packages:
            if package.start_location not in location_order:
                location_order.append(package.start_location)
            if package.end_location not in location_order:
                location_order.append(package.end_location)

        return [Location(name) for name in location_order]

    def calculate_travel_time(self, distance):
        average_speed = Vehicle.SPEED_CONSTANT
        return distance / average_speed

    def calculate_arrival_times(self):
        arrival_times = [self.departure_time]
        current_time = arrival_times[0]

        for i in range(len(self.locations) - 1):
            start = self.locations[i]
            end = self.locations[i + 1]
            distance = start.get_distance_to(end.name)
            travel_time_hours = self.calculate_travel_time(distance)
            travel_time_delta = timedelta(hours=travel_time_hours)
            current_time += travel_time_delta
            arrival_times.append(current_time)

        return [time.strftime('%d-%m-%Y %H:%M') for time in arrival_times]

    def next_stop(self, current_location):
        if current_location not in [loc.name for loc in self.locations]:
            raise ValueError(f"Current location {current_location} not on route.")

        current_index = [loc.name for loc in self.locations].index(current_location)
        if current_index < len(self.locations) - 1:
            return self.locations[current_index + 1].name
        return None  # No further stops

    def update_locations_for_packages(self, packages):
        for package in packages:
            start_location = Location(package.start_location)
            end_location = Location(package.end_location)
            if not any(location.name == start_location.name for location in self.locations):
                self.locations.append(start_location)
            if not any(location.name == end_location.name for location in self.locations):
                self.locations.append(end_location)

    def simulate_route(self):
        for n in range(len(self.locations) - 1):
            start_location = self.locations[n].name
            end_location = self.locations[n + 1].name
            route_distance = distances[start_location][end_location]
            route_duration = route_distance / Vehicle.SPEED_CONSTANT
            accelerated_seconds = route_duration * 3600  # Treat hours as seconds
            arrival_time = current_time + timedelta(seconds=accelerated_seconds)
            print(
                f"Simulating travel from {start_location} to {end_location}. Expected arrival: {arrival_time.strftime('%H:%M:%S')}")
            current_time = arrival_time
        print(f"Route {self.id} completed.")


    def __str__(self):
        arrival_times = self.calculate_arrival_times()
        stops_with_times = ', '.join(f"{loc.name} ({time})" for loc, time in zip(self.locations, arrival_times))
        return f"Route ID: {self.id}, Locations: {stops_with_times}, Truck ID: {self.truck.id_truck if self.truck else 'No truck assigned'}"

    def __len__(self):
        total_distance = 0
        for i in range(len(self.locations) - 1):
            start_location = self.locations[i]
            end_location = self.locations[i + 1]
            total_distance += start_location.get_distance_to(end_location.name)
        return total_distance