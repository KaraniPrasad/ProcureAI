# tools/procurement.py

import re
import logging
from datetime import timedelta
from typing import Dict, List
import pandas as pd
from sklearn.cluster import DBSCAN
from sklearn.feature_extraction.text import TfidfVectorizer
from src.procurement_ai.state.procurement_state import ProcurementState

logger = logging.getLogger(__name__)

class ProcurementAnalyzer:
    """Handles requisition analysis and clustering"""
    
    def analyze_requisitions(self, state: ProcurementState) -> ProcurementState:
        """Main analysis entry point"""
        try:
            if not state.get("requisitions"):
                raise ValueError("No requisitions provided")

            req_df = pd.DataFrame(state["requisitions"])
            req_df = self._preprocess_data(req_df)
            req_df = self._perform_clustering(req_df)
            
            return {
                "clusters": self._create_cluster_objects(req_df),
                "raw_data": req_df.to_dict(orient='records'),
                "errors": state.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return self._add_error(state, f"Analysis error: {str(e)}")

    def _preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Data cleaning and feature engineering"""
        df['required_date'] = pd.to_datetime(df['required_date'])
        df['unspsc'] = df['unspsc'].astype(str).apply(self._validate_unspsc)
        df['unspsc_family'] = df['unspsc'].str[:8]
        df['total_value'] = df['unit_price'] * df['quantity']
        return df

    def _validate_unspsc(self, code: str) -> str:
        """Validate and format UNSPSC code"""
        code = str(code).zfill(8)
        if not re.match(r"^\d{8}$", code):
            raise ValueError(f"Invalid UNSPSC format: {code}")
        return code

    def _perform_clustering(self, df: pd.DataFrame) -> pd.DataFrame:
        """Hierarchical clustering implementation"""
        df['base_cluster'] = df.groupby('unspsc_family').ngroup()
        
        vectorizer = TfidfVectorizer(stop_words='english', max_features=500)
        tfidf_matrix = vectorizer.fit_transform(df['description'])
        
        dbscan = DBSCAN(eps=0.5, min_samples=2, metric='cosine')
        df['nlp_cluster'] = dbscan.fit_predict(tfidf_matrix)
        
        df['final_cluster'] = (
            df['base_cluster'].astype(str) + 
            "_" + 
            df['nlp_cluster'].astype(str)
        )
        return df

    def _create_cluster_objects(self, df: pd.DataFrame) -> List[Dict]:
        """Convert dataframe to cluster objects"""
        clusters = []
        for cluster_id in df['final_cluster'].unique():
            cluster_df = df[df['final_cluster'] == cluster_id]
            
            clusters.append({
                "cluster_id": cluster_id,
                "unspsc_family": cluster_df['unspsc_family'].mode()[0],
                "total_value": cluster_df['total_value'].sum(),
                "units": cluster_df['quantity'].sum(),
                "locations": cluster_df['delivery_location'].unique().tolist(),
                "earliest_delivery": cluster_df['required_date'].min().strftime('%Y-%m-%d'),
                "latest_delivery": cluster_df['required_date'].max().strftime('%Y-%m-%d'),
                "item_count": len(cluster_df)
            })
        return clusters

    def _add_error(self, state: ProcurementState, error: str) -> ProcurementState:
        """Error handling helper"""
        state.setdefault("errors", []).append(error)
        return state


class RecommendationEngine:
    """Generates consolidation recommendations with UI parameters"""
    
    def suggest_aggregation(self, state: ProcurementState) -> ProcurementState:
        """Main recommendation generator"""
        try:
            config = state.get("config", {})
            clusters = state.get("clusters", [])
            
            return {
                "recommendations": [
                    self._create_recommendation(c, config) 
                    for c in clusters
                ],
                "errors": state.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Recommendation failed: {str(e)}")
            return self._add_error(state, f"Recommendation error: {str(e)}")

    def _create_recommendation(self, cluster: Dict, config: Dict) -> Dict:
        """Individual recommendation logic"""
        moq = config.get("moq", 25000)
        max_window = config.get("consolidation_window_days", 14)
        
        time_delta = (
            pd.to_datetime(cluster['latest_delivery']) - 
            pd.to_datetime(cluster['earliest_delivery'])
        ).days
        
        meets_moq = cluster['total_value'] >= moq
        meets_window = time_delta <= max_window
        
        if meets_moq and meets_window:
            return {
                "recommendation": "consolidate",
                "rationale": (
                    f"Meets MOQ (${moq}) and delivery window "
                    f"({time_delta}d <= {max_window}d)"
                ),
                "potential_savings": cluster['total_value'] * 0.15,
                "total_quantity": cluster['units'],
                "cluster_id": cluster['cluster_id']
            }
            
        rationale_parts = []
        if not meets_moq:
            rationale_parts.append(f"Value ${cluster['total_value']} < MOQ ${moq}")
        if not meets_window:
            rationale_parts.append(f"Window {time_delta}d > {max_window}d")
            
        return {
            "recommendation": "process_individually",
            "rationale": ". ".join(rationale_parts),
            "cluster_id": cluster['cluster_id']
        }

    def _add_error(self, state: ProcurementState, error: str) -> ProcurementState:
        state.setdefault("errors", []).append(error)
        return state


class SourcingManager:
    """Creates sourcing events with UI parameters"""
    
    def create_sourcing_event(self, state: ProcurementState) -> ProcurementState:
        """Sourcing event creation entry point"""
        try:
            config = state.get("config", {})
            buffer_days = config.get("consolidation_window_days", 14)
            
            return {
                "sourcing_events": self._generate_events(state, buffer_days),
                "errors": state.get("errors", [])
            }
            
        except Exception as e:
            logger.error(f"Sourcing event failed: {str(e)}")
            return self._add_error(state, f"Sourcing error: {str(e)}")

    def _generate_events(self, state: ProcurementState, buffer_days: int) -> List[Dict]:
        """Generate sourcing event objects"""
        return [
            self._create_event(cluster, buffer_days)
            for cluster in state.get("clusters", [])
            if self._should_create_event(cluster, state)
        ]

    def _should_create_event(self, cluster: Dict, state: ProcurementState) -> bool:
        """Check if cluster has consolidation recommendation"""
        return any(
            rec["recommendation"] == "consolidate" and 
            rec["cluster_id"] == cluster["cluster_id"]
            for rec in state.get("recommendations", [])
        )

    def _create_event(self, cluster: Dict, buffer_days: int) -> Dict:
        """Individual event creation"""
        start_date = pd.to_datetime(cluster['earliest_delivery'])
        end_date = pd.to_datetime(cluster['latest_delivery'])
        
        return {
            "event_type": "RFQ",
            "cluster_id": cluster['cluster_id'],
            "unspsc_family": cluster['unspsc_family'],
            "total_value": cluster['total_value'],
            "required_dates": {
                "start": start_date.strftime('%Y-%m-%d'),
                "end": (end_date + timedelta(days=buffer_days)).strftime('%Y-%m-%d')
            },
            "geographic_scope": cluster['locations'],
            "total_quantity": int(cluster['units']),
            "evaluation_criteria": ["price", "quality", "delivery_time"],
            "applied_parameters": {
                "moq": cluster['total_value'],
                "delivery_window": buffer_days
            }
        }

    def _add_error(self, state: ProcurementState, error: str) -> ProcurementState:
        state.setdefault("errors", []).append(error)
        return state