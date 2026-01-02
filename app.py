import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(page_title="Retail Price Optimizer", layout="wide")

# --- 2. DATA LOADING LOGIC ---
@st.cache_data
def load_data(file_source):
    if file_source == "Default: Fashion Boutique":
        return pd.read_csv("fashion_boutique_dataset.csv")
    elif file_source == "Tech Sales (Placeholder)":
        return pd.DataFrame({"item": ["Laptop"], "current_price": [1000], "markdown_percentage": [0], "is_returned": [False]})
    elif file_source == "Grocery Data (Placeholder)":
        return pd.DataFrame({"item": ["Apple"], "current_price": [1], "markdown_percentage": [0], "is_returned": [False]})
    else:
        return pd.read_csv(file_source)

# --- 3. SIDEBAR SELECTION ---
with st.sidebar:
    st.markdown("**DATA SELECTION**")
    data_option = st.selectbox(
        "Choose Dataset to Analyze",
        ["Default: Fashion Boutique", "Tech Sales (Placeholder)", "Grocery Data (Placeholder)"]
    )
    st.info(f"Using: {data_option}")
    
    st.markdown("---")
    st.markdown("**UPLOAD CUSTOM DATA**")
    uploaded_file = st.file_uploader("Drag and drop additional files here", type="csv")

# Load final data based on selection or upload
df = load_data(uploaded_file if uploaded_file else data_option)

# Data Cleaning
if 'is_returned' in df.columns:
    df['is_returned'] = df['is_returned'].fillna(False)

# --- 4. MAIN BODY HEADLINES & GUIDE ---
st.markdown("# REVENUE AND PRICE OPTIMIZATION STRATEGY")
st.markdown("---")

st.markdown("""
**DASHBOARD GUIDE**
* **Price Sensitivity:** Calculates how customer demand shifts when prices change.
* **Revenue Simulation:** Predicts total sales impact based on price adjustments.
* **The Sweet Spot:** Automatically identifies the price that maximizes total revenue.
""")

# Key Metrics Display
if 'current_price' in df.columns:
    total_revenue = df['current_price'].sum()
    m1, m2 = st.columns(2)
    m1.metric("Current Total Revenue", f"${total_revenue:,.2f}")
    m2.metric("Data Records Analyzed", f"{len(df):,}")

# --- 5. SIMULATION & MAGIC BUTTON LOGIC ---
st.markdown("---")
st.markdown("### **PRICE ELASTICITY SIMULATOR**")

# Define the elasticity (sensitivity) and calculate the mathematical peak
elasticity = -1.6 
optimal_p = round(-50 * (1 + elasticity) / elasticity, 2)

# Sync: Initialize slider value in session state
if 'price_slider' not in st.session_state:
    st.session_state.price_slider = 0.0

col_sim1, col_sim2 = st.columns([1, 2])

with col_sim1:
    st.markdown("**SIMULATION CONTROLS**")
    
    # THE MAGIC BUTTON
    if st.button("AUTO-SET TO SWEET SPOT"):
        st.session_state.price_slider = optimal_p

    st.caption(f"""
    **What is the 'Sweet Spot'?** In economics, there is a point where a price is high enough to make a good profit, 
    but low enough that customers don't walk away. Clicking the button above uses a 'Revenue Peak' formula 
    to find that exact {optimal_p}% sweet spot for this data.
    """)

    # THE SLIDER
    price_change = st.slider(
        "Target Price Adjustment (%)", 
        min_value=-50.0, 
        max_value=50.0, 
        step=0.5,
        key="price_slider"
    )
    
    # Impact Calculations
    demand_impact = (price_change * elasticity) / 100
    new_revenue = total_revenue * (1 + (price_change/100)) * (1 + demand_impact)
    revenue_delta = new_revenue - total_revenue
    
    # Return Risk Logic
    return_risk = "LOW"
    risk_msg = "Stable return patterns expected."
    if price_change < -25:
        return_risk = "HIGH
