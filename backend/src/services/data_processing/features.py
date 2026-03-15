import pandas as pd
import numpy as np

class FeatureEngineer:
    
    @staticmethod
    def calculate_airport_congestion(flights_df: pd.DataFrame, airport_col: str = 'origin_iata', window_hours: int = 2) -> pd.DataFrame:
        """
        Calculates a moving congestion score for an airport based on the number 
        of flights scheduled in a rolling time window.
        """
        if flights_df.empty or 'scheduled_departure' not in flights_df.columns:
            return flights_df
            
        df = flights_df.copy()
        df = df.sort_values(by='scheduled_departure')
        
        # Calculate rolling count of flights grouped by the origin airport
        df['congestion_score'] = df.groupby(airport_col)['scheduled_departure'] \
            .apply(lambda x: x.rolling(f'{window_hours}h', on=x).count()) \
            .reset_index(level=0, drop=True)
            
        # Normalize between 0 and 1 using a generic max threshold (e.g. 50 flights per hour)
        MAX_HOURLY_FLIGHTS = 50 * window_hours
        df['congestion_score'] = (df['congestion_score'] / MAX_HOURLY_FLIGHTS).clip(lower=0.0, upper=1.0)
        
        return df

    @staticmethod
    def merge_weather_features(flights_df: pd.DataFrame, weather_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merges weather severity scores into the flight data based on the origin airport 
        and closest matching time.
        """
        if flights_df.empty or weather_df.empty:
            flights_df['weather_severity'] = 0.0
            return flights_df
            
        # Need to sort for merge_asof
        f_df = flights_df.sort_values('scheduled_departure')
        w_df = weather_df.sort_values('timestamp')
        
        # Merge asof takes the weather record closest to the flight departure time
        # but only backwards in time (we can't know the future weather for prediction unless forecasted)
        merged_df = pd.merge_asof(
            f_df, w_df,
            left_on='scheduled_departure',
            right_on='timestamp',
            by_left='origin_iata',
            by_right='airport_iata',
            direction='backward',
            tolerance=pd.Timedelta('6h') # Fill with weather up to 6 hours old
        )
        
        # If no matching weather, assume 0 severity
        merged_df['severity_score'] = merged_df['severity_score'].fillna(0.0)
        merged_df.rename(columns={'severity_score': 'weather_severity'}, inplace=True)
        
        # Drop redundant weather columns from merge
        cols_to_drop = [c for c in merged_df.columns if c.startswith('weather_') and c != 'weather_severity']
        if 'timestamp' in merged_df.columns:
            cols_to_drop.append('timestamp')
        if 'airport_iata' in merged_df.columns:
            cols_to_drop.append('airport_iata')
            
        merged_df.drop(columns=cols_to_drop, inplace=True, errors='ignore')
        
        return merged_df
        
    @staticmethod
    def construct_ml_features(flights: list[dict], weather: list[dict] = None) -> pd.DataFrame:
        """Main pipeline runner to combine raw dicts into XGBoost-ready DataFrames."""
        from .cleaner import DataNormalizer
        
        f_df = DataNormalizer.clean_flight_data(flights)
        
        if f_df.empty:
            return f_df
            
        f_df = FeatureEngineer.calculate_airport_congestion(f_df)
        
        if weather and len(weather) > 0:
            w_df = DataNormalizer.clean_weather_data(weather)
            f_df = FeatureEngineer.merge_weather_features(f_df, w_df)
        else:
            f_df['weather_severity'] = 0.0
            
        return f_df
