import json
import random
import os

def mutate_json(data):
    if isinstance(data, dict):
        keys = list(data.keys())
        if keys:
            key = random.choice(keys)
            mutation_type = random.choice(["delete", "nullify", "duplicate"])
            if mutation_type == "delete":
                del data[key]
            elif mutation_type == "nullify":
                data[key] = None
            elif mutation_type == "duplicate":
                data[f"{key}_dup"] = data[key]
    return data

def apply_mutations(input_dir='./test_inputs', output_dir='mutated_inputs'):
    os.makedirs(output_dir, exist_ok=True)
    for filename in os.listdir(input_dir):
        print(f"Processing {filename}...")
        with open(os.path.join(input_dir, filename)) as f:
            try:
                data = json.load(f)
                mutated = mutate_json(data)
                with open(os.path.join(output_dir, filename), 'w') as out_f:
                    json.dump(mutated, out_f)
            except:
                print(f"Error processing {filename}, skipping...")
                continue

if __name__ == "__main__":
    apply_mutations()
    print("Mutated JSON files created in 'mutated_inputs' directory.")