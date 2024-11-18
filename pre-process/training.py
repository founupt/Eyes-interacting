# file: train_eye_tracking.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import joblib

data_path = "eye_tracking_data.csv" 
data = pd.read_csv(data_path)

X = data[['left_pupil_x', 'left_pupil_y', 'right_pupil_x', 'right_pupil_y']]
y = data[['left_eye_closed', 'right_eye_closed']]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy of the model: {accuracy:.2f}")

model_path = "eye_tracking_model.pkl"
joblib.dump(model, model_path)
print(f"Model saved to {model_path}")
