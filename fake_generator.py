import random
import time
import requests

API_BASE = 'http://127.0.0.1:8000/api'
USERNAME = 'admin'
PASSWORD = 'Admin123!'

MACHINES = [
    {'id': 1, 'base_kw': 5.5},
    {'id': 2, 'base_kw': 7.8},
    {'id': 3, 'base_kw': 3.2},
    {'id': 4, 'base_kw': 9.1},
]


def generate_payload(machine):
    voltage = random.uniform(370, 410)
    current = random.uniform(9.0, 15.0)
    power_kw = max(0.5, machine['base_kw'] + random.uniform(-1.2, 1.8))
    energy_kwh = power_kw / 12
    return {
        'machine_id': machine['id'],
        'voltage': round(voltage, 2),
        'current': round(current, 2),
        'power_kw': round(power_kw, 2),
        'energy_kwh': round(energy_kwh, 3),
    }


def main():
    print('Starting fake EMS data generator...')
    while True:
        for machine in MACHINES:
            payload = generate_payload(machine)
            response = requests.post(
                f"{API_BASE}/energy/ingest/",
                json=payload,
                auth=(USERNAME, PASSWORD),
                timeout=5,
            )
            if response.status_code not in (200, 201):
                print('Failed:', response.status_code, response.text)
            else:
                print('Sent:', payload)
        time.sleep(5)


if __name__ == '__main__':
    main()
