# ShelfAwareness - Grocery Analytics & Price Comparison

A modern toolkit for grocery store analytics and price comparison. This project helps you find real nearby grocery stores (using OpenStreetMap), compare prices across multiple retailers, and provides actionable insights for your own store's pricing strategy.

## Features

- **Dynamic Store Data**: Finds grocery stores within a 50-mile radius of Livonia, LA (or any location) using OpenStreetMap (OSM) Overpass API
- **Price Comparison**: Compares prices for common grocery items across all detected stores
- **Price Recommendations**: Suggests optimal retail prices for your store based on market data
- **Interactive Web App**: Streamlit app for exploring, adjusting, and analyzing prices
- **Reporting**: Generates CSV reports with detailed price comparisons
- **Visualization**: Interactive data visualizations and competitor analysis

## Project Components

- **[`price_comparison_app.py`](price_comparison_app.py)**: Streamlit web app for interactive price comparison, recommendations, and market analysis
- **[`data_collector.py`](data_collector.py)**: Tool for collecting real store locations from OSM and generating simulated price data
- **`data/` directory**: Contains generated CSVs for stores, items, and prices

## Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. (Optional) If you want to generate new data, ensure you have an internet connection (for OSM API access).

## Usage

### 1. Generate Data (Local Development)
To fetch real store locations and generate new sample price data:
```bash
python data_collector.py
```
This will create/update:
- `data/stores.csv` (real stores from OSM)
- `data/items.csv` (sample grocery items)
- `data/prices.csv` (simulated prices for all stores/items)

### 2. Run the Streamlit App
To launch the interactive price comparison dashboard:
```bash
streamlit run price_comparison_app.py
```

### 3. Deploy to Streamlit Cloud
- Push your code and the `data/` directory to GitHub.
- On [Streamlit Cloud](https://streamlit.io/cloud):
  - Set the repository URL and main file as `price_comparison_app.py`.
  - The app will use the pre-generated CSVs for fast startup.

#### requirements.txt (for Streamlit Cloud)
```
streamlit==1.32.0
pandas>=2.0.0
plotly==5.19.0
numpy>=1.26.0
geopy
```

## Output

### Data Files
- **`data/stores.csv`**: Real store locations (from OSM)
- **`data/items.csv`**: Master list of grocery items
- **`data/prices.csv`**: Simulated price data for all stores/items

### Visualizations & Features
- Price recommendations for your store based on market averages
- Interactive price adjustment tool to simulate new pricing
- Price trends and competitor analysis
- All prices shown in $X.00 format

## How Store Data is Collected
- The app uses the OpenStreetMap Overpass API to fetch all supermarkets, convenience stores, department stores, and discount stores within a 50-mile radius of your chosen location.
- No store data is hardcoded; all locations are real and up-to-date.

## How Price Data is Generated
- Prices are simulated for all stores and items, with realistic variation by store type.
- You can adjust the simulation logic in `data_collector.py` as needed.

## Customization
- To change the center location, edit the coordinates in `data_collector.py`.
- To add more item categories or adjust price simulation, edit the items and pricing logic in `data_collector.py`.

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the app locally:
```bash
streamlit run price_comparison_app.py
```

## Deployment

This app is configured for deployment on Streamlit Cloud. To deploy:

1. Push your code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repository
4. Select `price_comparison_app.py` as the main file
5. Deploy

## Project Structure

- `price_comparison_app.py`: Main Streamlit application
- `data_collector.py`: Script for generating sample data
- `data/`: Directory containing CSV data files
  - `stores.csv`: Store information
  - `items.csv`: Product information
  - `prices.csv`: Price history

## Features

- Real-time price comparison
- Margin analysis
- Category-specific insights
- Interactive visualizations
- Price trend analysis
- Competitor mapping

## Requirements

See `requirements.txt` for full list of dependencies.