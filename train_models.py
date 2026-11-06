# train_models.py

import os
import django
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import joblib

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'immo_predict_mada.settings')
django.setup()

from predictor.models import Rental, Land


def train_rental_model():
    print("Training Rental Model...")

    rentals = Rental.objects.all().values(
        'town_id', 'access_type', 'property_type', 'subtype', 'num_rooms',
        'exterior_showers_toilets', 'interior_showers_toilets', 'garage', 'garden',
        'price'
    )
    df = pd.DataFrame(list(rentals))

    if df.empty or len(df) < 10:
        print("Not enough data to train the rental model. Please add more data.")
        return

    y = df['price']
    X = df.drop('price', axis=1)
    X = X.rename(columns={'town_id': 'town'})

    categorical_cols = ['town', 'access_type', 'property_type', 'subtype']
    X_encoded = pd.get_dummies(X, columns=categorical_cols, drop_first=False)


    model_columns = list(X_encoded.columns)
    joblib.dump(model_columns, 'ml_models/rental_encoder.joblib')
    print("Rental model columns saved successfully.")

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    mse = mean_squared_error(y_test, predictions)
    rmse = np.sqrt(mse)
    print(f"Rental Model RMSE: {rmse}")

    joblib.dump(model, 'ml_models/rental_model.joblib')
    print("Rental model saved successfully.")


def train_land_model():
    print("\nTraining Land Model...")
    lands = Land.objects.all().values(
        'town_id', 'paper_type', 'access_type', 'is_fenced', 'is_ready_to_build',
        'superficy', 'price'
    )
    df = pd.DataFrame(list(lands))
    if df.empty or len(df) < 10:
        print("Not enough data to train land model.")
        return

    df['superficy'] = pd.to_numeric(df['superficy'])
    df['price'] = pd.to_numeric(df['price'])
    df = df[df['superficy'] > 0].copy()
    df['price_per_sqm'] = df['price'] / df['superficy']

    y = df['price_per_sqm']
    X = df.drop(['price', 'price_per_sqm'], axis=1).rename(columns={'town_id': 'town'})
    categorical_cols = ['town', 'paper_type', 'access_type']
    X_encoded = pd.get_dummies(X, columns=categorical_cols)

    model_columns = list(X_encoded.columns)
    joblib.dump(model_columns, 'ml_models/land_encoder.joblib')
    print("Land model columns saved successfully.")

    X_train, X_test, y_train, y_test = train_test_split(X_encoded, y, test_size=0.2, random_state=42)
    model = LinearRegression().fit(X_train, y_train)
    predictions = model.predict(X_test)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    print(f"Land Model RMSE: {rmse}")

    joblib.dump(model, 'ml_models/land_model.joblib')
    print("Land model saved successfully.")


if __name__ == '__main__':
    if not os.path.exists('ml_models'):
        os.makedirs('ml_models')

    train_rental_model()
    train_land_model()