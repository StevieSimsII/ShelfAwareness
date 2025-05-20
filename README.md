# Grocery Price Comparison Tool

This Python script compares grocery prices across different stores within a specified radius of a given zip code.

## Features

- Finds grocery stores within a 50-mile radius of a specified zip code
- Compares prices for 50+ common grocery items across categories
- Real-time price scraping from major retailers (Walmart, Target)
- Generates a CSV report with price comparisons
- Creates interactive visualizations of price data
- Includes store distances and timestamps

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Install Chrome browser (required for web scraping)

3. Create a `.env` file in the project root directory and add your Google Places API key:
```
GOOGLE_PLACES_API_KEY=your_api_key_here
```

You can obtain a Google Places API key from the [Google Cloud Console](https://console.cloud.google.com/).

## Usage

Run the script with:
```bash
python price_comparison.py
```

The script will:
1. Find grocery stores near zip code 70760
2. Scrape real prices from store websites
3. Generate price comparisons for 50+ grocery items
4. Save the results to `price_comparison_report.csv`
5. Create interactive visualizations
6. Display the results in the console

## Output

### CSV Report
The script generates a CSV file with the following columns:
- Item Name
- Store Name
- Price
- Distance (in miles)
- Date

### Visualizations
The script creates three interactive HTML visualizations:
1. `price_distribution.html`: Box plots showing price distribution by store for top items
2. `average_prices.html`: Bar chart showing average prices by store
3. `price_vs_distance.html`: Scatter plot showing price vs distance relationship

## Grocery Items

The script compares prices for items across these categories:
- Dairy & Eggs
- Meat & Seafood
- Produce
- Pantry Items
- Beverages
- Snacks
- Frozen Foods
- Canned Goods
- Condiments

## Error Handling

The script includes comprehensive error handling and logging:
- Graceful fallback to simulated prices if web scraping fails
- Detailed logging of all operations
- Automatic cleanup of browser resources

## Note

The script uses web scraping to get real prices from:
- Walmart
- Target

For other stores, it uses simulated price data. To add more stores:
1. Implement additional scraping methods in the `GroceryPriceComparer` class
2. Add the store name pattern matching in the `get_prices` method 