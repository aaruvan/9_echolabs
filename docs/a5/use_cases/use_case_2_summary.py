import requests

API_URL = "https://YOURDOMAIN/api/public/conversations/"

response = requests.get(API_URL, timeout=10)
response.raise_for_status()
data = response.json()

top_user = max(data, key=lambda row: row["total"], default=None)
if top_user:
    print("Top user:", top_user["user"])
    print("Conversation count:", top_user["total"])
else:
    print("No data returned.")
