from google import genai

from config import cfg

class Client():

    def generate(self, prompt: str):
        client = genai.Client(api_key=cfg.gemini_api_key)   
        response = client.models.generate_content(
            model = "gemini-3.6-flash", contents = prompt
        )
        return response.text

if __name__ == "__main__":
    test_client = Client()
    print(test_client.generate("скажи имя и фамилию основателя гугл"))