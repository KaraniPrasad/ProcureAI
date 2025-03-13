import streamlit as st

def render_sidebar() -> dict:
    """Render sidebar controls and return config"""
    

    with st.sidebar:
        st.header("⚙️ Aggregation Parameters")
        
        return {
            "moq": st.number_input(
                "Minimum Order Quantity (USD)",
                min_value=0,
                max_value=1000000,
                value=25000,
                help="Minimum total value threshold for consolidation"
            ),
            "consolidation_window_days": st.slider(
                "Maximum Delivery Window (days)",
                min_value=1,
                max_value=60,
                value=14,
                help="Maximum allowed spread between earliest and latest delivery dates"
            )
        }