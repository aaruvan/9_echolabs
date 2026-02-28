import csv
import requests

API_URL = "https://YOURDOMAIN/api/public/conversations/"
OUTPUT_FILE = "public_api_export.csv"

response = requests.get(API_URL, timeout=10)
response.raise_for_status()
data = response.json()

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["user", "total"])
    writer.writeheader()
    writer.writerows(data)

print("Wrote CSV:", OUTPUT_FILE)
