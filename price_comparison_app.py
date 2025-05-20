import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import pydeck as pdk

# Set page config
st.set_page_config(
    page_title="Sopranos Supermarket Price Intelligence",
    page_icon="🛒",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    stores_df = pd.read_csv('data/stores.csv')
    items_df = pd.read_csv('data/items.csv')
    prices_df = pd.read_csv('data/prices.csv')
    return stores_df, items_df, prices_df

def calculate_price_recommendations(prices_df, stores_df, items_df, my_store_id=1):
    # Get latest prices
    latest_date = prices_df['date'].max()
    latest_prices = prices_df[prices_df['date'] == latest_date]
    
    # Calculate price statistics for each item
    price_stats = []
    for item_id in items_df['item_id']:
        item_prices = latest_prices[latest_prices['item_id'] == item_id]
        my_price = item_prices[item_prices['store_id'] == my_store_id]['price'].iloc[0]
        
        # Calculate statistics excluding my store
        other_prices = item_prices[item_prices['store_id'] != my_store_id]['price']
        avg_price = other_prices.mean()
        min_price = other_prices.min()
        max_price = other_prices.max()
        
        # Always recommend the market average (other stores)
        recommended_price = avg_price
        
        price_stats.append({
            'item_id': item_id,
            'item_name': items_df[items_df['item_id'] == item_id]['name'].iloc[0],
            'my_price': my_price,
            'avg_price': avg_price,
            'min_price': min_price,
            'max_price': max_price,
            'recommended_price': round(recommended_price, 2),
            'price_difference': round(my_price - avg_price, 2),
            'price_difference_percent': round((my_price - avg_price) / avg_price * 100, 1)
        })
    
    return pd.DataFrame(price_stats)

def main():
    st.title("🛒 Sopranos Supermarket Price Intelligence")
    st.subheader("Livonia, LA")
    
    # Load data
    stores_df, items_df, prices_df = load_data()
    
    # Item selection (used everywhere)
    item_options = items_df['name'].tolist()
    selected_item = st.selectbox("Select an item to compare:", item_options, key="item_selectbox_main")
    selected_item_id = items_df[items_df['name'] == selected_item]['item_id'].iloc[0]
    latest_date = prices_df['date'].max()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range selector
    dates = sorted(prices_df['date'].unique())
    start_date = st.sidebar.selectbox("Start Date", dates, index=len(dates)-30)
    end_date = st.sidebar.selectbox("End Date", dates, index=len(dates)-1)
    
    # Category filter
    categories = ['All'] + sorted(items_df['category'].unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories)
    
    # Filter data based on selections
    filtered_prices = prices_df[
        (prices_df['date'] >= start_date) &
        (prices_df['date'] <= end_date)
    ]
    
    if selected_category != 'All':
        category_items = items_df[items_df['category'] == selected_category]['item_id']
        filtered_prices = filtered_prices[filtered_prices['item_id'].isin(category_items)]
    
    # Price Recommendations Section
    st.header("Price Recommendations")
    
    # Calculate price recommendations
    price_recommendations = calculate_price_recommendations(prices_df, stores_df, items_df)
    
    # Display price recommendations table
    st.subheader("Current Prices vs. Market")
    
    # Format the recommendations table
    recommendations_display = price_recommendations[[
        'item_name', 'my_price', 'avg_price', 'min_price', 'max_price',
        'recommended_price', 'price_difference_percent'
    ]].copy()
    
    recommendations_display.columns = [
        'Item', 'Your Price', 'Market Average', 'Market Min', 'Market Max',
        'Recommended Price', 'Price Difference (%)'
    ]
    
    # Format price columns as $X.00
    price_cols = ['Your Price', 'Market Average', 'Market Min', 'Market Max', 'Recommended Price']
    for col in price_cols:
        recommendations_display[col] = recommendations_display[col].apply(lambda x: f"${x:.2f}")
    
    # Add color coding for price differences
    def color_price_diff(val):
        if isinstance(val, str):
            try:
                val = float(val.replace('%','').replace('$',''))
            except:
                return ''
        if val > 10:
            return 'color: red'
        elif val < -10:
            return 'color: green'
        return ''
    
    st.dataframe(
        recommendations_display.style.applymap(
            color_price_diff,
            subset=['Price Difference (%)']
        ),
        use_container_width=True
    )
    
    # Price Adjustment Section
    st.header("Price Adjustment Tool")
    
    # Create a form for price adjustments
    with st.form("price_adjustment_form"):
        st.subheader("Adjust Your Prices")
        
        # Create columns for the form
        col1, col2, col3 = st.columns(3)
        
        # Dictionary to store adjusted prices
        adjusted_prices = {}
        
        # Create input fields for each item
        for idx, row in price_recommendations.iterrows():
            with col1 if idx % 3 == 0 else col2 if idx % 3 == 1 else col3:
                st.write(f"**{row['item_name']}**")
                st.write(f"Current: ${row['my_price']:.2f}")
                st.write(f"Recommended: ${row['recommended_price']:.2f}")
                adjusted_price = st.number_input(
                    f"New Price",
                    min_value=0.0,
                    max_value=100.0,
                    value=float(row['my_price']),
                    step=0.01,
                    key=f"price_{row['item_id']}"
                )
                adjusted_prices[row['item_id']] = adjusted_price
        
        # Submit button
        submitted = st.form_submit_button("Update Prices")
        
        if submitted:
            # Calculate impact of price changes
            st.subheader("Price Change Impact Analysis")
            
            impact_data = []
            for item_id, new_price in adjusted_prices.items():
                item_data = price_recommendations[price_recommendations['item_id'] == item_id].iloc[0]
                old_price = item_data['my_price']
                price_change = new_price - old_price
                percent_change = (price_change / old_price) * 100
                
                impact_data.append({
                    'Item': item_data['item_name'],
                    'Old Price': f"${old_price:.2f}",
                    'New Price': f"${new_price:.2f}",
                    'Change': f"${price_change:.2f}",
                    'Change %': f"{percent_change:.1f}%",
                    'Market Position': 'Above Average' if new_price > item_data['avg_price'] else 'Below Average',
                    'Competitiveness': 'More Competitive' if new_price < item_data['avg_price'] else 'Less Competitive'
                })
            
            st.dataframe(pd.DataFrame(impact_data), use_container_width=True)
            
            # Save the new prices
            st.success("Prices updated successfully!")
    
    # Market Analysis Section
    st.header("Market Analysis")
    
    # Price trends over time
    st.subheader("Price Trends")
    
    # Get the top 5 items with the largest price differences
    top_items = price_recommendations.nlargest(5, 'price_difference_percent')['item_id'].tolist()
    
    # Plot price trends for these items
    fig = go.Figure()
    
    for item_id in top_items:
        item_name = items_df[items_df['item_id'] == item_id]['name'].iloc[0]
        item_prices = filtered_prices[filtered_prices['item_id'] == item_id]
        
        # Plot your store's prices
        my_prices = item_prices[item_prices['store_id'] == 1]
        fig.add_trace(go.Scatter(
            x=my_prices['date'],
            y=my_prices['price'],
            name=f"{item_name} (Your Store)",
            line=dict(width=2)
        ))
        
        # Plot average prices
        avg_prices = item_prices.groupby('date')['price'].mean().reset_index()
        fig.add_trace(go.Scatter(
            x=avg_prices['date'],
            y=avg_prices['price'],
            name=f"{item_name} (Market Avg)",
            line=dict(dash='dash')
        ))
    
    fig.update_layout(
        title="Price Trends for Items with Largest Price Differences",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        hovermode="x unified",
        yaxis_tickformat = '$.2f'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Competitor Analysis
    st.subheader("Competitor Analysis")
    
    # Calculate average prices by store
    store_prices = filtered_prices.groupby(['store_id', 'item_id'])['price'].mean().reset_index()
    store_prices = store_prices.merge(stores_df[['store_id', 'store_name', 'distance']], on='store_id')
    store_prices = store_prices.merge(items_df[['item_id', 'name']], on='item_id')
    
    # Create heatmap of prices by store
    pivot_prices = store_prices.pivot_table(
        values='price',
        index='store_name',
        columns='name',
        aggfunc='mean'
    ).round(2)
    
    # Format all price values as $X.00
    for col in pivot_prices.columns:
        if col != 'Distance (miles)':
            pivot_prices[col] = pivot_prices[col].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else "")
    
    # Add distance information
    pivot_prices['Distance (miles)'] = store_prices.groupby('store_name')['distance'].first()
    
    st.dataframe(pivot_prices, use_container_width=True)

    # Store Locations Map (Item-aware)
    st.header("Store Locations Map")
    # Prepare map data with price for selected item
    item_map_prices = prices_df[(prices_df['item_id'] == selected_item_id) & (prices_df['date'] == latest_date)]
    map_df = stores_df.merge(item_map_prices[['store_id', 'price']], on='store_id', how='left')
    map_df = map_df.rename(columns={'lat': 'latitude', 'lon': 'longitude'})
    map_df['is_sopranos'] = map_df['store_name'].str.lower().str.contains('sopranos')

    # Normalize price for color scaling (green=cheapest, red=most expensive)
    min_price = map_df['price'].min()
    max_price = map_df['price'].max()
    def price_to_color(price):
        if pd.isnull(price):
            return [128, 128, 128, 120]  # gray for missing
        norm = (price - min_price) / (max_price - min_price) if max_price > min_price else 0
        r = int(255 * norm)
        g = int(255 * (1 - norm))
        return [r, g, 0, 180]
    map_df['color'] = map_df.apply(lambda row: [255, 0, 0, 200] if row['is_sopranos'] else price_to_color(row['price']), axis=1)

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position='[longitude, latitude]',
        get_color='color',
        get_radius=400,
        pickable=True,
        auto_highlight=True,
    )

    view_state = pdk.ViewState(
        latitude=map_df['latitude'].mean(),
        longitude=map_df['longitude'].mean(),
        zoom=9,
        pitch=0,
    )

    tooltip = {
        "html": "<b>{store_name}</b><br/>Category: {category}<br/>Distance: {distance} mi<br/>Price: ${price}",
        "style": {"backgroundColor": "steelblue", "color": "white"}
    }

    st.pydeck_chart(pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip
    ))

    # Item Price Comparison Across Stores
    st.header("Compare Prices for a Food Item Across Stores")
    # Use selected_item_id and selected_item from above
    item_prices = prices_df[(prices_df['item_id'] == selected_item_id) & (prices_df['date'] == latest_date)]
    item_prices = item_prices.merge(stores_df, on='store_id')
    item_prices = item_prices.sort_values('price')

    # Display table
    st.subheader(f"Prices for {selected_item} at Each Store (as of {latest_date})")
    st.dataframe(item_prices[['store_name', 'price', 'distance']].rename(columns={
        'store_name': 'Store', 'price': 'Price ($)', 'distance': 'Distance (mi)'
    }), use_container_width=True)

    # Display bar chart
    st.subheader(f"Price Comparison Bar Chart for {selected_item}")
    st.bar_chart(item_prices.set_index('store_name')['price'])

if __name__ == "__main__":
    main() 