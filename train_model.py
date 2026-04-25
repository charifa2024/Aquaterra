import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os

print("📦 Loading dataset...")
df = pd.read_csv("Crop_recommendation.csv")

print(f"✅ Dataset loaded: {len(df)} rows, columns: {list(df.columns)}")
print(df.head())

# Features and target
X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
y = df['label']

# Encode labels
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train
print("\n🤖 Training Random Forest model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)
print(f"\n✅ Model accuracy: {acc * 100:.2f}%")

# Save model and encoder
joblib.dump(model, "crop_model.pkl")
joblib.dump(le, "label_encoder.pkl")
print("💾 Model saved: crop_model.pkl")
print("💾 Encoder saved: label_encoder.pkl")
