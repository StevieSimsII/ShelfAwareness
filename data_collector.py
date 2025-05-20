import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import requests

def get_nearby_stores(center_lat, center_lon, radius_miles=50):
    radius_meters = int(radius_miles * 1609.34)
    query = f"""
    [out:json][timeout:25];
    (
      node["shop"="supermarket"](around:{radius_meters},{center_lat},{center_lon});
      node["shop"="convenience"](around:{radius_meters},{center_lat},{center_lon});
      node["shop"="department_store"](around:{radius_meters},{center_lat},{center_lon});
      node["shop"="discount"](around:{radius_meters},{center_lat},{center_lon});
    );
    out body;
    >;
    out skel qt;
    """
    url = "https://overpass-api.de/api/interpreter"
    response = requests.get(url, params={'data': query})
    data = response.json()
    stores = []
    store_id = 1
    for element in data['elements']:
        tags = element.get('tags', {})
        name = tags.get('name', f"Store {store_id}")
        category = tags.get('shop', 'unknown')
        address = tags.get('addr:city', '')
        stores.append({
            'store_id': store_id,
            'store_name': name,
            'category': category,
            'lat': element['lat'],
            'lon': element['lon'],
            'address': address
        })
        store_id += 1
    return stores

def generate_sample_data():
    # Livonia, LA coordinates
    LIVONIA_LAT = 30.5594
    LIVONIA_LON = -91.5557
    
    # Get nearby stores
    stores = get_nearby_stores(LIVONIA_LAT, LIVONIA_LON)
    
    # Add distance from center to each store
    for store in stores:
        store['distance'] = round(geodesic(
            (LIVONIA_LAT, LIVONIA_LON),
            (store['lat'], store['lon'])
        ).miles, 2)
    
    # Create sample items with categories and margin targets
    items = [
        # Dairy & Eggs (15-25% margin)
        {'item_id': 1, 'name': 'Milk (1 gallon)', 'category': 'Dairy', 'target_margin': 0.15},
        {'item_id': 2, 'name': 'Eggs (dozen)', 'category': 'Dairy', 'target_margin': 0.15},
        {'item_id': 3, 'name': 'Butter (1lb)', 'category': 'Dairy', 'target_margin': 0.20},
        {'item_id': 4, 'name': 'Cheese (8oz)', 'category': 'Dairy', 'target_margin': 0.25},
        
        # Meat & Poultry (20-30% margin)
        {'item_id': 5, 'name': 'Chicken Breast (1lb)', 'category': 'Meat', 'target_margin': 0.20},
        {'item_id': 6, 'name': 'Ground Beef (1lb)', 'category': 'Meat', 'target_margin': 0.25},
        {'item_id': 7, 'name': 'Pork Chops (1lb)', 'category': 'Meat', 'target_margin': 0.25},
        {'item_id': 8, 'name': 'Bacon (12oz)', 'category': 'Meat', 'target_margin': 0.30},
        
        # Produce (25-35% margin)
        {'item_id': 9, 'name': 'Bananas (1lb)', 'category': 'Produce', 'target_margin': 0.25},
        {'item_id': 10, 'name': 'Apples (1lb)', 'category': 'Produce', 'target_margin': 0.30},
        {'item_id': 11, 'name': 'Tomatoes (1lb)', 'category': 'Produce', 'target_margin': 0.35},
        {'item_id': 12, 'name': 'Lettuce (head)', 'category': 'Produce', 'target_margin': 0.30},
        
        # Pantry (20-30% margin)
        {'item_id': 13, 'name': 'Rice (5lb bag)', 'category': 'Pantry', 'target_margin': 0.20},
        {'item_id': 14, 'name': 'Pasta (1lb)', 'category': 'Pantry', 'target_margin': 0.25},
        {'item_id': 15, 'name': 'Cereal (box)', 'category': 'Pantry', 'target_margin': 0.30},
        {'item_id': 16, 'name': 'Flour (5lb bag)', 'category': 'Pantry', 'target_margin': 0.20},
        
        # Beverages (25-40% margin)
        {'item_id': 17, 'name': 'Coffee (12oz)', 'category': 'Beverages', 'target_margin': 0.35},
        {'item_id': 18, 'name': 'Orange Juice (1/2 gal)', 'category': 'Beverages', 'target_margin': 0.30},
        {'item_id': 19, 'name': 'Soda (12-pack)', 'category': 'Beverages', 'target_margin': 0.25},
        
        # Bakery (40-60% margin)
        {'item_id': 20, 'name': 'Bread (loaf)', 'category': 'Bakery', 'target_margin': 0.40},
        {'item_id': 21, 'name': 'Cake (whole)', 'category': 'Bakery', 'target_margin': 0.50},
        {'item_id': 22, 'name': 'Cookies (dozen)', 'category': 'Bakery', 'target_margin': 0.45},
        
        # Prepared Foods (40-60% margin)
        {'item_id': 23, 'name': 'Rotisserie Chicken', 'category': 'Prepared Foods', 'target_margin': 0.45},
        {'item_id': 24, 'name': 'Deli Sandwich', 'category': 'Prepared Foods', 'target_margin': 0.50},
        {'item_id': 25, 'name': 'Ready Meal', 'category': 'Prepared Foods', 'target_margin': 0.55},
        
        # Paper Goods (15-25% margin)
        {'item_id': 26, 'name': 'Toilet Paper (12pk)', 'category': 'Paper Goods', 'target_margin': 0.15},
        {'item_id': 27, 'name': 'Paper Towels (8pk)', 'category': 'Paper Goods', 'target_margin': 0.20},
        
        # Cleaning Supplies (20-30% margin)
        {'item_id': 28, 'name': 'Laundry Detergent', 'category': 'Cleaning Supplies', 'target_margin': 0.25},
        {'item_id': 29, 'name': 'Dish Soap', 'category': 'Cleaning Supplies', 'target_margin': 0.30},
        
        # Personal Care (25-35% margin)
        {'item_id': 30, 'name': 'Shampoo', 'category': 'Personal Care', 'target_margin': 0.30},
        {'item_id': 31, 'name': 'Toothpaste', 'category': 'Personal Care', 'target_margin': 0.35},
        
        # Health & Wellness (30-50% margin)
        {'item_id': 32, 'name': 'Multivitamin', 'category': 'Health & Wellness', 'target_margin': 0.40},
        {'item_id': 33, 'name': 'Pain Reliever', 'category': 'Health & Wellness', 'target_margin': 0.35},
        
        # Specialty Items (35-50% margin)
        {'item_id': 34, 'name': 'Organic Apples (1lb)', 'category': 'Specialty Items', 'target_margin': 0.40},
        {'item_id': 35, 'name': 'Gluten-Free Bread', 'category': 'Specialty Items', 'target_margin': 0.45}
    ]
    
    # Store price multipliers (to create price variations between stores)
    store_multipliers = {
        'Sopranos Supermarket': 1.0,    # Base price (your store)
        'Walmart Supercenter': 0.9,     # 10% cheaper
        'Target': 1.0,                  # Average price
        'Rouses Market': 1.05,          # 5% more expensive
        'Winn-Dixie': 1.0,             # Average price
        'Dollar General': 0.85,         # 15% cheaper
        'Family Dollar': 0.85,          # 15% cheaper
        'ALDI': 0.8,                    # 20% cheaper
        'Publix': 1.05,                 # 5% more expensive
        'Safeway': 1.0,                 # Average price
        'Walmart Neighborhood Market': 0.9,  # 10% cheaper
        'Circle K': 1.2,                # 20% more expensive
        'CVS Pharmacy': 1.3,            # 30% more expensive
        'Walgreens': 1.3,               # 30% more expensive
        'Save-A-Lot': 0.85              # 15% cheaper
    }
    
    # Generate prices for the last 30 days
    prices = []
    base_prices = {
        'Milk (1 gallon)': 3.99,
        'Eggs (dozen)': 4.99,
        'Butter (1lb)': 4.49,
        'Cheese (8oz)': 3.99,
        'Chicken Breast (1lb)': 5.99,
        'Ground Beef (1lb)': 6.99,
        'Pork Chops (1lb)': 5.49,
        'Bacon (12oz)': 6.99,
        'Bananas (1lb)': 0.69,
        'Apples (1lb)': 1.99,
        'Tomatoes (1lb)': 2.49,
        'Lettuce (head)': 1.99,
        'Rice (5lb bag)': 8.99,
        'Pasta (1lb)': 1.49,
        'Cereal (box)': 4.49,
        'Flour (5lb bag)': 4.99,
        'Coffee (12oz)': 7.99,
        'Orange Juice (1/2 gal)': 3.99,
        'Soda (12-pack)': 5.99,
        'Bread (loaf)': 2.99,
        'Cake (whole)': 24.99,
        'Cookies (dozen)': 4.99,
        'Rotisserie Chicken': 7.99,
        'Deli Sandwich': 5.99,
        'Ready Meal': 8.99,
        'Toilet Paper (12pk)': 12.99,
        'Paper Towels (8pk)': 8.99,
        'Laundry Detergent': 9.99,
        'Dish Soap': 2.99,
        'Shampoo': 5.99,
        'Toothpaste': 3.99,
        'Multivitamin': 12.99,
        'Pain Reliever': 8.99,
        'Organic Apples (1lb)': 3.99,
        'Gluten-Free Bread': 5.99
    }
    
    # Generate prices for the last 30 days
    for day in range(30):
        current_date = datetime.now() - timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d')
        
        for store in stores:
            for item in items:
                # Get base price and apply store multiplier
                base_price = base_prices[item['name']]
                store_multiplier = store_multipliers.get(store['store_name'], 1.0)
                
                # Add some random variation (±5%)
                variation = np.random.uniform(0.95, 1.05)
                
                # Calculate final price
                price = round(base_price * store_multiplier * variation, 2)
                
                prices.append({
                    'date': date_str,
                    'store_id': store['store_id'],
                    'item_id': item['item_id'],
                    'price': price
                })
    
    # Create DataFrames
    stores_df = pd.DataFrame(stores)
    items_df = pd.DataFrame(items)
    prices_df = pd.DataFrame(prices)
    
    # Create data directory if it doesn't exist
    if not os.path.exists('data'):
        os.makedirs('data')
    
    # Save to CSV files
    stores_df.to_csv('data/stores.csv', index=False)
    items_df.to_csv('data/items.csv', index=False)
    prices_df.to_csv('data/prices.csv', index=False)
    
    print("Sample data generated and saved to CSV files:")
    print(f"- {len(stores_df)} stores within 50 miles of Livonia, LA")
    print(f"- {len(items_df)} items")
    print(f"- {len(prices_df)} price records")

if __name__ == "__main__":
    generate_sample_data() 