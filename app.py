import streamlit as st
import joblib
import numpy as np

# Load model
model = joblib.load("rock_mine.pkl")

st.title("🚢 Submarine Sonar: Mine vs Rock Detector")

# Simulate SONAR input (replace with real data)
st.sidebar.header("Simulate SONAR Data")
input_features = []
for i in range(60):  # Assuming 60 features
    val = st.sidebar.slider(f"Feature {i+1}", 0.0, 1.0, 0.5)
    input_features.append(val)

# Predict
if st.button("Detect Object"):
    prediction = model.predict([input_features])
    if prediction[0] == 1:
        st.error("💣 MINE DETECTED! EVASIVE ACTION!")
    else:
        st.success("🪨 It's just a rock. Proceeding safely.")

    # Show probability
    proba = model.predict_proba([input_features])[0]
    st.write(f"Confidence: {max(proba)*100:.2f}%")