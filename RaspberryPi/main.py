from machine import Pin, ADC, I2C
from time import sleep
import ujson
import network
import usocket

# Pin configuration
# Capacitive Soil Moisture Sensor
soil_moisture = ADC(Pin(26))  # ADC0 (GP26)

# AHT25 (Temperature and Humidity Sensor)
i2c_aht25 = I2C(0, scl=Pin(1), sda=Pin(0))  # I2C0 (GP1 - SCL, GP0 - SDA)
AHT25_ADDR = 0x38  # I2C address for AHT25

# BMP280 (Pressure and Temperature Sensor)
i2c_bmp280 = I2C(1, scl=Pin(3), sda=Pin(2))  # I2C1 (GP3 - SCL, GP2 - SDA)
BMP280_ADDR = 0x76  # I2C address for BMP280

# WiFi configuration
WIFI_SSID = "wifi_ssid"
WIFI_PASSWORD = "wifi_password"

# Flask server configuration
FLASK_SERVER_IP = "192.168.1.100"  # Replace with your server's IP address
FLASK_SERVER_PORT = 5000
FLASK_ENDPOINT = "/update"

# Device ID
DEVICE_ID = "Device 1"

# Connect to WiFi
def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    print("Connecting to WiFi...", end="")
    while not wlan.isconnected():
        print(".", end="")
        sleep(1)
    print("\nConnected to WiFi!")
    print("IP Address:", wlan.ifconfig()[0])

# Read AHT25 data (Temperature and Humidity)
def read_aht25():
    i2c_aht25.writeto(AHT25_ADDR, b'\xAC\x33\x00')  # Start measurement
    sleep(0.5)  # Wait for measurement to complete
    data = i2c_aht25.readfrom(AHT25_ADDR, 6)
    humidity = ((data[1] << 8) | data[2]) * 100 / 0x10000
    temperature = (((data[3] & 0x7F) << 8) | data[4]) * 200 / 0x10000 - 50
    return temperature, humidity

# Read BMP280 data (Pressure)
def read_bmp280():
    data = i2c_bmp280.readfrom_mem(BMP280_ADDR, 0xF7, 6)
    pressure_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)

    # Simplified calibration (for demo purposes)
    pressure = pressure_raw / 25600.0
    altitude = 44330 * (1 - (pressure_raw / 101325) ** (1 / 5.255))
    return pressure, altitude

# Read Capacitive Soil Moisture Sensor
def read_soil_moisture():
    adc_value = soil_moisture.read_u16()  # 16-bit ADC value
    voltage = adc_value * 3.3 / 65535  # Convert to voltage
    soil_moisture_percentage = (voltage / 3.3) * 100  # Simplified percentage
    return soil_moisture_percentage

# Send data to Flask server
def send_data_to_flask(data):
    try:
        # Create a socket connection
        addr = usocket.getaddrinfo(f"{FLASK_SERVER_IP}", FLASK_SERVER_PORT)[0][-1]
        client_socket = usocket.socket()
        client_socket.connect(addr)
        
        # Format HTTP POST request
        payload = ujson.dumps(data)
        http_request = f"POST {FLASK_ENDPOINT} HTTP/1.1\r\n" \
                       f"Host: {FLASK_SERVER_IP}\r\n" \
                       f"Content-Type: application/json\r\n" \
                       f"Content-Length: {len(payload)}\r\n\r\n" \
                       f"{payload}"
        
        # Send request
        client_socket.send(http_request)
        client_socket.close()
        print("Data sent:", payload)
    except Exception as e:
        print("Failed to send data:", e)

# Main function
def main():
    connect_wifi()
    while True:
        try:
            # Read sensor data
            soil_moisture = read_soil_moisture()
            temp_aht25, humidity_aht25 = read_aht25()
            pressure_bmp280, altitude_bmp280 = read_bmp280()

            # Prepare data
            data = {
                "device": DEVICE_ID,
                "soil_moisture": soil_moisture,
                "temperature_aht25": temp_aht25,
                "humidity_aht25": humidity_aht25,
                "pressure_bmp280": pressure_bmp280,
                "altitude_bmp280": altitude_bmp280,
            }

            # Send to Flask server
            send_data_to_flask(data)
            sleep(1)  # Send data every second
        except Exception as e:
            print("Error:", e)

# Run the main function
if __name__ == "__main__":
    main()