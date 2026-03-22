import os

from dotenv import load_dotenv
from google import genai


def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("Missing API key")
        raise SystemExit(1)

    client = genai.Client(api_key=api_key)
    print(f"Checking Gemini models for key prefix: {api_key[:5]}...")

    candidates = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-pro",
        "gemini-pro",
        "gemini-3-flash-preview",
    ]

    for model_name in candidates:
        print(f"Trying model: {model_name}")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents="Hello, are you working?",
            )
            print(f"Success with model: {model_name}")
            print(f"Response: {response.text}")
            break
        except Exception as exc:
            if "404" in str(exc):
                print("Not found (404)")
            else:
                print(f"Other error: {exc}")


if __name__ == "__main__":
    main()
