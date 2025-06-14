import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')

# Print the API key
print(f'OpenAI API Key: {api_key}') 