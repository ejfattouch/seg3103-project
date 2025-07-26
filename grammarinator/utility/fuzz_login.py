import requests
import os
import json

test_dir = "test_inputs/"

for filename in os.listdir(test_dir):
    filepath = os.path.join(test_dir, filename)

    with open(filepath, 'r') as f:
        lines = f.readlines()

        for i, line in enumerate(lines):
            try:
                data = json.loads(line.strip())
                response = requests.post("http://localhost:8080/login", json=data)
                print(f"{filename}:{i} ✅ {response.status_code}: {response.text[:80]}")
            except json.JSONDecodeError:
                print(f"{filename}:{i} ❌ Invalid JSON: {line.strip()}")
            except Exception as e:
                print(f"{filename}:{i} ⚠️ Request failed: {e}")
