# app.py

import streamlit as st
import pandas as pd

import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestClassifier

# Load your dataset


df = pd.read_csv('Machine-Data/feature_engineered_data.csv', parse_dates=True)


st.title("📉 Equipment Failure Risk Predictor")
st.markdown("Predict maintenance needs using historical usage and asset features.")

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Equipment")
    type_filter = st.multiselect("Type", options=df["Type"].unique(), default=list(df["Type"].unique()))
    location_filter = st.multiselect("Location", options=df["Location"].unique(), default=list(df["Location"].unique()))
    manu_filter = st.multiselect("Manufacturer", options=df["Manufacturer"].unique(), default=list(df["Manufacturer"].unique()))

# Filter data
filtered_df = df[
    df["Type"].isin(type_filter) &
    df["Location"].isin(location_filter) &
    df["Manufacturer"].isin(manu_filter)
].copy()

# Define features and target
features = ['Avg_Usage_Hours', 'Total_Usage_Hours', 'Usage_Std', 'Days_Since_Last_Maintenance', 'Days_Since_Purchase']
['Equipment_ID', 'Purchase_Date', 'Avg_Usage_Hours', 'Total_Usage_Hours',
       'Usage_Std', 'Last_Maintenance_Date', 'Failure_Flag',
       'Days_Since_Last_Maintenance', 'Days_Since_Purchase']
X = filtered_df[features].fillna(0)
y = filtered_df['Failure_Flag']

# Train model (in memory for demonstration)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)
pred_probs = model.predict_proba(X)[:, 1]
filtered_df["Predicted_Failure_Prob"] = np.round(pred_probs, 2)

# Show table
st.subheader("📋 Equipment Risk Table")
st.dataframe(filtered_df[["Equipment_ID", "Type", "Location", "Manufacturer", "Predicted_Failure_Prob"]].sort_values("Predicted_Failure_Prob", ascending=False))

# Plot
st.subheader("📊 Failure Risk Distribution")
fig, ax = plt.subplots(figsize=(8, 4))
filtered_df["Predicted_Failure_Prob"].hist(bins=10, color="orange", edgecolor="black", ax=ax)
ax.set_xlabel("Predicted Failure Probability")
ax.set_ylabel("Count of Equipment")
st.pyplot(fig)

# Feature importance
st.subheader("🔎 Feature Importance")
importances = model.feature_importances_
feat_df = pd.DataFrame({"Feature": features, "Importance": importances}).sort_values(by="Importance", ascending=False)
st.bar_chart(feat_df.set_index("Feature"))

# Download
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button("📥 Download Predictions", csv, "failure_predictions.csv", "text/csv")
