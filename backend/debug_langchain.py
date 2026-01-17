import os
import time
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Try gemini-pro first as it is most likely to be available
models_to_try = [
    "gemini-pro",
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest"
]

for model_name in models_to_try:
    print(f"\n--- Testing model: {model_name} ---")
    print(f"Testing Gemini with key ending in: ...{api_key[-5:]}")
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=0.7,
        max_retries=0, 
        google_api_key=api_key
    )

    try:
        print("Sending request...")
        resp = llm.invoke([HumanMessage(content="Hello")])
        print("SUCCESS!")
        print(resp.content)
        break # Stop if one works
    except Exception as e:
        print(f"FAILED: {e}")
