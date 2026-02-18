from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")

if not HF_TOKEN:
    print("No token found")
    exit(1)

client = InferenceClient(token=HF_TOKEN)
MODEL = "google/gemma-2-2b-it"

try:
    response = client.text_generation(
        "What is 2+2?",
        model=MODEL,
        max_new_tokens=50
    )
    print("Response:", response)
except Exception as e:
    print("Error:", e)