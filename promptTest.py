import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Set the API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)
# Function to test the secret key
def test_openai_api():
    try:
        # Test with a simple API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello! Can you confirm you're working?"}
            ]
        )
        # Print the model's response
        print("OpenAI API is working!")
        print("Response:", response.choices[0].message.content)
    except openai.AuthenticationError:
        print("Authentication failed: Invalid API key.")
    except openai.OpenAIError as e:
        print(f"An OpenAI API error occurred: {e}")

# Run the test
test_openai_api()
