import pandas as pd
import numpy as np
import os
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from flask import current_app

def train_delivery_model():
    """
    Train a machine learning model to predict delivery time based on distance
    """
    try:
        # Try to use the pre-loaded training data from the application config
        if hasattr(current_app, 'config') and 'TRAINING_DATA' in current_app.config:
            df = current_app.config['TRAINING_DATA']
            print("Using pre-loaded training data")
        else:
            # If not available, try to load from the CSV file
            dataset_path = "Delhivery_Logistics_Cleaned.csv"
            if os.path.exists(dataset_path):
                df = pd.read_csv(dataset_path)
                print(f"Loaded training data from {dataset_path}")
            else:
                # Fallback to the shipments data if available
                fallback_path = "data/shipments.csv"
                if os.path.exists(fallback_path):
                    df = pd.read_csv(fallback_path)
                    print(f"Using fallback data from {fallback_path}")
                else:
                    print("No training data available")
                    return create_dummy_model()
        
        # Filter rows with valid distance and time data
        # Adjust these column names based on your actual dataset structure
        distance_col = 'distance' if 'distance' in df.columns else 'Distance_Km'
        time_col = 'estimated_time' if 'estimated_time' in df.columns else 'Time_Taken_Hrs'
        
        df = df.dropna(subset=[distance_col, time_col])
        
        if len(df) >= 5:  # Only train if we have enough data
            # Prepare features and target
            X = df[[distance_col]]
            y = df[time_col]
            
            # If time is in hours and we want minutes, convert
            if time_col == 'Time_Taken_Hrs':
                y = y * 60  # Convert hours to minutes
            
            try:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                model = GradientBoostingRegressor(n_estimators=100, random_state=42)
                model.fit(X_train, y_train)
                return model
            except Exception as e:
                print(f"Error during model training: {e}")
                return create_dummy_model()
        else:
            return create_dummy_model()
    except Exception as e:
        print(f"Overall error in train_delivery_model: {e}")
        return create_dummy_model()

def create_dummy_model():
    """
    Create a simple dummy model when not enough data is available
    This model assumes 1 km takes about 2 minutes on average
    """
    class DummyModel:
        def predict(self, X):
            # Simple formula: ~2 min per km
            return X.iloc[:, 0] * 2 + np.random.normal(0, 5, size=len(X))
    
    return DummyModel()

def predict_delivery_time(model, distance):
    """
    Predict delivery time based on distance using the trained model
    """
    try:
        input_data = pd.DataFrame([[distance]], columns=['distance'])
        prediction = model.predict(input_data)[0]
        return round(prediction, 2)
    except Exception as e:
        print(f"Prediction error: {e}")
        # Fallback to a simple heuristic if prediction fails
        return round(distance * 2, 2)  # ~2 min per km