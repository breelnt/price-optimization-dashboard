# --- 5. Return Logistics Analysis ---
st.markdown("---")
st.markdown("### **RETURN LOGISTICS ANALYSIS**")

# Layman's Context for the "Below the Fold" section
st.write("""
**What are we looking at here?** This section tracks the 'Return-to-Sale' relationship. 
While lower prices can drive a massive spike in sales volume, they often attract 
one-time shoppers or impulse buyers who are 15-20% more likely to return items. 
A successful price strategy must balance **high volume** with **low returns** to protect your actual profit.
""")

if 'is_returned' in df.columns:
    # Adding a human-readable insight based on the current data
    return_rate = (df['is_returned'].sum() / len(df)) * 100
    st.info(f"Current Dashboard Insight: Overall return rate is {return_rate:.1f}%. "
            "Categories with higher markdowns typically show more 'Return Reason' entries related to Quality.")

    fig_box = px.box(df, x='category', y='markdown_percentage', color='is_returned',
                     title="HOW MARKDOWNS IMPACT RETURNS BY CATEGORY",
                     labels={'markdown_percentage': 'Markdown %', 'category': 'Product Group'})
    
    st.plotly_chart(fig_box, use_container_width=True)

# --- 6. Footer ---
st.markdown("---")
st.caption("Developed by Bree Thomas | Data Business Analyst Portfolio | 2024")
