import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_ai_model(csv_path="data/large_nodes.csv", model_path="ai_node_model.pkl"):
    df = pd.read_csv(csv_path)
    # Features
    X = df[['latitude','longitude','energy','health']]
    # Target: Node failure (1 إذا health < 50)
    y = df['health'].apply(lambda x: 1 if x<50 else 0)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    joblib.dump(model, model_path)
    return model

def predict_failure(model, node_features):
    """
    node_features = dict {latitude, longitude, energy, health}
    """
    X = pd.DataFrame([node_features])  # استخدم DataFrame مع أسماء الأعمدة
    return model.predict(X)[0]  # 0 = ok, 1 = fail
