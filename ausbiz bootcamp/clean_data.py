import json

with open("your_file.json", "r") as f:
    data = json.load(f)

print("First job record:", data[0])
