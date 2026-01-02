import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- Page Config ---
st.set_page_config(page_title="Retail Price Optimizer", layout="wide")

# --- 1. Data Loading Logic ---
@st.cache_data
def load_data(file_source):
    # Logic to handle different sources
    if file_source == "Default: Fashion Boutique":
        return pd.read_csv("fashion_boutique_dataset.csv")
    elif file_source == "Tech Sales (Placeholder)":
        # Placeholder for future dataset
        return pd.DataFrame({"item": ["Laptop"], "current_price": [1000], "markdown_percentage": [0], "is_returned": [False]})
    elif file_source == "Grocery Data (Placeholder)":
        # Placeholder for future dataset
        return pd.DataFrame({"item": ["Apple"], "current_price": [1], "markdown_percentage": [0], "is_returned": [False]})
    else:
        return pd.read_csv(file_source)

# --- 2. Sidebar Layout Refinement ---
with st.sidebar:
    st.header("Data Selection")
    
    # Selection priority: Default/Dropdown first
    data_option = st.selectbox(
        "Choose Dataset to Analyze",
        ["Default: Fashion Boutique", "Tech Sales (Placeholder)", "Grocery Data (Placeholder)"]
    )
    
    st.info(f"Currently using: {data_option}")
    
    st.markdown("---")
    
    # Custom upload moved to bottom
    st.subheader("Upload Custom Data")
    uploaded_file = st.file_uploader("Drag and drop additional files here", type="csv")

# Load final data based on priority (Upload overrides dropdown)
if uploaded_file:
    df = load_data(uploaded_file)
else:
    df = load_data(data_option)

# Data Cleaning
if 'is_returned' in df.columns:
    df['is_returned'] = df['is_returned'].fillna(False)

# --- 3. Main Body: Headlines and Description ---
st.markdown("# REVENUE AND PRICE OPTIMIZATION STRATEGY")
st.markdown("---")

st.markdown("""
### How to use this dashboard
* **Understand Price Sensitivity:** This tool calculates how much your customers' buying habits change when you change your prices.
* **Simulate Revenue:** Use the sliders below to see a prediction of your total sales if you were to raise or lower prices today.
* **Analyze Returns:** Look at the 'Return Problem' section to see if your discounts are accidentally attracting low-quality sales that end up being returned.
* **Identify the 'Sweet Spot':** The Revenue Optimization Curve shows you the exact price point where you make the most money before customers start leaving.
""")

# --- 4. Key Metrics ---
if 'current_price' in df.columns:
    total_revenue = df['current_price'].sum()
    m1, m2 = st.columns(2)
    m1.metric("Current Total Revenue", f"${total_revenue:,.2f}")
    m2.metric("Data Records Analyzed", f"{len(df):,}")

# --- 5. Simulation Controls ---
st.markdown("## == PRICE ELASTICITY SIMULATOR ==")

col_sim1, col_sim2 = st.columns([1, 2])

with col_sim1:
    st.subheader("Simulation Controls")
    
    st.write("""
    **What happens when I move the slider?** Moving this slider simulates a store-wide price change. If you move it to the right (increase), 
    the system predicts how many customers will stop buying. If you move it to the left (discount), 
    it predicts how many new customers will be attracted by the lower price.
    """)
    
    price_change = st.slider("Target Price Adjustment (%)", -50, 50, 0)
    
    # Applied logic
    elasticity = -1.6
    demand_impact = (price_change * elasticity) / 100
    new_revenue = total_revenue * (1 + (price_change/100)) * (1 + demand_impact)
    revenue_delta = new_revenue - total_revenue

    st.metric("Projected Revenue Change", f"${revenue_delta:,.2f}", delta=f"{((new_revenue/total_revenue)-1)*100:.1f}%")

with col_sim2:
    # Visualization
    sim_prices = np.linspace(-0.5, 0.5, 20)
    sim_revs = [total_revenue * (1 + p) * (1 + (p * elasticity)) for p in sim_prices]
    fig_curve = px.line(x=sim_prices*100, y=sim_revs, 
                        labels={'x': 'Price Change %', 'y': 'Revenue ($)'}, 
                        title="The Revenue 'Sweet Spot'")
    fig_curve.add_vline(x=price_change, line_dash="dash", line_color="red")
    st.plotly_chart(fig_curve, use_container_width=True)

# --- 6. Returns ---
st.markdown("## == RETURN LOGISTICS ANALYSIS ==")
if 'is_returned' in df.columns:
    fig_box = px.box(df, x='category', y='markdown_percentage', color='is_returned',
                     title="Markdown Spread vs. Returns")
    st.plotly_chart(fig_box, use_container_width=True)
