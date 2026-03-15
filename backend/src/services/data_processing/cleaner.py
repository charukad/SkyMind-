import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class DataNormalizer:
    @staticmethod
    def clean_flight_data(raw_flights: list[dict]) -> pd.DataFrame:
        """
        Takes raw dictionary flight data (from APIs or DB) and cleans it.
        - Resolves missing callsigns
        - Normalizes timestamps to UTC
        - Computes baseline features like 'minutes_to_departure'
        """
        if not raw_flights:
            return pd.DataFrame()
            
        df = pd.DataFrame(raw_flights)
        
        # 1. Handle missing values
        # Fill missing origin/dest with UNK (Unknown) to prevent ML dropping entire rows
        df['origin_iata'] = df['origin_iata'].fillna('UNK')
        df['destination_iata'] = df['destination_iata'].fillna('UNK')
        
        # 2. Convert string times to datetime objects if needed
        time_cols = ['scheduled_departure', 'scheduled_arrival', 'actual_departure', 'actual_arrival']
        for col in time_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
        # 3. Create basic derived temporal features
        now = datetime.utcnow()
        if 'scheduled_departure' in df.columns:
            # Time until scheduled departure (negative means already departed)
            df['minutes_to_departure'] = (df['scheduled_departure'] - now).dt.total_seconds() / 60.0
            
            # Simple feature: hour of day (useful for predicting evening rush-hour delays)
            df['departure_hour'] = df['scheduled_departure'].dt.hour
            
        logger.info(f"Cleaned {len(df)} flight records.")
        return df

    @staticmethod
    def clean_weather_data(raw_weather: list[dict]) -> pd.DataFrame:
        """
        Normalizes weather events into a standard ML format.
        """
        if not raw_weather:
            return pd.DataFrame()
            
        df = pd.DataFrame(raw_weather)
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
            
        # One-hot encode the categorical conditions for ML ingestion
        if 'condition' in df.columns:
            conditions_dummies = pd.get_dummies(df['condition'], prefix='weather')
            df = pd.concat([df, conditions_dummies], axis=1)
            
        # Ensure severity score is bounded 0.0 - 1.0
        if 'severity_score' in df.columns:
            df['severity_score'] = df['severity_score'].clip(lower=0.0, upper=1.0)
            
        logger.info(f"Cleaned {len(df)} weather records.")
        return df
