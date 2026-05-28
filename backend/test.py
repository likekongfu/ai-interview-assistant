import requests

url = "http://127.0.0.1:8000/stream_generate_questions"

with requests.post(url, stream=True) as r:
    for line in r.iter_lines():
        if line:
            print("Received:", line.decode())