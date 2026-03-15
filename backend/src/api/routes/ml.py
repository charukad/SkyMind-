from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Dict, Any
import pandas as pd
import logging

from src.services.advanced.delay_xgb_model import XGBoostBaselineModel
from src.services.advanced.explainability import ModelExplainer
from src.services.advanced.demand_forecasting import DemandForecastingModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ml", tags=["Machine Learning Inference"])

# Load models into memory once at startup
try:
    delay_model = XGBoostBaselineModel()
    delay_model._load_model()
    explainer = ModelExplainer(delay_model.model)
    logger.info("ML Models loaded successfully.")
except Exception as e:
    logger.warning(f"Failed to load ML models on startup. Will lazy load when required or error. Details: {str(e)}")
    delay_model = XGBoostBaselineModel()
    explainer = None


class FlightInferenceRequest(BaseModel):
    # Features required by the baseline XGBoost model
    departure_hour: int = Field(..., ge=0, le=23)
    minutes_to_departure: float
    congestion_score: float = Field(..., ge=0.0, le=1.0)
    weather_severity: float = Field(0.0, ge=0.0, le=1.0)

class DelayPredictionResponse(BaseModel):
    probability_delayed: float
    is_delayed_prediction: bool
    explanation: Dict[str, Any]

class DemandForecastRequest(BaseModel):
    route_id: str # e.g. "JFK-LHR"
    days_ahead: int = Field(30, ge=1, le=365)

@router.post("/predict-delay", response_model=DelayPredictionResponse)
async def predict_flight_delay(request: FlightInferenceRequest):
    """
    Predict if a flight will be delayed > 15 minutes based on dynamic features.
    Provides SHAP-powered plain english explanations.
    """
    # Convert Pydantic request to DataFrame for ML models
    df = pd.DataFrame([request.model_dump()])
    
    try:
        # Get probability
        probs = delay_model.predict(df)
        probability = float(probs[0])
        
        # Get explanation
        if explainer is None and delay_model.model is not None:
            explainer_inst = ModelExplainer(delay_model.model)
            explanation = explainer_inst.explain_prediction(df, delay_model.features)
        elif explainer is not None:
            explanation = explainer.explain_prediction(df, delay_model.features)
        else:
            explanation = {"error": "Model not loaded"}
            
        return DelayPredictionResponse(
            probability_delayed=probability,
            is_delayed_prediction=probability > 0.5,
            explanation=explanation
        )
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        raise HTTPException(status_code=500, detail="ML inference engine error.")

@router.post("/forecast-demand")
async def forecast_passenger_demand(request: DemandForecastRequest):
    """
    Predict future passenger loads for a specific route using Facebook Prophet.
    """
    try:
        forecaster = DemandForecastingModel(route_id=request.route_id)
        # Attempt to load, will raise if model does not exist for this route
        forecaster._load_model() 
        
        result_df = forecaster.forecast_demand(days_ahead=request.days_ahead)
        
        # Convert Prophet df back to native dict format
        # Replace NaN with None for JSON serialization
        result_df = result_df.replace({pd.NA: None}) 
        # Convert timestamp to string
        result_df['ds'] = result_df['ds'].dt.strftime('%Y-%m-%d')
        
        return {
            "route_id": request.route_id,
            "forecast": result_df.to_dict(orient="records")
        }
    except Exception as e:
        logger.error(f"Demand forecasting failed: {e}")
        raise HTTPException(status_code=404, detail=f"Failed to fetch forecast. Does model for {request.route_id} exist? Details: {str(e)}")
