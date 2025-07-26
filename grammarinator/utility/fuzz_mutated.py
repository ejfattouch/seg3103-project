import requests
import os
import json

for file in os.listdir('mutated_inputs/'):
    with open(f'mutated_inputs/{file}') as f:
        try:
            data = json.loads(f.read())
            response = requests.post("http://localhost:3000/login", json=data)
            print(f"{file} ✅ {response.status_code} - {response.text[:80]}")
        except json.JSONDecodeError as e:
            print(f"{file} ❌ Invalid JSON:\n{f.read()}")
        except Exception as e:
            print(f"{file} ❌ Other error: {e}")
