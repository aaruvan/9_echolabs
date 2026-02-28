import requests

API_URL = "https://YOURDOMAIN/api/public/conversations/"

response = requests.get(API_URL, timeout=10)
response.raise_for_status()
data = response.json()

print("Total users:", len(data))
print("Sample rows:", data[:3])
