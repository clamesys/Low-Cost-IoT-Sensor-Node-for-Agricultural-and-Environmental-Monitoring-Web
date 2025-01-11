import flet as ft
import threading
import time
import json
import socket
import os
from flask import Flask, request
from waitress import serve

# Flask server to receive data from Raspberry Pi Pico W
app = Flask(__name__)

# List to store received device data
devices_data = []

@app.route('/update', methods=['POST'])
def update_device_data():
    global devices_data
    # Receive JSON data from the Pico and update the list
    device_data = request.json
    print(f"Received data: {device_data}")

    # Update the device data or append if it's a new device
    updated = False
    for i, device in enumerate(devices_data):
        if device["device"] == device_data["device"]:
            devices_data[i] = device_data
            updated = True
            break
    if not updated:
        devices_data.append(device_data)

    return "Data received", 200

# Get the local IP address of the machine
def get_ip():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)
    return ip_address

# Flet app to display the data
def main(page: ft.Page):
    page.title = "Real-Time Monitoring Dashboard"
    page.padding = 20
    page.scroll = "adaptive"

    # Get the local IP address
    ip_address = get_ip()

    # Header
    page.add(
        ft.Text(
            "Real-Time Monitoring Dashboard",
            size=40,
            weight=ft.FontWeight.BOLD,
            color="blue"
        )
    )

    # Display the IP address on the dashboard
    ip_label = ft.Text(
        f"Server IP Address: {ip_address}",
        size=20,
        weight=ft.FontWeight.BOLD,
        color="green"
    )
    page.add(ip_label)

    # Table for device data
    data_table = ft.DataTable(
        columns=[
            ft.DataColumn(ft.Text("Device")),
            ft.DataColumn(ft.Text("Temperature (°C)")),
            ft.DataColumn(ft.Text("Humidity (%)")),
            ft.DataColumn(ft.Text("Pressure (hPa)")),
            ft.DataColumn(ft.Text("Altitude (m)")),
            ft.DataColumn(ft.Text("Soil Moisture (%)")),
        ],
        rows=[],
    )

    # Function to update table rows
    def update_table():
        while True:
            data_table.rows.clear()
            for device in devices_data:
                data_table.rows.append(
                    ft.DataRow(
                        cells=[
                            ft.DataCell(ft.Text(device["device"])),
                            ft.DataCell(ft.Text(f"{device['temperature_aht25']:.1f}")),
                            ft.DataCell(ft.Text(f"{device['humidity_aht25']:.1f}")),
                            ft.DataCell(ft.Text(f"{device['pressure_bmp280']:.1f}")),
                            ft.DataCell(ft.Text(f"{device['altitude_bmp280']:.1f}")),
                            ft.DataCell(ft.Text(f"{device['soil_moisture']:.1f}")),
                        ]
                    )
                )
            page.update()
            time.sleep(1)  # Update every second

    # Add the table to the page
    page.add(data_table)

    # Start a thread to update the table dynamically
    threading.Thread(target=update_table, daemon=True).start()

    # Function to clear all data and reset the UI
    def clear_data(e):
        global devices_data
        devices_data.clear()  # Clear the device data list
        data_table.rows.clear()  # Clear the rows in the table
        page.update()  # Refresh the page

    # Clear button
    clear_button = ft.ElevatedButton("Clear Data", on_click=clear_data)
    page.add(clear_button)

# Start Flask server in production mode (using Waitress)
def start_flask_server():
    serve(app, host="0.0.0.0", port=5000, clear_untrusted_proxy_headers=False)

# Run both the Flask and Flet apps in separate threads
if __name__ == "__main__":
    # Start Flask server in a background thread
    flask_thread = threading.Thread(target=start_flask_server, daemon=True)
    flask_thread.start()

    # Run the Flet app in web mode
    ft.app(target=main, view=ft.WEB_BROWSER, port=int(os.environ.get("PORT", 5000)))
