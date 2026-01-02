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
        return pd.DataFrame({
            "category": ["Electronics", "Electronics", "Mobile"],
            "item": ["Laptop", "Tablet", "Phone"], 
            "current_price": [1200, 600, 800], 
            "markdown_percentage": [5, 10, 0], 
            "is_returned": [False, True, False]
        })
    elif file_source == "Grocery Data (Placeholder)":
        return pd.DataFrame({
            "category": ["Produce", "Produce", "Dairy"],
            "item": ["Apple", "Orange", "Milk"], 
            "current_price": [2, 3, 4], 
            "markdown_percentage": [0, 20, 0], 
            "is_returned": [False, False, False]
        })
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

st.markdown("Adjust the **Price Slider** to test different scenarios and view the impact on revenue in the summary below.")

st.markdown("""
* **Price Sensitivity:** Analyzes how customer demand shifts when you change your prices.
* **Revenue Simulation:** Manually test pricing scenarios to see predicted sales volume and revenue impact.
* **Revenue Maximization:** Identifies the mathematical peak where profit and volume are perfectly balanced.
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

elasticity = -1.6 
optimal_p = round(-50 * (1 + elasticity) / elasticity, 2)

# --- SESSION STATE FIX ---
# Initialize the slider value in session state so the button can change it
if 'current_slider_val' not in st.session_state:
    st.session_state.current_slider_val = 0.0

col_sim1, col_sim2 = st.columns([1, 2])

with col_sim1:
    st.markdown("**SIMULATION CONTROLS**")
    
    # THE SLIDER (Note: value is linked to session state)
    price_change = st.slider(
        "Target Price Adjustment (%)", 
        min_value=-50.0, 
        max_value=50.0, 
        step=0.5,
        value=st.session_state.current_slider_val
    )
    
    # Keep session state in sync with manual slides
    st.session_state.current_slider_val = price_change

    st.markdown("---")

    # THE OPTIMIZATION BUTTON
    if st.button("RUN REVENUE OPTIMIZATION"):
        # Update the session state value
        st.session_state.current_slider_val = optimal_p
        # Force a rerun to move the slider visually
        st.rerun()

    st.caption(f"""
    **STRATEGIC OPTIMIZATION:** Click the button above to automatically align the slider with the 
    recommended price point. This identifies the balance where price changes are offset by 
    volume shifts to reach the highest possible total revenue.
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
    st.markdown("**EXECUTIVE IMPACT SUMMARY**")
    
    direction = "increase" if demand_impact > 0 else "decrease"
    change_type = "extra" if revenue_delta >= 0 else "loss of"
    
    # DYNAMIC ONE-SENTENCE SUMMARY
    st.info(f"""
    **ONE-SENTENCE SUMMARY (Updates with slider):** By adjusting our price by **{price_change}%**, we expect sales volume to **{direction}** by **{abs(demand_impact * 100):.1f}%**, 
    resulting in a total revenue of **${new_revenue:,.2f}** (a **{change_type} ${abs(revenue_delta):,.2f}** vs. current).
    """)

    st.markdown(f"""
    * **Target Price Change:** `{price_change}%`
    * **Predicted Volume Shift:** `{ (demand_impact * 100):.1f}%`
    * **Return Risk Level:** `{return_risk}` ({risk_msg})
    """)
    st.markdown("---")

    # Revenue Curve Visualization
    sim_prices = np.linspace(-50, 50, 50)
    sim_revs = [total_revenue * (1 + p/100) * (1 + (p * elasticity / 100)) for p in sim_prices]
    
    fig_curve = px.line(x=sim_prices, y=sim_revs, 
                        labels={'x': 'Price Change %', 'y': 'Revenue ($)'}, 
                        title="REVENUE OPTIMIZATION CURVE")
    
    fig_curve.add_vline(x=price_change, line_dash="dash", line_color="red", annotation_text="Selection")
    fig_curve.add_vline(x=optimal_p, line_dash="dot", line_color="green", annotation_text="Peak")
    st.plotly_chart(fig_curve, use_container_width=True)

# --- 6. RETURN LOGISTICS ANALYSIS ---
st.markdown("---")
st.markdown("### **RETURN LOGISTICS ANALYSIS**")

st.markdown("""
**GRAPH INTERPRETATION:**
* **Objective:** Determine if deeper markdowns lead to more frequent returns by category.
* **Data Breakdown:** Comparing items that were **Returned (True)** vs. items that were **Kept (False)**.
* **What to look for:** If the 'True' boxes sit higher on the chart than the 'False' boxes, it shows that deep discounts are causing higher return rates for that specific product group.
""")

if 'is_returned' in df.columns and 'category' in df.columns:
    return_rate = (df['is_returned'].sum() / len(df)) * 100
    cat_returns = df.groupby('category')['is_returned'].mean().sort_values(ascending=False)
    top_cat = cat_returns.index[0]
    top_rate = cat_returns.values[0] * 100

    st.info(f"""
    **CURRENT DATA SUMMARY:** Our overall rate of return across all categories is **{return_rate:.1f}%**. 
    The highest return rate is currently in the **{top_cat}** category, where items are returned at a rate of **{top_rate:.1f}%**. 
    *This summary refreshes automatically whenever new data is selected or uploaded.*
    """)

    fig_box = px.box(df, x='category', y='markdown_percentage', color='is_returned',
                     title="HOW MARKDOWNS IMPACT RETURNS BY CATEGORY",
                     labels={'markdown_percentage': 'Markdown %', 'category': 'Product Group'})
    
    st.plotly_chart(fig_box, use_container_width=True)

# --- 7. FOOTER ---
st.markdown("---")
st.caption("Developed by Bree Thomas | Data Business Analyst Portfolio | 2025")
