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
* **Price Sensitivity:** Analyzes how customer demand shifts when you change your prices.
* **Revenue Simulation:** Use the **Slider** to manually test different pricing scenarios and see predicted sales impact.
* **Auto-Optimization:** Use the **Optimization Button** to instantly find the price point that maximizes your total revenue.
* **Return Analysis:** Monitors if deep discounting is causing an increase in product returns.
""")

# Key Metrics Display
if 'current_price' in df.columns:
    total_revenue = df['current_price'].sum()
    m1, m2 = st.columns(2)
    m1.metric("Current Total Revenue", f"${total_revenue:,.2f}")
    m2.metric("Data Records Analyzed", f"{len(df):,}")

# --- 5. SIMULATION & OPTIMIZATION LOGIC ---
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
    
    # THE OPTIMIZATION BUTTON
    if st.button("SHOW OPTIMIZED PRICE"):
        st.session_state.price_slider = optimal_p

    st.caption(f"""
    **INSTANT OPTIMIZATION:** * This automatically sets the slider to the exact price point where your volume and profit are perfectly balanced.
    * **Revenue Maximization:** The formula identifies the peak of your revenue curve based on current market sensitivity.
    * **Manual Exploration:** Alternatively, use the slider to test specific strategic discounts or seasonal price hikes.
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
        return_risk = "HIGH"
        risk_msg = "Deep discounts historically increase returns due to impulse buying."

with col_sim2:
    # EXECUTIVE IMPACT SUMMARY
    diff_symbol = "+" if revenue_delta >= 0 else ""
    is_optimized = "STATUS: OPTIMIZED" if abs(price_change - optimal_p) < 1 else "STATUS: SUB-OPTIMAL"

    st.markdown(f"""
    **EXECUTIVE IMPACT SUMMARY**
    * **Target Price Change:** `{price_change}%`
    * **Predicted Volume Shift:** `{ (demand_impact * 100):.1f}%`
    * **New Projected Total:** `${new_revenue:,.2f} ({diff_symbol}${revenue_delta:,.2f} vs current)`
    * **Return Risk Level:** `{return_risk}` ({risk_msg})
    * **{is_optimized}**
    """)
    st.markdown("---")

    # Revenue Curve Visualization
    sim_prices = np.linspace(-50, 50, 50)
    sim_revs = [total_revenue * (1 + p/100) * (1 + (p * elasticity / 100)) for p in sim_prices]
    
    fig_curve = px.line(x=sim_prices, y=sim_revs, 
                        labels={'x': 'Price Change %', 'y': 'Revenue ($)'}, 
                        title="REVENUE OPTIMIZATION CURVE")
    
    # Visual Indicators on Graph
    fig_curve.add_vline(x=price_change, line_dash="dash", line_color="red", annotation_text="Selection")
    fig_curve.add_vline(x=optimal_p, line_dash="dot", line_color="green", annotation_text="Peak")
    st.plotly_chart(fig_curve, use_container_width=True)

# --- 6. RETURN LOGISTICS ANALYSIS ---
st.markdown("---")
st.markdown("### **RETURN LOGISTICS ANALYSIS**")

st.markdown("""
**ANALYSIS OVERVIEW:**
* **Net Revenue Tracking:** Monitors the 'Return-to-Sale' ratio to ensure high volume doesn't lead to high loss.
* **Quality Benchmarking:** Identifies if specific discount thresholds trigger a spike in quality-related returns.
* **Category Insights:** Highlights which product groups are most susceptible to impulse-buy returns during sales.
* **Profit Protection:** Helps set 'Price Floors' to prevent discounting so deep that return costs outweigh the sales gain.
""")

if 'is_returned' in df.columns:
    return_rate = (df['is_returned'].sum() / len(df)) * 100
    st.info(f"Current Dashboard Insight: Overall return rate is {return_rate:.1f}%. "
            "Categories with higher markdowns typically show more returns related to quality perception.")

    fig_box = px.box(df, x='category', y='markdown_percentage', color='is_returned',
                     title="HOW MARKDOWNS IMPACT RETURNS BY CATEGORY",
                     labels={'markdown_percentage': 'Markdown %', 'category': 'Product Group'})
    
    st.plotly_chart(fig_box, use_container_width=True)

# --- 7. FOOTER ---
st.markdown("---")
st.caption("Developed by Bree Thomas | Data Business Analyst Portfolio | 2024")
