import shap
import pandas as pd
import numpy as np
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ModelExplainer:
    def __init__(self, model):
        """
        Initializes the SHAP TreeExplainer for the XGBoost model.
        """
        self.model = model
        self.explainer = None
        
        if self.model is not None:
            self.explainer = shap.TreeExplainer(self.model)
            
    def explain_prediction(self, df: pd.DataFrame, features: list[str]) -> Dict[str, Any]:
        """
        Generate feature importance and a human-readable explanation for a single prediction.
        Expects a DataFrame containing exactly 1 row.
        """
        if self.explainer is None:
            return {"error": "Model explainer not initialized"}
            
        if len(df) != 1:
            return {"error": "Explanation requires exactly 1 row of data"}
            
        X = df[features].fillna(0.0)
        
        # Calculate SHAP values
        shap_values = self.explainer.shap_values(X)
        
        # XGBoost binary classification returns margin values, convert to probabilities
        base_value = self.explainer.expected_value
        
        # Map feature names to their impact score
        impacts = {}
        for i, feature in enumerate(features):
            impacts[feature] = float(shap_values[0][i])
            
        # Sort features by highest impact on delay
        sorted_impacts = sorted(impacts.items(), key=lambda t: t[1], reverse=True)
        top_factor, top_impact = sorted_impacts[0]
        
        # Generate plain english explanation
        explanation = self._generate_nlp_explanation(top_factor, top_impact, X.iloc[0])
        
        return {
            "top_risk_factor": top_factor,
            "feature_impacts": impacts,
            "explanation": explanation,
            "base_risk_score": float(base_value)
        }
        
    def _generate_nlp_explanation(self, top_factor: str, top_impact: float, row: pd.Series) -> str:
        """Translates ML SHAP values into actionable operational intelligence."""
        
        if top_impact < 0:
            return "Flight is expected to operate on time with minimal risk factors."
            
        if top_factor == 'congestion_score':
            val = round(row['congestion_score'] * 100, 1)
            return f"High risk of delay due to severe airport congestion ({val}% capacity utilization)."
        elif top_factor == 'weather_severity':
            val = round(row['weather_severity'] * 10, 1)
            return f"High risk of delay due to severe weather conditions (Severity: {val}/10)."
        elif top_factor == 'minutes_to_departure':
            return "Delay risk is elevated due to the proximity to scheduled departure without active movement."
        elif top_factor == 'departure_hour':
            return "Delay risk is elevated due to peak-hour evening cascading effects."
            
        return "Delay expected due to compound network factors."
