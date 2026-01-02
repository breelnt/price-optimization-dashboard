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
* **How to use:** Adjust the **Price Slider** to test scenarios, then check the **Executive Summary** to see how that change impacts your bottom line.
* **Price Sensitivity:** Analyzes how customer demand shifts when you change your prices.
* **Revenue Simulation:** Manually test pricing scenarios to see predicted sales volume and revenue impact.
* **Revenue Maximization:** Uses a quadratic formula ($Price \\times Volume$) to identify the mathematical peak where profit and volume are perfectly balanced.
* **Return Analysis:** Monitors if deep discounting is accidentally driving up your return rates.
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
    
    # THE SLIDER
    price_change = st.slider(
        "Target Price Adjustment (%)", 
        min_value=-50.0, 
        max_value=50.0, 
        step=0.5,
        key="price_slider"
    )

    st.markdown("---")

    # THE OPTIMIZATION BUTTON
    if st.button("RUN REVENUE OPTIMIZATION"):
        st.session_state.price_slider = optimal_p

    st.caption(f"""
    **STRATEGIC OPTIMIZATION:** Click the button above to instantly align the slider with the **{optimal_p}%** price point. 
    This identifies the equilibrium where price changes are perfectly balanced against potential volume loss, 
    resulting in maximum total revenue.
    """)
    
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

    st.markdown(f"""
    **EXECUTIVE IMPACT SUMMARY**
    * **Target Price Change:** `{price_change}%`
    * **Predicted Volume Shift:** `{ (demand_impact * 100):.1f}%`
    * **New Projected Total:** `${new_revenue:,.2f} ({diff_symbol}${revenue_delta:,.2f} vs current)`
    * **Return Risk Level:** `{return_risk}` ({risk_msg})
    """)

    # DYNAMIC BOTTOM LINE SUMMARY
    # We use st.info to make this stand out as the key takeaway
    direction = "increase" if demand_impact > 0 else "decrease"
    change_type = "extra" if revenue_delta >= 0 else "loss of"
    
    st.info(f"**The Bottom Line:** By adjusting our price by **{price_change}%**, we expect sales volume to **{direction}** by **{abs(demand_impact * 100):.1f}%**. This results in an estimated total revenue of **${new_revenue:,.2f}**, which is a **{change_type} ${abs(revenue_delta):,.2f}** compared to today.")

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
**GRAPH INTERPRETATION:**
* **Objective:** Determine if deeper markdowns lead to more frequent returns.
* **Data Breakdown:** Comparing items that were **Returned (True)** vs. items that were **Kept (False)**.
* **What to look for:** If the 'True' boxes sit higher on the chart than the 'False' boxes, it shows that deep discounts are causing higher return rates for that category.
""")

if 'is_returned' in df.columns:
    return_rate = (df['is_returned'].sum() / len(df)) * 100
    st.info(f"**LIVE DATA INSIGHT:** Currently, **{return_rate:.1f}%** of all items in this dataset were returned. "
            "This percentage updates automatically if you switch datasets or upload new files.")

    fig_box = px.box(df, x='category', y='markdown_percentage', color='is_returned',
                     title="HOW MARKDOWNS IMPACT RETURNS BY CATEGORY",
                     labels={'markdown_percentage': 'Markdown %', 'category': 'Product Group'})
    
    st.plotly_chart(fig_box, use_container_width=True)

# --- 7. FOOTER ---
st.markdown("---")
st.caption("Developed by Bree Thomas | Data Business Analyst Portfolio | 2025")
