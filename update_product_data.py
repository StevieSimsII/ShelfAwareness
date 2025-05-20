import csv
import os
from datetime import datetime

# Define new product categories and items
new_products = [
    # Paper Goods (New Category)
    {"item_id": "ITEM_0101", "name": "Toilet Paper", "category": "Paper Goods", "brand": "Generic", "unit": "Pack", "description": "12-roll pack toilet paper"},
    {"item_id": "ITEM_0102", "name": "Paper Towels", "category": "Paper Goods", "brand": "Generic", "unit": "Pack", "description": "6-roll paper towels"},
    {"item_id": "ITEM_0103", "name": "Facial Tissues", "category": "Paper Goods", "brand": "Generic", "unit": "Box", "description": "160-count facial tissues"},
    {"item_id": "ITEM_0104", "name": "Paper Napkins", "category": "Paper Goods", "brand": "Generic", "unit": "Pack", "description": "250-count paper napkins"},
    
    # Cleaning Supplies (New Category)
    {"item_id": "ITEM_0201", "name": "Laundry Detergent", "category": "Cleaning Supplies", "brand": "Generic", "unit": "Bottle", "description": "100oz liquid detergent"},
    {"item_id": "ITEM_0202", "name": "Dish Soap", "category": "Cleaning Supplies", "brand": "Generic", "unit": "Bottle", "description": "24oz dish washing liquid"},
    {"item_id": "ITEM_0203", "name": "All-purpose Cleaner", "category": "Cleaning Supplies", "brand": "Generic", "unit": "Bottle", "description": "32oz multi-surface cleaner"},
    {"item_id": "ITEM_0204", "name": "Bathroom Cleaner", "category": "Cleaning Supplies", "brand": "Generic", "unit": "Bottle", "description": "32oz bathroom cleaner"},
    
    # Personal Care (New Category)
    {"item_id": "ITEM_0301", "name": "Shampoo", "category": "Personal Care", "brand": "Generic", "unit": "Bottle", "description": "12oz shampoo"},
    {"item_id": "ITEM_0302", "name": "Body Wash", "category": "Personal Care", "brand": "Generic", "unit": "Bottle", "description": "16oz body wash"},
    {"item_id": "ITEM_0303", "name": "Toothpaste", "category": "Personal Care", "brand": "Generic", "unit": "Tube", "description": "6oz toothpaste"},
    {"item_id": "ITEM_0304", "name": "Deodorant", "category": "Personal Care", "brand": "Generic", "unit": "Stick", "description": "2.6oz deodorant"},
    
    # Prepared Foods (New Category)
    {"item_id": "ITEM_0401", "name": "Rotisserie Chicken", "category": "Prepared Foods", "brand": "Generic", "unit": "Each", "description": "Whole rotisserie chicken"},
    {"item_id": "ITEM_0402", "name": "Prepared Salad", "category": "Prepared Foods", "brand": "Generic", "unit": "Container", "description": "12oz caesar salad"},
    {"item_id": "ITEM_0403", "name": "Deli Sandwich", "category": "Prepared Foods", "brand": "Generic", "unit": "Each", "description": "Turkey sandwich"},
    {"item_id": "ITEM_0404", "name": "Ready Meal", "category": "Prepared Foods", "brand": "Generic", "unit": "Container", "description": "16oz pasta meal"},
    
    # Bakery (New Category)
    {"item_id": "ITEM_0501", "name": "Fresh Baked Bread", "category": "Bakery", "brand": "Generic", "unit": "Loaf", "description": "Fresh baked sourdough bread"},
    {"item_id": "ITEM_0502", "name": "Cake", "category": "Bakery", "brand": "Generic", "unit": "Each", "description": "8-inch chocolate cake"},
    {"item_id": "ITEM_0503", "name": "Fresh Cookies", "category": "Bakery", "brand": "Generic", "unit": "Dozen", "description": "Chocolate chip cookies"},
    {"item_id": "ITEM_0504", "name": "Pastries", "category": "Bakery", "brand": "Generic", "unit": "Each", "description": "Assorted pastries"},
    
    # Health & Wellness (New Category)
    {"item_id": "ITEM_0601", "name": "Multivitamin", "category": "Health & Wellness", "brand": "Generic", "unit": "Bottle", "description": "100-count multivitamins"},
    {"item_id": "ITEM_0602", "name": "Pain Reliever", "category": "Health & Wellness", "brand": "Generic", "unit": "Bottle", "description": "100-count acetaminophen"},
    {"item_id": "ITEM_0603", "name": "Cold Medicine", "category": "Health & Wellness", "brand": "Generic", "unit": "Box", "description": "24-count cold relief tablets"},
    {"item_id": "ITEM_0604", "name": "First Aid Kit", "category": "Health & Wellness", "brand": "Generic", "unit": "Kit", "description": "30-piece first aid kit"},
    
    # Specialty Items (Expansion)
    {"item_id": "ITEM_0701", "name": "Organic Apples", "category": "Specialty Items", "brand": "Organic", "unit": "Pound", "description": "Organic gala apples"},
    {"item_id": "ITEM_0702", "name": "Gluten-free Bread", "category": "Specialty Items", "brand": "Gluten-Free", "unit": "Loaf", "description": "Gluten-free sandwich bread"},
    {"item_id": "ITEM_0703", "name": "Plant-based Milk", "category": "Specialty Items", "brand": "Plant-Based", "unit": "Half-Gallon", "description": "Oat milk"},
    {"item_id": "ITEM_0704", "name": "Plant-based Burger", "category": "Specialty Items", "brand": "Plant-Based", "unit": "Pack", "description": "4-pack plant-based burger patties"}
]

def update_items_file():
    """Add new products to the items.csv file"""
    items_file = os.path.join("data", "items.csv")
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Read existing items
    existing_items = []
    try:
        with open(items_file, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_items.append(row)
    except FileNotFoundError:
        # If file doesn't exist, create it with headers
        existing_items = []
    
    # Add new products if they don't already exist
    existing_ids = [item.get('item_id') for item in existing_items]
    added_count = 0
    
    for product in new_products:
        if product['item_id'] not in existing_ids:
            product['last_updated'] = today
            existing_items.append(product)
            added_count += 1
    
    # Write back all items
    with open(items_file, 'w', newline='') as csvfile:
        fieldnames = ['item_id', 'name', 'category', 'brand', 'unit', 'description', 'last_updated']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for item in existing_items:
            writer.writerow(item)
    
    print(f"Added {added_count} new products to {items_file}")

def update_price_comparison_script():
    """Update the product list in price_comparison.py"""
    script_file = "price_comparison.py"
    with open(script_file, 'r') as file:
        content = file.read()
    
    # Find the items list section
    items_list_start = content.find("self.items = [")
    if items_list_start == -1:
        print("Could not find items list in price_comparison.py")
        return
    
    items_list_end = content.find("]", items_list_start)
    if items_list_end == -1:
        print("Could not find end of items list in price_comparison.py")
        return
    
    # Extract the current items list
    current_items = content[items_list_start:items_list_end+1]
    
    # Create new items list with added categories
    new_items_list = """self.items = [
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
            "ketchup", "mustard", "mayonnaise", "hot sauce",
            # Paper Goods
            "toilet paper", "paper towels", "facial tissues", "paper napkins",
            # Cleaning Supplies
            "laundry detergent", "dish soap", "all-purpose cleaner", "bathroom cleaner",
            # Personal Care
            "shampoo", "body wash", "toothpaste", "deodorant",
            # Prepared Foods
            "rotisserie chicken", "prepared salad", "deli sandwich", "ready meal",
            # Bakery
            "fresh baked bread", "cake", "fresh cookies", "pastries",
            # Health & Wellness
            "multivitamin", "pain reliever", "cold medicine", "first aid kit",
            # Specialty Items
            "organic apples", "gluten-free bread", "plant-based milk", "plant-based burger"
        ]"""
    
    # Replace the old items list with the new one
    updated_content = content.replace(current_items, new_items_list)
    
    # Write the updated content back to the file
    with open(script_file, 'w') as file:
        file.write(updated_content)
    
    print(f"Updated items list in {script_file}")

def main():
    """Main function to update product data"""
    print("Updating product data for ShelfAwareness...")
    
    # Update items.csv with new products
    update_items_file()
    
    # Update price_comparison.py with new product categories
    update_price_comparison_script()
    
    print("Product data update complete!")
    print("Run price_comparison.py to collect data for the new products.")

if __name__ == "__main__":
    main()
