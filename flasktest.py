import requests

def test_flask_server():
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            print("Flask server is running successfully!")
            print("Response:", response.text[:100] + "...")
        else:
            print(f"Server returned status code: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print("Failed to connect to Flask server:", e)

if __name__ == "__main__":
    test_flask_server()