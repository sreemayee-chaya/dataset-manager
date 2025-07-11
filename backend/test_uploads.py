import requests

url = "http://127.0.0.1:5000/upload"
file_path = "test.txt"

with open(file_path, "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)

print("Status code:", response.status_code)
print("Response:", response.text)
