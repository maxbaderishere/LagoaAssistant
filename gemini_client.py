from google import genai
from db import ChatRequests
from config import cfg

class Client:

    def generate(self, prompt: str, history: list[ChatRequests]) -> str:
        client = genai.Client(api_key=cfg.gemini_api_key)   
        contents = []
        for item in history:
            contents.append({"role": "user", "parts": [{"text": item.promt}]})
            contents.append({"role": "model", "parts": [{"text": item.response}]})
        contents.append({"role": "user", "parts": [{"text": prompt}]})

        response = client.models.generate_content(
            model="gemini-3.6-flash", contents=contents
        )
        return response.text
if __name__ == "__main__":
    test_client = Client()
    print(test_client.generate("скажи имя и фамилию основателя гугл"))