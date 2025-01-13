import requests
import random
import time
import json

# The Flask server address (the one from your Flet app)
flask_server_url = "http://127.0.0.1:5000/update"

# Example device names
devices = ["Device 1", "Device 2", "Device 3", "Device 4", "Device 5", "Device 6", "Device 7", "Device 8"]

def generate_fake_data(device):
    # Generate fake sensor data
    return {
        "device": device,
        "temperature_aht25": round(random.uniform(20.0, 30.0), 2),
        "humidity_aht25": round(random.uniform(30.0, 60.0), 2),
        "pressure_bmp280": round(random.uniform(980.0, 1050.0), 2),
        "altitude_bmp280": round(random.uniform(100.0, 500.0), 2),
        "soil_moisture": round(random.uniform(10.0, 60.0), 2),
    }

def send_data():
    while True:
        for device in devices:
            # Generate random data for each device
            device_data = generate_fake_data(device)

            # Send data to Flask server via HTTP POST
            try:
                response = requests.post(flask_server_url, json=device_data)
                if response.status_code == 200:
                    print(f"Data sent for {device}: {device_data}")
                else:
                    print(f"Failed to send data for {device}")
            except requests.exceptions.RequestException as e:
                print(f"Error sending data: {e}")
        
        # Wait before sending the next set of data
        time.sleep(2)

if __name__ == "__main__":
    send_data()
