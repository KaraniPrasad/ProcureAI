# ui/upload.py
import streamlit as st
import pandas as pd
from typing import Optional, Tuple
from src.procurement_ai.state.procurement_state import ProcurementState

def handle_file_upload() -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """Handle file upload and validation"""
    uploaded_file = st.file_uploader(
        "Upload Procurement Data (CSV)",
        type="csv",
        help="Upload a CSV file with columns: 'unspsc', 'description', 'quantity', 'unit_price', 'required_date', 'delivery_location'"
    )
    
    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)
            
            # Validate required columns
            required_columns = {
                'unspsc', 'description', 'quantity',
                'unit_price', 'required_date', 'delivery_location'
            }
            
            if not required_columns.issubset(df.columns):
                missing = required_columns - set(df.columns)
                return None, f"Missing required columns: {', '.join(missing)}"
                
            # Basic data validation
            if df['quantity'].min() < 0:
                return None, "Quantity values cannot be negative"
                
            if df['unit_price'].min() < 0:
                return None, "Unit price values cannot be negative"
                
            return df, None
            
        except Exception as e:
            return None, f"File processing error: {str(e)}"
    
    return None, None

def create_initial_state(df: pd.DataFrame) -> ProcurementState:
    """Create initial workflow state from validated data"""
    return {
        "requisitions": df.to_dict("records"),
        "config": st.session_state.config,
        "clusters": [],
        "recommendations": [],
        "sourcing_events": [],
        "errors": []
    }