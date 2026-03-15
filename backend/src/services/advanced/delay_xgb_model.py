import xgboost as xgb
import pandas as pd
import numpy as np
import pickle
import os
import logging
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score

logger = logging.getLogger(__name__)

# Target variable threshold (e.g. flight is delayed if > 15 minutes late)
DELAY_THRESHOLD_MINUTES = 15

# Global path for saving models
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ml", "models")
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "delay_xgb_baseline.pkl")

class XGBoostBaselineModel:
    def __init__(self):
        self.model = None
        self.features = [
            'departure_hour', 
            'minutes_to_departure', 
            'congestion_score', 
            'weather_severity'
        ]
        
    def train(self, df: pd.DataFrame):
        """
        Train the baseline XGBoost model.
        Expects a DataFrame with the output of FeatureEngineer.construct_ml_features
        AND actual historical delays.
        """
        logger.info("Starting XGBoost training...")
        
        # 1. Prepare target variable (Binary classification)
        if 'actual_departure' not in df.columns or 'scheduled_departure' not in df.columns:
            logger.error("Missing actual or scheduled departure times. Cannot train target.")
            return False
            
        # Calculate actual delay
        delay_seconds = (df['actual_departure'] - df['scheduled_departure']).dt.total_seconds()
        df['actual_delay_minutes'] = delay_seconds / 60.0
        
        # 0 = On Time, 1 = Delayed
        df['is_delayed'] = (df['actual_delay_minutes'] > DELAY_THRESHOLD_MINUTES).astype(int)
        
        # Drop rows where target is NaN (flights that haven't departed yet)
        df_trainable = df.dropna(subset=['is_delayed'] + self.features)
        
        if len(df_trainable) < 100:
            logger.warning("Insufficient data to train robust model. Need at least 100 historical records.")
            return False
            
        X = df_trainable[self.features]
        y = df_trainable['is_delayed']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # 2. Train model
        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            n_estimators=100,
            learning_rate=0.1,
            max_depth=5,
            random_state=42,
            eval_metric='auc'
        )
        
        self.model.fit(X_train, y_train)
        
        # 3. Evaluate
        preds = self.model.predict(X_test)
        preds_proba = self.model.predict_proba(X_test)[:, 1]
        
        metrics = {
            "accuracy": accuracy_score(y_test, preds),
            "precision": precision_score(y_test, preds, zero_division=0),
            "recall": recall_score(y_test, preds, zero_division=0),
            "auc": roc_auc_score(y_test, preds_proba)
        }
        
        logger.info(f"Model trained successfully. Metrics: {metrics}")
        
        # 4. Save
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)
            
        logger.info(f"Model saved to {MODEL_PATH}")
        return metrics

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        """
        Predict delay probability for new flights.
        Returns array of probabilities [0.0 - 1.0].
        """
        if self.model is None:
            self._load_model()
            
        # Ensure only expected features are passed
        X = df[self.features].fillna(0.0) # Impute missing inferences with 0 (baseline)
        
        # Return probability of class 1 (Delayed)
        probabilities = self.model.predict_proba(X)[:, 1]
        return probabilities

    def _load_model(self):
        if not os.path.exists(MODEL_PATH):
            raise Exception("No trained model found. Please train first.")
        with open(MODEL_PATH, 'rb') as f:
            self.model = pickle.load(f)
