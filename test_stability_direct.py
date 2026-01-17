import os
import sys
from dotenv import load_dotenv

# Ensure we can import from backend
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Load env from backend/.env
load_dotenv("backend/.env")

# Check key presence
key = os.getenv("STABILITY_API_KEY")
print(f"Testing Stability Key: {key[:5]}...{key[-5:] if key else 'None'}")

if not key:
    print("ERROR: STABILITY_API_KEY is missing.")
    sys.exit(1)

# Import the logic (or copy it solely for testing to avoid other dep issues if any)
# I will copy the logic to isolate the test to just Stability API 
import requests
import base64

def test_stability_generation():
    endpoint = "https://api.stability.ai/v2beta/stable-image/generate/core"
    prompt = "A futuristic logo for an AI startup, minimal, blue and white"
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Accept": "image/*",
    }
    files = {
        "prompt": (None, prompt),
        "output_format": (None, "png"),
    }
    
    print("Sending request to Stability AI...")
    try:
        resp = requests.post(endpoint, headers=headers, files=files)
        if resp.status_code == 200:
            print("Success! Image generated.")
            # Verify base64 decode works
            # image_base64 = base64.b64encode(resp.content).decode("utf-8")
            # print("Image decoded successfully.")
        else:
            print(f"Error: {resp.status_code}")
            print(resp.text)
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_stability_generation()
