import os
import logging
import streamlit as st
from dotenv import load_dotenv
from src.procurement_ai.graph.workflow import create_procurement_workflow
from src.procurement_ai.llms.setup import get_groq_llm
from src.procurement_ai.ui.sidebar import render_sidebar
from src.procurement_ai.ui.results import display_results
from src.procurement_ai.ui.upload import handle_file_upload
import pandas as pd
from src.procurement_ai.state.procurement_state import ProcurementState, ProcurementConfig

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def main():
    print ("main function called")
    #st.set_page_config(page_title="Demand Analyzer", layout="wide")
   
    
    st.set_page_config(page_title= "🤖 " + "Demand Analyzer", layout="wide")
    st.title("🚀 AI Procurement Workflow for Demand Aggregation")
    st.session_state.timeframe = ''
    st.session_state.IsFetchButtonClicked = False
    st.session_state.IsSDLC = False
        
    # Get config from sidebar
    config = render_sidebar()
    
    
    
    
    uploaded_file = st.file_uploader("Upload Procurement Data (CSV)", type="csv")
    
    if uploaded_file:
        try:
            # Create initial state with config
            initial_state: ProcurementState = {
                "requisitions": pd.read_csv(uploaded_file).to_dict("records"),
                "config": config,
                "clusters": [],
                "recommendations": [],
                "sourcing_events": [],
                "errors": []
            }
            
            workflow = create_procurement_workflow()
            results = workflow.invoke(initial_state)
            display_results(results)
            
        except Exception as e:
            st.error(f"Processing failed: {str(e)}")

#if __name__=="__main__":
#   main()