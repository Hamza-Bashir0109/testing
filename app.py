import streamlit as st
import pandas as pd
import numpy as np

class Airport:
    def __init__(self, id, name, city, jry):
        self.id = id
        self.name = name
        self.city = city
        self.jry = jry

class Route:
    def __init__(self, source_id, destination_id, distance, cost=0, time=0):
        self.source_id = source_id
        self.destination_id = destination_id
        self.distance = distance
        self.cost = cost
        self.time = time

class FlightSystem:
    def __init__(self, max_airports):
        self.max_airports = max_airports
        self.airports = {}
        self.routes = {}

    def add_airport(self, id, name, city, jry):
        if not name or not city or not jry:
            st.error("Error: All fields are required.")
            return
        if id in self.airports:
            st.error(f"Error: Airport with ID {id} already exists!")
            return
        self.airports[id] = Airport(id, name, city, jry)
        st.success(f"Airport '{name}' added successfully with ID {id}.")

    def add_route(self, source_id, destination_id, distance, cost=0, time=0):
        if source_id not in self.airports or destination_id not in self.airports:
            st.error("Error: One or both airports do not exist!")
            return
        if (source_id, destination_id) in self.routes:
            st.error("Error: Route already exists!")
            return
        self.routes[(source_id, destination_id)] = Route(source_id, destination_id, distance, cost, time)
        st.success(f"Route from {source_id} to {destination_id} added successfully.")

    def find_shortest_path(self, start_id, end_id, optimize_cost=False, optimize_time=False):
        from heapq import heappop, heappush

        distances = {id: float('inf') for id in self.airports}
        distances[start_id] = 0
        previous = {id: None for id in self.airports}
        pq = [(0, start_id)]

        while pq:
            current_distance, current_id = heappop(pq)
            if current_id == end_id:
                break
            if current_distance > distances[current_id]:
                continue

            for (source, destination), route in self.routes.items():
                if source != current_id:
                    continue
                weight = route.distance
                if optimize_cost:
                    weight = route.cost
                elif optimize_time:
                    weight = route.time

                distance = current_distance + weight
                if distance < distances[destination]:
                    distances[destination] = distance
                    previous[destination] = current_id
                    heappush(pq, (distance, destination))

        path = []
        current = end_id
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()

        if distances[end_id] == float('inf'):
            st.warning("No path found.")
        else:
            st.success(f"Shortest path: {' -> '.join(map(str, path))}")
            st.write(f"Total Distance: {distances[end_id]}")

    def save_routes(self, filename):
        data = [{
            "Source": src,
            "Destination": dest,
            "Distance": route.distance,
            "Cost": route.cost,
            "Time": route.time
        } for (src, dest), route in self.routes.items()]
        pd.DataFrame(data).to_csv(filename, index=False)
        st.success(f"Routes saved to {filename}.")

    def load_routes(self, filename):
        try:
            data = pd.read_csv(filename)
            for _, row in data.iterrows():
                self.add_route(int(row["Source"]), int(row["Destination"]),
                               float(row["Distance"]), float(row["Cost"]), float(row["Time"]))
            st.success(f"Routes loaded from {filename}.")
        except Exception as e:
            st.error(f"Error: {e}")

# Streamlit Interface
st.title("Flight Route Optimization System")

flight_system = FlightSystem(max_airports=1000)

menu = ["Add Airport", "Add Route", "Find Path", "Save/Load Routes", "View Airports"]
choice = st.sidebar.selectbox("Menu", menu)

if choice == "Add Airport":
    st.subheader("Add Airport")
    id = st.number_input("Airport ID", min_value=0, step=1)
    name = st.text_input("Airport Name").strip()
    city = st.text_input("City").strip()
    jry = st.text_input("Jurisdiction").strip()

    if st.button("Add Airport"):
        if id >= 0 and name and city and jry:
            flight_system.add_airport(int(id), name, city, jry)
        else:
            st.error("Error: Please fill out all fields correctly.")

elif choice == "Add Route":
    st.subheader("Add Route")
    source = st.number_input("Source Airport ID", min_value=0, step=1)
    dest = st.number_input("Destination Airport ID", min_value=0, step=1)
    distance = st.number_input("Distance", min_value=0.0, step=0.1)
    cost = st.number_input("Cost", min_value=0.0, step=0.1)
    time = st.number_input("Time", min_value=0.0, step=0.1)
    if st.button("Add Route"):
        flight_system.add_route(source, dest, distance, cost, time)

elif choice == "Find Path":
    st.subheader("Find Path")
    start = st.number_input("Starting Airport ID", min_value=0, step=1)
    end = st.number_input("Destination Airport ID", min_value=0, step=1)
    optimize = st.radio("Optimize for", ["Distance", "Cost", "Time"])
    if st.button("Find Path"):
        if optimize == "Distance":
            flight_system.find_shortest_path(start, end)
        elif optimize == "Cost":
            flight_system.find_shortest_path(start, end, optimize_cost=True)
        elif optimize == "Time":
            flight_system.find_shortest_path(start, end, optimize_time=True)

elif choice == "Save/Load Routes":
    st.subheader("Save or Load Routes")
    save_filename = st.text_input("Save filename")
    if st.button("Save Routes"):
        flight_system.save_routes(save_filename)

    load_filename = st.text_input("Load filename")
    if st.button("Load Routes"):
        flight_system.load_routes(load_filename)

elif choice == "View Airports":
    st.subheader("View Airports")
    if flight_system.airports:
        for airport_id, airport in flight_system.airports.items():
            st.write(f"ID: {airport_id}, Name: {airport.name}, City: {airport.city}, Jurisdiction: {airport.jry}")
    else:
        st.info("No airports added yet.")
