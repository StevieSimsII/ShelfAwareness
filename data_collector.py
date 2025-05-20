import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

def get_nearby_stores(center_lat, center_lon, radius_miles=50):
    # List of stores in Louisiana with their coordinates
    stores_data = [
        {'store_id': 1, 'store_name': 'Sopranos Supermarket', 'category': 'supermarket', 
         'lat': 30.5594, 'lon': -91.5557, 'address': 'Livonia, LA'},
        {'store_id': 2, 'store_name': 'Walmart Supercenter', 'category': 'supermarket',
         'lat': 30.4515, 'lon': -91.1874, 'address': 'Baton Rouge, LA'},
        {'store_id': 3, 'store_name': 'Target', 'category': 'department_store',
         'lat': 30.4507, 'lon': -91.1545, 'address': 'Baton Rouge, LA'},
        {'store_id': 4, 'store_name': 'Rouses Market', 'category': 'supermarket',
         'lat': 30.4521, 'lon': -91.1874, 'address': 'Baton Rouge, LA'},
        {'store_id': 5, 'store_name': 'Winn-Dixie', 'category': 'supermarket',
         'lat': 30.4515, 'lon': -91.1874, 'address': 'Baton Rouge, LA'},
        {'store_id': 6, 'store_name': 'Dollar General', 'category': 'discount',
         'lat': 30.5594, 'lon': -91.5557, 'address': 'Livonia, LA'},
        {'store_id': 7, 'store_name': 'Family Dollar', 'category': 'discount',
         'lat': 30.5594, 'lon': -91.5557, 'address': 'Livonia, LA'},
        {'store_id': 8, 'store_name': 'ALDI', 'category': 'discount',
         'lat': 30.4515, 'lon': -91.1874, 'address': 'Baton Rouge, LA'},
        {'store_id': 9, 'store_name': 'Publix', 'category': 'supermarket',
         'lat': 30.4515, 'lon': -91.1874, 'address': 'Baton Rouge, LA'},
        {'store_id': 10, 'store_name': 'Safeway', 'category': 'supermarket',
         'lat': 30.4515, 'lon': -91.1874, 'address': 'Baton Rouge, LA'},
        {'store_id': 11, 'store_name': 'Walmart Neighborhood Market', 'category': 'supermarket',
         'lat': 30.4515, 'lon': -91.1874, 'address': 'Baton Rouge, LA'},
        {'store_id': 12, 'store_name': 'Circle K', 'category': 'convenience',
         'lat': 30.5594, 'lon': -91.5557, 'address': 'Livonia, LA'},
        {'store_id': 13, 'store_name': 'CVS Pharmacy', 'category': 'pharmacy',
         'lat': 30.4515, 'lon': -91.1874, 'address': 'Baton Rouge, LA'},
        {'store_id': 14, 'store_name': 'Walgreens', 'category': 'pharmacy',
         'lat': 30.4515, 'lon': -91.1874, 'address': 'Baton Rouge, LA'},
        {'store_id': 15, 'store_name': 'Save-A-Lot', 'category': 'discount',
         'lat': 30.4515, 'lon': -91.1874, 'address': 'Baton Rouge, LA'}
    ]
    
    # Filter stores within radius
    nearby_stores = []
    for store in stores_data:
        distance = geodesic(
            (center_lat, center_lon),
            (store['lat'], store['lon'])
        ).miles
        if distance <= radius_miles:
            store['distance'] = round(distance, 1)
            nearby_stores.append(store)
    
    return nearby_stores

def generate_sample_data():
    # Livonia, LA coordinates
    LIVONIA_LAT = 30.5594
    LIVONIA_LON = -91.5557
    
    # Get nearby stores
    stores = get_nearby_stores(LIVONIA_LAT, LIVONIA_LON)
    
    # Create sample items with categories
    items = [
        {'item_id': 1, 'name': 'Milk (1 gallon)', 'category': 'Dairy'},
        {'item_id': 2, 'name': 'Eggs (dozen)', 'category': 'Dairy'},
        {'item_id': 3, 'name': 'Bread (loaf)', 'category': 'Bakery'},
        {'item_id': 4, 'name': 'Chicken Breast (1lb)', 'category': 'Meat'},
        {'item_id': 5, 'name': 'Ground Beef (1lb)', 'category': 'Meat'},
        {'item_id': 6, 'name': 'Bananas (1lb)', 'category': 'Produce'},
        {'item_id': 7, 'name': 'Apples (1lb)', 'category': 'Produce'},
        {'item_id': 8, 'name': 'Rice (5lb bag)', 'category': 'Pantry'},
        {'item_id': 9, 'name': 'Pasta (1lb)', 'category': 'Pantry'},
        {'item_id': 10, 'name': 'Cereal (box)', 'category': 'Breakfast'}
    ]
    
    # Generate prices for the last 30 days
    prices = []
    base_prices = {
        'Milk (1 gallon)': 3.99,
        'Eggs (dozen)': 4.99,
        'Bread (loaf)': 2.99,
        'Chicken Breast (1lb)': 5.99,
        'Ground Beef (1lb)': 6.99,
        'Bananas (1lb)': 0.69,
        'Apples (1lb)': 1.99,
        'Rice (5lb bag)': 8.99,
        'Pasta (1lb)': 1.49,
        'Cereal (box)': 4.49
    }
    
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
    for day in range(30):
        current_date = datetime.now() - timedelta(days=day)
        date_str = current_date.strftime('%Y-%m-%d')
        
        for store in stores:
            for item in items:
                # Get base price and apply store multiplier
                base_price = base_prices[item['name']]
                store_multiplier = store_multipliers[store['store_name']]
                
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