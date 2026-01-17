import os
from dotenv import load_dotenv
from openai import OpenAI

# Load env variables explicitly
load_dotenv("backend/.env")

api_key = os.getenv("OPENAI_API_KEY")
print(f"Testing Key: {api_key[:10]}...{api_key[-5:]}")

client = OpenAI(api_key=api_key)

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print("Success! Response:", response.choices[0].message.content)
except Exception as e:
    print("\nXXX API ERROR XXX")
    print(e)
