from Secrets.keys import google_api
import requests
import json

class Gemini:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={google_api}"
    headers = {
            'Content-Type': 'application/json'
        }

    def invoke(text: str):
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": text}
                    ]
                }
            ]
        }

        response = requests.post(Gemini.url, headers=Gemini.headers, data=json.dumps(data))

        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
        else:
            return {"error": f"Request failed with status code {response.status_code}", "details": response.text}

# Usage
response = Gemini.invoke("hello")
print(response)
