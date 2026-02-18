from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv
import traceback

load_dotenv()
HF_TOKEN = os.getenv("HUGGINGFACE_API_KEY")

if not HF_TOKEN:
    print("No token found")
    exit(1)

print(f"Using token: {HF_TOKEN[:5]}...{HF_TOKEN[-5:]}")  # Show partial token for confirmation

client = InferenceClient(token=HF_TOKEN)
MODEL = "google/gemma-2-2b-it"

try:
    print(f"Calling model {MODEL}...")
    response = client.text_generation(
        "What is 2+2?",
        model=MODEL,
        max_new_tokens=50
    )
    print("Response:", response)
except Exception as e:
    print("="*50)
    print("ERROR OCCURRED:")
    traceback.print_exc()  # This prints the full traceback
    print("="*50)
