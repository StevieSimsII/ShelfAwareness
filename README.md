# ShelfAwareness - Grocery Analytics & Price Comparison

A comprehensive toolkit for grocery store analytics and price comparison. This project helps you find nearby grocery stores, compare prices across multiple retailers, and provides insights to improve grocery retail operations.

## Features

- **Price Comparison**: Finds grocery stores within a 50-mile radius and compares prices for 50+ common grocery items
- **Data Analytics**: Tools and documentation for implementing advanced grocery retail analytics
- **Real-time Price Data**: Scrapes real prices from major retailers.
- **Reporting**: Generates CSV reports with detailed price comparisons
- **Visualization**: Creates interactive data visualizations
- **Location Intelligence**: Includes store distances and geographic analysis

## Project Components

- **[`price_comparison.py`](price_comparison.py)**: Core script that finds stores and collects price data
- **[`price_comparison_app.py`](price_comparison_app.py)**: Streamlit web app for interactive exploration
- **[`data_collector.py`](data_collector.py)**: Tool for collecting and aggregating price data
- **[`grocery_analytics_improvement_ideas.md`](grocery_analytics_improvement_ideas.md)**: Comprehensive ideas for improving grocery analytics
- **[`store_api_comparison.md`](store_api_comparison.md)**: Evaluation of different store APIs for data collection

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

### Data Files
- **`stores.csv`**: Information about nearby grocery stores
- **`price_comparison_report.csv`**: Detailed price comparison data
- **`data/items.csv`**: Master list of grocery items
- **`data/prices.csv`**: Historical price data
- **`data/stores.csv`**: Detailed store information

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

## Analytics Documentation

This project includes several markdown files documenting analytics approaches:

### [`grocery_analytics_improvement_ideas.md`](grocery_analytics_improvement_ideas.md)
Comprehensive collection of innovative analytics ideas tailored for grocery retailers, including:

- **Data Collection**: Real-time POS tracking, loyalty data analysis, foot traffic sensors
- **Data Analysis**: Predictive modeling, basket analysis, shrinkage analytics
- **Advanced Techniques**: ML models, NLP analysis, anomaly detection
- **Geo & Market Intelligence**: Price mapping, regional trends, demographic analysis
- **Operational Efficiency**: Shelf space optimization, predictive inventory modeling
- **Customer Experience**: Sentiment analysis, movement heatmaps, personalization
- **And more**: Omnichannel integration, sustainability insights, pricing optimization

### [`store_api_comparison.md`](store_api_comparison.md)
Evaluation of different APIs for collecting store and pricing data.

## Note

The script uses web scraping to get real prices from:
- Walmart
- Target

For other stores, it uses simulated price data. To add more stores:
1. Implement additional scraping methods in the `GroceryPriceComparer` class
2. Add the store name pattern matching in the `get_prices` method

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.