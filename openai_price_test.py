import os
import openai
import pandas as pd
import time
from dotenv import load_dotenv
from datetime import date

# Remove old output file if it exists
if os.path.exists("data/prices.csv"):
    os.remove("data/prices.csv")

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

# Load store and item info
stores_df = pd.read_csv("data/stores.csv")
items_df = pd.read_csv("data/items.csv")

# Map store and item names to IDs
store_map = {row['store_name']: row['store_id'] for _, row in stores_df.iterrows()}
item_map = {row['name']: row['item_id'] for _, row in items_df.iterrows()}

stores = [
    {"name": "Walmart"},
    {"name": "Super 1 Foods"},
    {"name": "Dollar General"},
    {"name": "Soprano's Supermarket"},
]
items = ["milk", "eggs", "bread"]

def get_price_from_openai(store, item):
    prompt = (
        f"What is the current price for {item} at {store['name']}? "
        "If you don't know, estimate based on typical prices in Louisiana."
    )
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.2,
        )
        answer = response.choices[0].message.content
        print(f"OpenAI response for {store['name']} - {item}: {answer}")
        import re
        match = re.search(r"\$[0-9]+(?:\.[0-9]{2})?", answer)
        if match:
            print(f"Extracted price: {match.group(0)}")
            return float(match.group(0).replace("$", ""))
        else:
            print("No price found in response.")
            return None
    except Exception as e:
        print(f"OpenAI API error for {store['name']} - {item}: {e}")
        return None

results = []
today = date.today().isoformat()
for store in stores:
    for item in items:
        price = get_price_from_openai(store, item)
        print(f"DEBUG: Store: {store['name']}, Item: {item}, Price: {price}")
        if price is not None and store["name"] in store_map and item in item_map:
            print(f"Writing row: {store['name']} ({store_map[store['name']]}) - {item} ({item_map[item]}) - {price}")
            results.append({
                "store_id": store_map[store["name"]],
                "item_id": item_map[item],
                "price": price,
                "date": today
            })
        else:
            print(f"Skipping: {store['name']} or {item} not found in map, or price is None")
        time.sleep(1)

df = pd.DataFrame(results, columns=["store_id", "item_id", "price", "date"])
df.to_csv("data/prices.csv", index=False)
print("Saved results to data/prices.csv") 