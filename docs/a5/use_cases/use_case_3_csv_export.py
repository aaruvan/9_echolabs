"""
A5 Use Case 3: Export public API data to CSV.
Production API: vanshiaaru.pythonanywhere.com (Team 9 – EchoLabs).
Run: python use_case_3_csv_export.py
Then capture a screenshot showing the script output and/or the generated CSV for submission.
"""
import csv
import requests

API_URL = "https://vanshiaaru.pythonanywhere.com/api/public/conversations/"
OUTPUT_FILE = "public_api_export.csv"

response = requests.get(API_URL, timeout=10)
response.raise_for_status()
data = response.json()

with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["user", "total"])
    writer.writeheader()
    writer.writerows(data)

print("Wrote CSV:", OUTPUT_FILE)
