import streamlit as st
import csv
import heapq
from collections import defaultdict

class Airport:
    def __init__(self, id, name, city, country):
        self.id = id
        self.name = name
        self.city = city
        self.country = country

class FlightGraph:
    def __init__(self):
        self.airports = {}
        self.adjacency_list = defaultdict(list)

    def load_airports_from_csv(self, file_name):
        try:
            with open(file_name, mode='r') as file:
                reader = csv.reader(file)
                for row in reader:
                    if len(row) < 4 or not row[0].isdigit():
                        continue
                    id = int(row[0])
                    self.add_airport(id, row[1], row[2], row[3])
            st.success("Airports loaded successfully.")
        except Exception as e:
            st.error(f"Error loading airports: {e}")

    def add_airport(self, id, name, city, country):
        if id in self.airports:
            st.error("Airport ID already exists!")
        else:
            self.airports[id] = Airport(id, name, city, country)
            st.success("Airport added successfully.")

    def add_route(self, source_id, dest_id, distance, cost, time):
        if source_id not in self.airports or dest_id not in self.airports:
            st.error("Invalid airport IDs!")
        else:
            self.adjacency_list[source_id].append((dest_id, distance, cost, time))
            st.success("Route added successfully.")

    def dijkstra(self, start_id, dest_id, criterion):
        if start_id not in self.airports or dest_id not in self.airports:
            st.error("Invalid airport IDs!")
            return
        criteria_index = {"distance": 1, "cost": 2, "time": 3}
        if criterion not in criteria_index:
            st.error("Invalid criterion!")
            return
        
        index = criteria_index[criterion]
        distances = {id: float('inf') for id in self.airports}
        previous = {id: None for id in self.airports}
        distances[start_id] = 0
        pq = [(0, start_id)]

        while pq:
            current_distance, current_id = heapq.heappop(pq)
            if current_distance > distances[current_id]:
                continue
            for neighbor, dist, cost, time in self.adjacency_list[current_id]:
                weight = [dist, cost, time][index - 1]
                new_distance = current_distance + weight
                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    previous[neighbor] = current_id
                    heapq.heappush(pq, (new_distance, neighbor))

        if distances[dest_id] == float('inf'):
            st.warning("No path exists!")
        else:
            path = []
            current = dest_id
            while current:
                path.append(self.airports[current].name)
                current = previous[current]
            path.reverse()
            st.success(f"Optimal {criterion}: {distances[dest_id]}")
            st.info(" -> ".join(path))

# Streamlit Interface
st.title("Flight Route Optimization System")
graph = FlightGraph()

st.sidebar.header("Options")
option = st.sidebar.selectbox("Choose an option", ["Load Airports", "Add Airport", "Add Route", "Find Optimal Path"])

if option == "Load Airports":
    uploaded_file = st.file_uploader("Upload CSV file")
    if uploaded_file:
        graph.load_airports_from_csv(uploaded_file)

elif option == "Add Airport":
    id = st.number_input("Airport ID", min_value=0, step=1)
    name = st.text_input("Airport Name")
    city = st.text_input("City")
    country = st.text_input("Country")
    if st.button("Add Airport"):
        graph.add_airport(id, name, city, country)

elif option == "Add Route":
    source = st.number_input("Source Airport ID", min_value=0, step=1)
    dest = st.number_input("Destination Airport ID", min_value=0, step=1)
    distance = st.number_input("Distance", min_value=0.0)
    cost = st.number_input("Cost", min_value=0.0)
    time = st.number_input("Time", min_value=0.0)
    if st.button("Add Route"):
        graph.add_route(source, dest, distance, cost, time)

elif option == "Find Optimal Path":
    source = st.number_input("Source Airport ID", min_value=0, step=1)
    dest = st.number_input("Destination Airport ID", min_value=0, step=1)
    criterion = st.selectbox("Criterion", ["distance", "cost", "time"])
    if st.button("Find Path"):
        graph.dijkstra(source, dest, criterion)
