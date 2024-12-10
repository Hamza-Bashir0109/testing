import pandas as pd
import sys
import math

class Airport:
    def __init__(self, airport_id, name, city, country):
        self.id = airport_id
        self.name = name
        self.city = city
        self.country = country

class AdjNode:
    def __init__(self, airport_id, distance, cost, time):
        self.airport_id = airport_id
        self.distance = distance
        self.cost = cost
        self.time = time
        self.next = None

class AdjList:
    def __init__(self):
        self.head = None

class FlightGraph:
    def __init__(self, max_airports):
        self.num_airports = max_airports
        self.adjacency_list = [AdjList() for _ in range(max_airports)]
        self.airports = [None] * max_airports

    def load_airports_from_csv(self, file_name):
        try:
            df = pd.read_csv(file_name)
            for _, row in df.iterrows():
                if not str(row['id']).isdigit():
                    print(f"Skipping invalid entry: {row}")
                    continue

                airport_id = int(row['id'])
                self.add_airport(
                    airport_id, row['name'], row['city'], row['country']
                )

            print(f"Airports loaded successfully from {file_name}")
        except FileNotFoundError:
            print(f"Error: Could not open file {file_name}")

    def add_airport(self, airport_id, name, city, country):
        if airport_id >= self.num_airports or airport_id < 0:
            print("Error: Invalid Airport ID!")
            return

        if self.airports[airport_id] is not None:
            print("Error: Airport ID already exists!")
            return

        self.airports[airport_id] = Airport(airport_id, name, city, country)
        print("Airport added successfully.")

    def add_route(self, source_id, destination_id, distance, cost, time):
        if (
            source_id >= self.num_airports or
            destination_id >= self.num_airports or
            source_id < 0 or destination_id < 0
        ):
            print("Error: Invalid Airport IDs for the route!")
            return

        if self.airports[source_id] is None or self.airports[destination_id] is None:
            print("Error: One or both airports do not exist!")
            return

        new_node = AdjNode(destination_id, distance, cost, time)
        new_node.next = self.adjacency_list[source_id].head
        self.adjacency_list[source_id].head = new_node
        print("Route added successfully.")

    def dijkstra(self, start_id, dest_id, criterion):
        inf = math.inf
        values = [inf] * self.num_airports
        previous = [-1] * self.num_airports
        visited = [False] * self.num_airports

        values[start_id] = 0

        for _ in range(self.num_airports):
            current = -1
            min_value = inf

            for i in range(self.num_airports):
                if not visited[i] and values[i] < min_value:
                    current = i
                    min_value = values[i]

            if current == -1:
                break

            visited[current] = True

            neighbor = self.adjacency_list[current].head
            while neighbor:
                new_value = values[current]
                if criterion == "distance":
                    new_value += neighbor.distance
                elif criterion == "cost":
                    new_value += neighbor.cost
                elif criterion == "time":
                    new_value += neighbor.time

                if new_value < values[neighbor.airport_id]:
                    values[neighbor.airport_id] = new_value
                    previous[neighbor.airport_id] = current

                neighbor = neighbor.next

        if values[dest_id] == inf:
            print(f"No path exists from Airport {start_id} to Airport {dest_id}.")
        else:
            print(f"Optimal path ({criterion}): {values[dest_id]}")
            print("Path: ", end="")
            self.print_path(previous, dest_id)
            print()

    def print_path(self, previous, current_id):
        if current_id == -1:
            return

        self.print_path(previous, previous[current_id])
        if self.airports[current_id]:
            print(self.airports[current_id].name, end=" ")
        else:
            print(current_id, end=" ")

# Example usage
if __name__ == "__main__":
    max_airports = 1000
    graph = FlightGraph(max_airports)
    graph.load_airports_from_csv("route.csv")

    while True:
        print("\nMenu:")
        print("1. Add Airport")
        print("2. Add Route")
        print("3. Find Optimal Path")
        print("4. Exit")

        choice = input("Enter your choice: ")
        if choice == "1":
            airport_id = int(input("Enter Airport ID: "))
            name = input("Enter Airport Name: ")
            city = input("Enter City: ")
            country = input("Enter Country: ")
            graph.add_airport(airport_id, name, city, country)
        elif choice == "2":
            source = int(input("Enter Source Airport ID: "))
            destination = int(input("Enter Destination Airport ID: "))
            distance = float(input("Enter Distance: "))
            cost = float(input("Enter Cost: "))
            time = float(input("Enter Time: "))
            graph.add_route(source, destination, distance, cost, time)
        elif choice == "3":
            source = int(input("Enter Source Airport ID: "))
            destination = int(input("Enter Destination Airport ID: "))
            criterion = input("Enter Criterion (distance/cost/time): ")
            graph.dijkstra(source, destination, criterion)
        elif choice == "4":
            print("Thank you for using the Flight Route Optimization System!")
            break
        else:
            print("Invalid choice. Please try again.")
