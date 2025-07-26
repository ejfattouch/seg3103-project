import requests
import os
import json
import random
import string
from copy import deepcopy

test_dir = "test_inputs/"
url = "http://localhost:3000/login"

# Mutation helpers
def mutate_json(obj):
    mutated = deepcopy(obj)

    # Mutation 1: Drop a random key
    if random.random() < 0.3:
        if mutated:
            key_to_remove = random.choice(list(mutated.keys()))
            mutated.pop(key_to_remove, None)

    # Mutation 2: Rename a key
    if random.random() < 0.3:
        keys = list(mutated.keys())
        if keys:
            key = random.choice(keys)
            mutated["_" + key] = mutated.pop(key)

    # Mutation 3: Mess with value type
    for k in list(mutated.keys()):
        if random.random() < 0.3:
            mutated[k] = random.choice([None, 1234, ["array"], {"nested": True}])

    # Mutation 4: Add an unexpected key
    if random.random() < 0.3:
        mutated["unexpected_field"] = ''.join(random.choices(string.ascii_letters, k=5))

    return mutated

# Fuzzing loop
for filename in os.listdir(test_dir):
    filepath = os.path.join(test_dir, filename)

    with open(filepath, 'r') as f:
        lines = f.readlines()

        for i, line in enumerate(lines):
            try:
                original = json.loads(line.strip())
                mutated = mutate_json(original)

                response = requests.post(url, json=mutated)
                print(f"{filename}:{i} [{response.status_code}] {mutated}")
            except json.JSONDecodeError:
                print(f"{filename}:{i} ❌ Invalid JSON")
            except Exception as e:
                print(f"{filename}:{i} ⚠️ Error: {e}")
