import requests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pandas as pd

# Sample item list
items = ["milk", "eggs", "bread"]

# Step 1: Get user location
def get_user_location():
    geolocator = Nominatim(user_agent="store_locator")
    location = geolocator.geocode("New Orleans, LA")  # replace with dynamic input
    return (location.latitude, location.longitude)

# Step 2: Get nearby grocery stores using Yelp or Google Places API
def get_nearby_stores(location, radius=50):
    # Placeholder: Replace with actual API call to Google Places or Yelp
    return [
        {"name": "Walmart", "lat": 29.9511, "lon": -90.0715, "url": "https://www.walmart.com/"},
        {"name": "Target", "lat": 29.9600, "lon": -90.0700, "url": "https://www.target.com/"},
        {"name": "Rouses", "lat": 29.9500, "lon": -90.0700, "url": "https://www.rouses.com/shop/"},
    ]

# Step 3: Scrape prices for specific items from each store (requires custom scraper per site)
def get_prices_from_walmart(item):
    search_url = f"https://www.walmart.com/search?q={item}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        price_span = soup.find("span", class_="price-characteristic")
        return f"${price_span.text}" if price_span else "N/A"
    except:
        return "Error"

def get_prices_from_rouses(item):
    search_url = f"https://www.rouses.com/shop/?s={item}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    try:
        # This selector may need to be updated based on Rouses' HTML
        price_tag = soup.find("span", class_="woocommerce-Price-amount")
        return price_tag.text.strip() if price_tag else "N/A"
    except:
        return "Error"

# Step 4: Loop through stores and items
def collect_prices():
    user_location = get_user_location()
    stores = get_nearby_stores(user_location)

    price_data = []
    for store in stores:
        store_location = (store["lat"], store["lon"])
        if geodesic(user_location, store_location).miles <= 50:
            for item in items:
                if "walmart" in store["url"]:
                    price = get_prices_from_walmart(item)
                elif "rouses" in store["url"]:
                    price = get_prices_from_rouses(item)
                else:
                    price = "TBD"
                price_data.append({
                    "Store": store["name"],
                    "Item": item,
                    "Price": price
                })

    return pd.DataFrame(price_data)

# Step 5: Save or display the result
df = collect_prices()
print(df)
df.to_csv("local_store_prices.csv", index=False)
