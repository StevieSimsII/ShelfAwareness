import os
import csv
import openai
import re
from dotenv import load_dotenv
from datetime import date

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
api_key = os.getenv('OPENAI_API_KEY')
print(f'API Key loaded: {api_key is not None}')

# Set the API key
openai.api_key = api_key

def extract_price(text):
    # Find all price patterns in the text
    prices = re.findall(r'\$?\d+\.?\d*', text)
    if not prices:
        return None
    
    # Convert all found prices to float
    prices = [float(price.replace('$', '')) for price in prices]
    
    # If multiple prices found (range), return average
    if len(prices) > 1:
        return round(sum(prices) / len(prices), 2)
    return round(prices[0], 2)

def estimate_price(store_name, item_name):
    prompt = f"""What is the exact current price of {item_name} at {store_name} in Louisiana?
    Please respond with ONLY a single number representing the price in dollars.
    For example, if the price is $3.99, just respond with: 3.99
    Do not include any other text or explanation."""
    
    try:
        response = openai.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.3  # Lower temperature for more consistent responses
        )
        price_text = response.choices[0].message.content.strip()
        price = extract_price(price_text)
        print(f"Raw response for {store_name} - {item_name}: {price_text}")
        print(f"Extracted price: {price}")
        return price
    except Exception as e:
        print(f'Error estimating price: {e}')
        return None

# Read store and item data
stores = []
items = []

with open('data/stores.csv', 'r') as f:
    reader = csv.DictReader(f)
    stores = list(reader)

with open('data/items.csv', 'r') as f:
    reader = csv.DictReader(f)
    items = list(reader)

# Get today's date
today = date.today().isoformat()

# Estimate prices and write to CSV
with open('data/prices.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['store_id', 'item_id', 'price', 'date'])

    for store in stores:
        for item in items:
            price = estimate_price(store['store_name'], item['name'])
            if price:
                writer.writerow([store['store_id'], item['item_id'], price, today]) 