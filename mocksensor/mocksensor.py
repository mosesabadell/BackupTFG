import time
import json
import random
import argparse

def generate_random_temperature(sensor_data):
    sensor_data["timestamp"] = time.time()
    current_temp = sensor_data["temperature"]
    difference = random.uniform(0, 0.5)
    add_or_subtract = random.randint(0, 1)

    if add_or_subtract and current_temp < 35:
        sensor_data["temperature"] += difference
    elif current_temp > 10:
        sensor_data["temperature"] -= difference

def generate_random_nivell(sensor_data):
    sensor_data["nivell"] = random.randint(0, 100)

    if sensor_data["nivell"] > 30:
        sensor_data["HF"] = 1
    else:
        sensor_data["HF"] = 0

    if sensor_data["nivell"] > 70:
        sensor_data["LF"] = 1
    elif sensor_data["nivell"] < 30:
        sensor_data["LF"] = 0

def main(device_id):
    sensor_data = {
        "device_id": device_id,
        "client_id": "c03d5155",
        "sensor_type": "Temperature",
        "temperature": 25,
        "nivell": 36,
        "HF": 0,
        "LF": 0,
        "timestamp": time.time()
    }

    while True:
        generate_random_temperature(sensor_data)
        generate_random_nivell(sensor_data)
        output_file_path = f'/tmp/output_mock_sensor_{device_id}.json'
        with open(output_file_path, 'a') as output_file:
            output_file.write(f'{json.dumps(sensor_data)}\n')
        time.sleep(0.5)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Mock sensor data generator.')
    parser.add_argument('--device_id', type=str, required=True, help='Device ID of the sensor.')
    args = parser.parse_args()

    main(args.device_id)
