import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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
    # Force all IDs to string for reliable merging
    stores_df['store_id'] = stores_df['store_id'].astype(str)
    prices_df['store_id'] = prices_df['store_id'].astype(str)
    prices_df['item_id'] = prices_df['item_id'].astype(str)
    items_df['item_id'] = items_df['item_id'].astype(str)
    return stores_df, items_df, prices_df

def calculate_price_recommendations(prices_df, stores_df, items_df, my_store_id='1'):
    # Get latest prices
    latest_date = prices_df['date'].max()
    latest_prices = prices_df[prices_df['date'] == latest_date]
    
    # Calculate price statistics for each item
    price_stats = []
    for item_id in items_df['item_id']:
        item_prices = latest_prices[latest_prices['item_id'] == item_id]
        my_store_prices = item_prices[item_prices['store_id'] == my_store_id]['price']
        my_price = my_store_prices.iloc[0] if not my_store_prices.empty else np.nan
        
        # Calculate statistics excluding my store
        other_prices = item_prices[item_prices['store_id'] != my_store_id]['price']
        avg_price = other_prices.mean()
        min_price = other_prices.min()
        max_price = other_prices.max()
        
        # Get item details
        item_details = items_df[items_df['item_id'] == item_id].iloc[0]
        
        # Use default target margin of 20%
        target_margin = 0.20
        
        # Calculate current margin (assuming cost is 70% of market average)
        estimated_cost = avg_price * 0.7 if not np.isnan(avg_price) else np.nan
        current_margin = (my_price - estimated_cost) / my_price if not np.isnan(my_price) and not np.isnan(estimated_cost) else np.nan
        
        # Calculate margin gap
        margin_gap = current_margin - target_margin if not np.isnan(current_margin) else np.nan
        
        # Recommend price based on target margin
        recommended_price = estimated_cost / (1 - target_margin) if not np.isnan(estimated_cost) else np.nan
        
        price_stats.append({
            'item_id': item_id,
            'item_name': item_details['name'],
            'target_margin': target_margin,
            'current_margin': current_margin,
            'margin_gap': margin_gap,
            'my_price': my_price,
            'avg_price': avg_price,
            'min_price': min_price,
            'max_price': max_price,
            'recommended_price': round(recommended_price, 2) if not np.isnan(recommended_price) else np.nan,
            'price_difference': round(my_price - avg_price, 2) if not np.isnan(my_price) and not np.isnan(avg_price) else np.nan,
            'price_difference_percent': round((my_price - avg_price) / avg_price * 100, 1) if not np.isnan(my_price) and not np.isnan(avg_price) and avg_price != 0 else np.nan
        })
    
    return pd.DataFrame(price_stats)

def main():
    st.title("🛒 Sopranos Supermarket Price Intelligence")
    st.subheader("Livonia, LA")

    # Load data
    stores_df, items_df, prices_df = load_data()

    # Price Recommendations Section
    st.header("Price Recommendations")
    
    # Calculate price recommendations
    price_recommendations = calculate_price_recommendations(prices_df, stores_df, items_df)
    
    # Display price recommendations table
    st.subheader("Current Prices vs. Market")
    
    # Format the recommendations table
    recommendations_display = price_recommendations[[
        'item_name', 'my_price', 'avg_price', 'min_price', 'max_price',
        'recommended_price', 'price_difference_percent', 'current_margin', 'target_margin', 'margin_gap'
    ]].copy()
    
    recommendations_display.columns = [
        'Item', 'Your Price', 'Market Average', 'Market Min', 'Market Max',
        'Recommended Price', 'Price Difference (%)', 'Current Margin', 'Target Margin', 'Margin Gap'
    ]
    
    # Format price columns as $X.00
    price_cols = ['Your Price', 'Market Average', 'Market Min', 'Market Max', 'Recommended Price']
    for col in price_cols:
        recommendations_display[col] = recommendations_display[col].apply(lambda x: f"${x:.2f}")
    
    # Format margin columns as percentages
    margin_cols = ['Current Margin', 'Target Margin', 'Margin Gap']
    for col in margin_cols:
        recommendations_display[col] = recommendations_display[col].apply(lambda x: f"{x*100:.1f}%")
    
    # Add color coding for price differences and margin gaps
    def color_price_diff(val):
        try:
            v = float(str(val).replace('%','').replace('$',''))
        except:
            return ''
        if v > 10:
            return 'color: red'
        elif v < -10:
            return 'color: green'
        else:
            return ''

    def color_margin_gap(val):
        try:
            v = float(str(val).replace('%',''))
        except:
            return ''
        if v < -5:  # Margin is more than 5% below target
            return 'color: red'
        elif v > 5:  # Margin is more than 5% above target
            return 'color: green'
        else:
            return ''

    st.dataframe(
        recommendations_display.style
        .map(color_price_diff, subset=['Price Difference (%)'])
        .map(color_margin_gap, subset=['Margin Gap']),
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
    
    # --- Store Locations Table and Map ---
    st.header("Store Locations and Prices")
    item_options = items_df['name'].tolist()
    selected_item = st.selectbox("Choose a food item to display on the map:", item_options, key="item_selectbox_main")
    selected_item_id = items_df[items_df['name'] == selected_item]['item_id'].iloc[0]
    latest_date = prices_df['date'].max()

    # Prepare map data with price for selected item
    item_map_prices = prices_df[(prices_df['item_id'] == selected_item_id) & (prices_df['date'] == latest_date)]
    stores_df['store_id'] = stores_df['store_id'].astype(str)
    item_map_prices['store_id'] = item_map_prices['store_id'].astype(str)
    map_df = stores_df.merge(item_map_prices[['store_id', 'price']], on='store_id', how='left')
    map_df = map_df.rename(columns={'lat': 'latitude', 'lon': 'longitude'})
    map_df['price_str'] = map_df['price'].apply(lambda x: f"${x:.2f}" if pd.notnull(x) else "N/A")
    map_df['label'] = map_df.apply(lambda row: f"{row['store_name']}\n{row['price_str']}", axis=1)
    map_df['is_sopranos'] = map_df['store_name'].str.lower().str.contains('soprano')

    # Remove lat/lon from table
    st.subheader(f"Store Locations and Prices for {selected_item} (as of {latest_date})")
    display_df = map_df[['store_name', 'address', 'price_str']].copy()
    display_df.columns = ['Store Name', 'Address', 'Price']
    st.dataframe(display_df, use_container_width=True)

    if map_df[['latitude', 'longitude']].dropna().empty:
        st.warning('No store location data available for the map. Please check your stores.csv for lat/lon columns and values.')
    else:
        # Add slight jitter to overlapping points (optional, only if needed)
        jitter = 0.0005
        map_df['latitude_jitter'] = map_df['latitude'] + map_df.groupby(['latitude', 'longitude']).cumcount() * jitter
        map_df['longitude_jitter'] = map_df['longitude'] + map_df.groupby(['latitude', 'longitude']).cumcount() * jitter

        # IconLayer for Soprano's
        icon_data = {
            "url": "https://cdn-icons-png.flaticon.com/512/25/25694.png",  # white house PNG
            "width": 512,
            "height": 512,
            "anchorY": 512
        }
        map_df['icon_data'] = map_df['is_sopranos'].apply(lambda x: icon_data if x else None)

        icon_layer = pdk.Layer(
            "IconLayer",
            data=map_df[map_df['is_sopranos']],
            get_icon="icon_data",
            get_position='[longitude_jitter, latitude_jitter]',
            get_size=4,
            size_scale=10,
            pickable=True,
        )

        # ScatterplotLayer for other stores
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=map_df[~map_df['is_sopranos']],
            get_position='[longitude_jitter, latitude_jitter]',
            get_color=[0, 102, 204, 180],
            get_radius=400,
            pickable=True,
            auto_highlight=True,
        )

        # TextLayer for all stores
        text_layer = pdk.Layer(
            "TextLayer",
            data=map_df,
            get_position='[longitude_jitter, latitude_jitter]',
            get_text='label',
            get_size=16,
            get_color=[0, 0, 0, 255],
            get_angle=0,
            get_alignment_baseline="bottom",
        )

        view_state = pdk.ViewState(
            latitude=map_df['latitude'].mean() if not map_df.empty else 30.5594,
            longitude=map_df['longitude'].mean() if not map_df.empty else -91.5557,
            zoom=9,
            pitch=0,
        )

        tooltip = {
            "html": "<b>{store_name}</b><br/><b>Price: {price_str}</b>",
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }

        st.pydeck_chart(pdk.Deck(
            layers=[icon_layer, scatter_layer, text_layer],
            initial_view_state=view_state,
            tooltip=tooltip
        ), use_container_width=True, height=700)

if __name__ == "__main__":
    main() 