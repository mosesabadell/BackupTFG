import time
import json
import random


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
    # Generar un nivell aleatori entre 0 i 100
    sensor_data["nivell"] = random.randint(0, 100)

    # Controlar el valor de HF
    if sensor_data["nivell"] > 30:
        sensor_data["HF"] = 1
    else:
        sensor_data["HF"] = 0

    # Controlar el valor de LF
    if sensor_data["nivell"] > 70:
        sensor_data["LF"] = 1
    elif sensor_data["nivell"] < 30:
        sensor_data["LF"] = 0


def main():
    sensor_data = {
        "device_id": "01MAC01",
        "client_id": "01SN01",
        "sensor_type": "DadesAltaveu",
        "temperature": 25,
        "nivell": 36,
        "HF": 0,  # Inicialització de HF
        "LF": 0,  # Inicialització de LF
        "timestamp": time.time()
    }

    while True:
        generate_random_temperature(sensor_data)  # Actualitzar temperatura
        generate_random_nivell(sensor_data)  # Actualitzar nivell, HF i LF
        with open('/tmp/output_mock_sensor.json', 'a') as output_file:
            output_file.write(f'{json.dumps(sensor_data)}\n')
        time.sleep(0.5)


if __name__ == '__main__':
    main()
