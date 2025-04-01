import pandas as pd
import numpy as np
import os
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split

def train_delivery_model():
    """
    Train a machine learning model to predict delivery time based on distance
    """
    # Load or create dataset
    dataset_path = "data/shipments.csv"
    
    if os.path.exists(dataset_path):
        df = pd.read_csv(dataset_path)
        # Filter rows with valid distance and time data
        df = df.dropna(subset=['distance', 'estimated_time'])
        
        if len(df) >= 5:  # Only train if we have enough data
            # Prepare features and target
            X = df[['distance']]
            y = df['estimated_time']
            
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
    else:
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