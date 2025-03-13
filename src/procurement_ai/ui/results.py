import streamlit as st
import pandas as pd

def display_results(results):
    if results.get("errors"):
        st.error("## Processing Errors")
        for error in results["errors"]:
            st.error(f"- {error}")
    else:
        st.success("Analysis Complete!")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Recommendations")
            st.dataframe(
                pd.DataFrame(results["recommendations"]),
                use_container_width=True
            )
        
        with col2:
            st.subheader("Sourcing Events")
            for event in results["sourcing_events"]:
                with st.expander(event["unspsc_family"]):
                    st.json(event)