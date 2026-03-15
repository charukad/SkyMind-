import pandas as pd
from prophet import Prophet
import os
import pickle
import logging

logger = logging.getLogger(__name__)

# Global path for saving passenger demand models
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)

class DemandForecastingModel:
    def __init__(self, route_id: str):
        """
        Initializes a Prophet model for a specific route (e.g., 'JFK-LHR').
        Prophet typically trains a unique model per independent time series.
        """
        self.route_id = route_id
        self.model = None
        self.model_path = os.path.join(MODEL_DIR, f"demand_prophet_{self.route_id}.pkl")
        
    def train(self, df: pd.DataFrame):
        """
        Train the Prophet model.
        Expects a DataFrame with 'ds' (datetime) and 'y' (passenger count).
        """
        logger.info(f"Starting Prophet training for route {self.route_id}...")
        
        if 'ds' not in df.columns or 'y' not in df.columns:
            logger.error("Dataframe must contain 'ds' (date) and 'y' (target) columns.")
            return False
            
        if len(df) < 30:
            logger.warning("Insufficient data points. Need at least 30 days of historical data.")
            return False
            
        # Prophet handles missing data well, but we should drop NaNs in the target
        df_trainable = df.dropna(subset=['y', 'ds'])
        
        # Initialize Prophet with holiday effects and yearly seasonality
        self.model = Prophet(
            yearly_seasonality=True,
            weekly_seasonality=True,
            daily_seasonality=False # Passenger load is usually daily aggregated, not hourly
        )
        
        # Add built-in country holidays if known (e.g. US)
        # In a generic global network, this gets complex based on origin/dest countries
        self.model.add_country_holidays(country_name='US')
        
        self.model.fit(df_trainable)
        
        # Save model
        with open(self.model_path, 'wb') as f:
            pickle.dump(self.model, f)
            
        logger.info(f"Model saved to {self.model_path}")
        return True

    def forecast_demand(self, days_ahead: int = 30) -> pd.DataFrame:
        """
        Forecast passenger demand for the next N days.
        Returns a dataframe with 'ds', 'yhat' (prediction), 'yhat_lower', 'yhat_upper'
        """
        if self.model is None:
            self._load_model()
            
        future = self.model.make_future_dataframe(periods=days_ahead)
        forecast = self.model.predict(future)
        
        # We only care about the future predictions, so tail the dataframe
        future_forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days_ahead)
        
        # Passenger count obviously cannot be negative
        for col in ['yhat', 'yhat_lower', 'yhat_upper']:
            future_forecast[col] = future_forecast[col].clip(lower=0).round(0).astype(int)
            
        return future_forecast

    def _load_model(self):
        if not os.path.exists(self.model_path):
            raise Exception(f"No trained model found for route {self.route_id}. Please train first.")
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
