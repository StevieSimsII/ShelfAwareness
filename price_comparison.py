import os
import requests
from datetime import datetime
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import logging
from typing import List, Dict, Any
import json
import csv

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class GroceryPriceComparer:
    def __init__(self, zip_code: str, radius_miles: int = 50):
        self.zip_code = zip_code
        self.radius_miles = radius_miles
        self.geolocator = Nominatim(user_agent="grocery_price_comparer")
        
        # Store types to search for in OpenStreetMap
        self.store_types = [
            'supermarket',
            'convenience',
            'wholesale',
            'department_store'
        ]
        
        # Store categories for better organization
        self.store_categories = {
            'supermarket': ['walmart', 'target', 'kroger', 'safeway', 'albertsons', 'publix', 'whole foods', 'trader joe\'s'],
            'wholesale': ['costco', 'sam\'s club', 'bj\'s'],
            'discount': ['dollar general', 'family dollar', 'dollar tree'],
            'convenience': ['7-eleven', 'circle k', 'cvs', 'walgreens'],
            'specialty': ['whole foods', 'trader joe\'s', 'sprouts', 'aldi', 'lidl']
        }
        
        # Expanded grocery items list
        self.items = [
            # Dairy & Eggs
            "milk", "eggs", "butter", "cheese", "yogurt", "sour cream", "heavy cream",
            # Meat & Seafood
            "chicken breast", "ground beef", "pork chops", "bacon", "salmon", "shrimp",
            # Produce
            "bananas", "apples", "oranges", "potatoes", "onions", "tomatoes", "lettuce",
            "carrots", "broccoli", "spinach", "avocado",
            # Pantry
            "bread", "rice", "pasta", "cereal", "flour", "sugar", "salt", "pepper",
            "olive oil", "vegetable oil", "peanut butter", "jam",
            # Beverages
            "coffee", "tea", "orange juice", "apple juice", "water",
            # Snacks
            "chips", "crackers", "cookies", "granola bars",
            # Frozen
            "frozen pizza", "ice cream", "frozen vegetables",
            # Canned Goods
            "canned tuna", "canned beans", "canned soup",
            # Condiments
            "ketchup", "mustard", "mayonnaise", "hot sauce"
        ]
        
        self.stores = []
        self.price_data = []

    def get_location_from_zip(self) -> tuple:
        """Convert city/state to latitude/longitude using Nominatim"""
        try:
            # Use Baton Rouge, Louisiana, USA for geocoding
            location = self.geolocator.geocode("Baton Rouge, Louisiana, USA")
            if location:
                return (location.latitude, location.longitude)
            else:
                raise Exception(f"Could not find location for Baton Rouge, Louisiana, USA")
        except Exception as e:
            logger.error(f"Error getting location: {str(e)}")
            raise

    def categorize_store(self, store_name: str) -> str:
        """Categorize store based on its name"""
        store_name_lower = store_name.lower()
        for category, keywords in self.store_categories.items():
            if any(keyword in store_name_lower for keyword in keywords):
                return category
        return 'other'

    def find_nearby_stores(self) -> List[Dict[str, Any]]:
        """Find all types of stores that sell groceries within specified radius using Overpass API"""
        try:
            lat, lng = self.get_location_from_zip()
            all_stores = []
            
            # Convert radius from miles to meters
            radius_meters = self.radius_miles * 1609.34
            
            # Build Overpass QL query
            query = f"""
            [out:json][timeout:25];
            (
              node["shop"="supermarket"](around:{radius_meters},{lat},{lng});
              node["shop"="convenience"](around:{radius_meters},{lat},{lng});
              node["shop"="wholesale"](around:{radius_meters},{lat},{lng});
              node["shop"="department_store"](around:{radius_meters},{lat},{lng});
              node["amenity"="marketplace"](around:{radius_meters},{lat},{lng});
              node["shop"="general"](around:{radius_meters},{lat},{lng});
              node["shop"="variety_store"](around:{radius_meters},{lat},{lng});
              node["shop"="mall"](around:{radius_meters},{lat},{lng});
            );
            out body;
            >;
            out skel qt;
            """
            
            # Make request to Overpass API
            response = requests.get(
                "https://overpass-api.de/api/interpreter",
                params={'data': query}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                for element in data.get('elements', []):
                    if element.get('type') == 'node':
                        # Calculate distance
                        distance = geodesic(
                            (lat, lng),
                            (element['lat'], element['lon'])
                        ).miles
                        
                        # Get store name from tags with better fallbacks
                        tags = element.get('tags', {})
                        
                        # Try different name variations
                        name = (
                            tags.get('name') or  # Try standard name
                            tags.get('name:en') or  # Try English name
                            tags.get('brand') or  # Try brand name
                            tags.get('operator') or  # Try operator name
                            f"{tags.get('shop', 'Store')} at {tags.get('addr:street', 'this location')}"  # Fallback with shop type and street
                        )
                        
                        # Clean up the name
                        if name:
                            # Remove common prefixes/suffixes
                            name = name.replace('Supermercado', '').replace('Tienda', '').strip()
                            # Remove extra whitespace
                            name = ' '.join(name.split())
                            # If name is too generic, add more context
                            if name.lower() in ['store', 'shop', 'market']:
                                name = f"{name.title()} on {tags.get('addr:street', 'this street')}"
                        
                        # Create store entry
                        store = {
                            'name': name or 'Unknown Store',
                            'address': tags.get('addr:street', 'N/A'),
                            'location': {
                                'lat': element['lat'],
                                'lng': element['lon']
                            },
                            'distance': distance,
                            'category': self.categorize_store(name or ''),
                            'type': tags.get('shop', 'other'),
                            'brand': tags.get('brand', 'N/A'),
                            'operator': tags.get('operator', 'N/A')
                        }
                        all_stores.append(store)
                
                # Remove duplicates
                unique_stores = []
                seen_names = set()
                for store in sorted(all_stores, key=lambda x: x['distance']):
                    # Use a combination of name and location to identify unique stores
                    store_id = f"{store['name']}_{store['location']['lat']}_{store['location']['lng']}"
                    if store_id not in seen_names:
                        seen_names.add(store_id)
                        unique_stores.append(store)
                
                return unique_stores
            else:
                raise Exception(f"Overpass API request failed with status code {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error finding nearby stores: {str(e)}")
            raise

    def get_prices(self) -> List[Dict[str, Any]]:
        """Get simulated prices for items at each store"""
        prices = []
        for store in self.stores:
            for item in self.items:
                # Simulate price data
                price = round(2 + (hash(f"{store['name']}{item}") % 100) / 100, 2)
                prices.append({
                    'item': item,
                    'store': store['name'],
                    'price': price,
                    'distance': round(store['distance'], 1),
                    'date': datetime.now().strftime('%Y-%m-%d')
                })
        return prices

    def save_to_csv(self, data: List[Dict[str, Any]], filename: str):
        """Save data to CSV file in a more readable format"""
        if not data:
            return
        
        if filename == 'price_comparison_report.csv':
            # Create a pivot table format for price comparison
            stores = sorted(set(item['store'] for item in data))
            items = sorted(set(item['item'] for item in data))
            
            # Create headers
            headers = ['Item'] + stores
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                # Write each item's prices across all stores
                for item in items:
                    row = [item]
                    for store in stores:
                        # Find price for this item at this store
                        price_data = next(
                            (p for p in data if p['item'] == item and p['store'] == store),
                            None
                        )
                        price = f"${price_data['price']:.2f}" if price_data else "N/A"
                        row.append(price)
                    writer.writerow(row)
                
                # Add a summary row with average prices
                writer.writerow(['Average Price'] + [
                    f"${sum(p['price'] for p in data if p['store'] == store) / len(items):.2f}"
                    for store in stores
                ])
                
                # Add a row with store distances
                writer.writerow(['Distance (miles)'] + [
                    f"{next((p['distance'] for p in data if p['store'] == store), 'N/A'):.1f}"
                    for store in stores
                ])
        else:
            # Original format for other files
            fieldnames = data[0].keys()
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)

    def generate_report(self) -> List[Dict[str, Any]]:
        """Generate a comprehensive store and price comparison report"""
        try:
            # Find all stores
            self.stores = self.find_nearby_stores()
            logger.info(f"Found {len(self.stores)} stores in the area")
            
            # Save stores to CSV
            self.save_to_csv(self.stores, 'stores.csv')
            logger.info("Store information saved to stores.csv")
            
            # Get prices
            self.price_data = self.get_prices()
            
            # Save prices to CSV
            self.save_to_csv(self.price_data, 'price_comparison_report.csv')
            logger.info("Price comparison report saved to price_comparison_report.csv")
            
            return self.price_data
        except Exception as e:
            logger.error(f"Error generating report: {str(e)}")
            raise

    def analyze_price_patterns(self, price_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze price patterns across stores and items"""
        analysis = {
            'cheapest_stores': {},
            'most_expensive_stores': {},
            'price_variation': {},
            'best_value_stores': {},
            'item_categories': {
                'dairy': ['milk', 'eggs', 'butter', 'cheese', 'yogurt', 'sour cream', 'heavy cream'],
                'meat': ['chicken breast', 'ground beef', 'pork chops', 'bacon', 'salmon', 'shrimp'],
                'produce': ['bananas', 'apples', 'oranges', 'potatoes', 'onions', 'tomatoes', 'lettuce', 
                           'carrots', 'broccoli', 'spinach', 'avocado'],
                'pantry': ['bread', 'rice', 'pasta', 'cereal', 'flour', 'sugar', 'salt', 'pepper',
                          'olive oil', 'vegetable oil', 'peanut butter', 'jam'],
                'beverages': ['coffee', 'tea', 'orange juice', 'apple juice', 'water'],
                'snacks': ['chips', 'crackers', 'cookies', 'granola bars'],
                'frozen': ['frozen pizza', 'ice cream', 'frozen vegetables'],
                'canned': ['canned tuna', 'canned beans', 'canned soup'],
                'condiments': ['ketchup', 'mustard', 'mayonnaise', 'hot sauce']
            }
        }
        
        # Calculate store averages and price variations
        store_prices = {}
        item_prices = {}
        
        for price in price_data:
            store = price['store']
            item = price['item']
            price_value = price['price']
            
            # Store prices
            if store not in store_prices:
                store_prices[store] = []
            store_prices[store].append(price_value)
            
            # Item prices
            if item not in item_prices:
                item_prices[item] = []
            item_prices[item].append(price_value)
        
        # Calculate store statistics
        for store, prices in store_prices.items():
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            price_range = max_price - min_price
            
            analysis['cheapest_stores'][store] = avg_price
            analysis['price_variation'][store] = price_range
            
            # Calculate value score (lower is better)
            # Consider both average price and distance
            store_data = next(s for s in self.stores if s['name'] == store)
            value_score = avg_price * (1 + (store_data['distance'] / 50))  # Distance penalty
            analysis['best_value_stores'][store] = value_score
        
        # Sort stores by price and value
        analysis['cheapest_stores'] = dict(sorted(analysis['cheapest_stores'].items(), key=lambda x: x[1]))
        analysis['most_expensive_stores'] = dict(sorted(analysis['cheapest_stores'].items(), key=lambda x: x[1], reverse=True))
        analysis['best_value_stores'] = dict(sorted(analysis['best_value_stores'].items(), key=lambda x: x[1]))
        
        # Calculate category averages
        category_averages = {}
        for category, items in analysis['item_categories'].items():
            category_prices = []
            for item in items:
                if item in item_prices:
                    category_prices.extend(item_prices[item])
            if category_prices:
                category_averages[category] = sum(category_prices) / len(category_prices)
        
        analysis['category_averages'] = dict(sorted(category_averages.items(), key=lambda x: x[1]))
        
        return analysis

def main():
    try:
        # This script is configured for Baton Rouge, LA
        print("\nGrocery Price Comparison for Baton Rouge, LA (within 50 miles)")
        # Initialize the comparer (zip_code argument is ignored)
        comparer = GroceryPriceComparer("")
        
        # Generate and display the report
        report = comparer.generate_report()
        
        # Analyze price patterns
        analysis = comparer.analyze_price_patterns(report)
        
        print("\nStore Summary:")
        print(f"Total stores found: {len(comparer.stores)}")
        print("\nStore categories:")
        for store in comparer.stores:
            print(f"- {store['name']} ({store['category']}, {store['distance']:.1f} miles)")
        
        print("\nPrice Analysis:")
        print("\nTop 5 Cheapest Stores (Average Price):")
        for store, price in list(analysis['cheapest_stores'].items())[:5]:
            print(f"- {store}: ${price:.2f}")
        
        print("\nTop 5 Most Expensive Stores (Average Price):")
        for store, price in list(analysis['most_expensive_stores'].items())[:5]:
            print(f"- {store}: ${price:.2f}")
        
        print("\nTop 5 Best Value Stores (Price + Distance):")
        for store, score in list(analysis['best_value_stores'].items())[:5]:
            print(f"- {store}: Value Score {score:.2f}")
        
        print("\nPrice Variation by Store (Highest to Lowest):")
        sorted_variation = dict(sorted(analysis['price_variation'].items(), key=lambda x: x[1], reverse=True))
        for store, variation in list(sorted_variation.items())[:5]:
            print(f"- {store}: ${variation:.2f} range")
        
        print("\nAverage Prices by Category:")
        for category, avg_price in analysis['category_averages'].items():
            print(f"- {category.title()}: ${avg_price:.2f}")
        
        print("\nPrice Comparison Report:")
        for item in comparer.items:
            print(f"\n{item.upper()}:")
            item_prices = [p for p in report if p['item'] == item]
            for price in sorted(item_prices, key=lambda x: x['price']):
                print(f"  {price['store']}: ${price['price']:.2f} ({price['distance']:.1f} miles)")
        
        print("\nReports have been saved as CSV files:")
        print("- stores.csv (Store information)")
        print("- price_comparison_report.csv (Price comparisons)")
        
    except Exception as e:
        logger.error(f"Error in main execution: {str(e)}")
        raise

if __name__ == "__main__":
    main() 