"""
A5 Use Case 1: Call public API and print summary.
Production API: vanshiaaru.pythonanywhere.com (Team 9 – EchoLabs).
Run: python use_case_1_requests.py
Then capture a screenshot of the terminal output for submission.
"""
import requests

API_URL = "https://vanshiaaru.pythonanywhere.com/api/public/conversations/"

response = requests.get(API_URL, timeout=10)
response.raise_for_status()
data = response.json()

print("Total users:", len(data))
print("Sample rows:", data[:3])
