"""
A5 Use Case 2: Find top user by conversation count from public API.
Production API: vanshiaaru.pythonanywhere.com (Team 9 – EchoLabs).
Run: python use_case_2_summary.py
Then capture a screenshot of the terminal output for submission.
"""
import requests

API_URL = "https://vanshiaaru.pythonanywhere.com/api/public/conversations/"

response = requests.get(API_URL, timeout=10)
response.raise_for_status()
data = response.json()

top_user = max(data, key=lambda row: row["total"], default=None)
if top_user:
    print("Top user:", top_user["user"])
    print("Conversation count:", top_user["total"])
else:
    print("No data returned.")
