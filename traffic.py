from flask import Flask, jsonify
from datetime import datetime
import random

app = Flask(__name__)

# Helper function to calculate weighted vehicle count based on speed and distance
def calculate_weighted_vehicle_count(vehicles):
    weighted_count = 0
    close_vehicles = 0
    far_vehicles = 0

    for vehicle in vehicles:
        speed = vehicle["speed"]  # Speed in km/h
        distance = vehicle["distance"]  # Distance in meters

        # Categorize vehicles by proximity
        if distance <= 500:
            close_vehicles += 1
        else:
            far_vehicles += 1

        # Apply speed weighting
        if speed < 20:  # Stuck vehicles
            speed_weight = 1
        elif 20 <= speed <= 40:  # Slow-moving vehicles
            speed_weight = 0.5
        else:  # Fast-moving vehicles
            speed_weight = 0.25

        # Apply distance weighting
        if distance <= 300:  # Close to the intersection
            distance_weight = 1
        elif 300 < distance <= 500:  # Slightly farther
            distance_weight = 0.5
        elif 500 < distance <= 800:  # Farther but relevant
            distance_weight = 0.25
        else:  # Too far to influence signal
            distance_weight = 0

        # Combine speed and distance weights
        weighted_count += speed_weight * distance_weight

    return round(weighted_count), close_vehicles, far_vehicles

# Helper function to calculate green light time
def calculate_green_light_time(vehicle_count, is_peak_hour=False):
    base_time = 20  # Start with a base time of 20 seconds
    vehicle_factor = vehicle_count * 2  # Add 2 seconds per vehicle
    peak_hour_adjustment = 10 if is_peak_hour else 0  # Add 10 seconds during peak hours

    # Calculate green light time
    green_light_time = base_time + vehicle_factor + peak_hour_adjustment

    # Cap the maximum green light time to 90 seconds
    return min(green_light_time, 90)

# Check if current time is peak hour
def is_peak_hour():
    current_hour = datetime.now().hour
    return 7 <= current_hour <= 9 or 17 <= current_hour <= 19  # Peak hours: 7-9 AM, 5-7 PM

@app.route('/')
def home():
    return "Welcome to the Intelligent Traffic Management System!"

@app.route('/traffic')
def traffic_info():
    # Simulate dynamic vehicle data
    # Each vehicle is represented as a dictionary with speed and distance
    vehicles = [
        {"speed": random.randint(10, 60), "distance": random.randint(100, 1000)}
        for _ in range(random.randint(1, 50))
    ]

    # Calculate weighted vehicle count and categorize vehicles
    weighted_count, close_vehicles, far_vehicles = calculate_weighted_vehicle_count(vehicles)

    # Check if it's peak hour
    peak_hour = is_peak_hour()

    # Calculate green light time
    green_light_time = calculate_green_light_time(weighted_count, peak_hour)

    # Determine location message (static for now)
    location_message = "Nearby Traffic Signal Detected" if close_vehicles > 0 else "No Traffic Detected"

    # Return traffic data response
    traffic_data = {
        "status": "success",
        "data": {
            "location": location_message,
            "traffic_light": "Green",
            "vehicles_detected": {
                "close": close_vehicles,
                "far": far_vehicles,
                "total": close_vehicles + far_vehicles
            },
            "green_light_time": green_light_time
        }
    }

    return jsonify(traffic_data)

if __name__ == '__main__':
    app.run(debug=True)
