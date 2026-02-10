import streamlit as st
import pandas as pd
import mysql.connector
import pickle
import os

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="Car Analytics & Brand Prediction",
    layout="wide"
)

st.title("🚗 Car Analytics & Brand Prediction System")

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Siva",          # change if needed
        database="car_analytics"
    )

# -------------------------------------------------
# LOAD MODEL SAFELY (DEPLOYMENT-SAFE)
# -------------------------------------------------
@st.cache_resource
def load_model():
    model_path = "model/car_brand_model.pkl"
    encoder_path = "model/label_encoders.pkl"

    if not os.path.exists(model_path) or not os.path.exists(encoder_path):
        return None, None

    with open(model_path, "rb") as f:
        model = pickle.load(f)

    with open(encoder_path, "rb") as f:
        encoders = pickle.load(f)

    return model, encoders

model, label_encoders = load_model()

# -------------------------------------------------
# SIDEBAR
# -------------------------------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Analytics Dashboard", "Car Brand Prediction"]
)

# =================================================
# 📊 ANALYTICS DASHBOARD
# =================================================
if page == "Analytics Dashboard":
    st.subheader("📊 Business Insights")

    conn = get_connection()

    # -------- KPIs --------
    st.markdown("### 📌 Key Metrics")
    col1, col2, col3 = st.columns(3)

    total_cars = pd.read_sql("SELECT COUNT(*) AS total FROM cars", conn)
    total_brands = pd.read_sql("SELECT COUNT(DISTINCT car_brand) AS total FROM cars", conn)
    total_countries = pd.read_sql("SELECT COUNT(DISTINCT country) AS total FROM cars", conn)

    col1.metric("Total Cars", int(total_cars.iloc[0, 0]))
    col2.metric("Unique Brands", int(total_brands.iloc[0, 0]))
    col3.metric("Countries Covered", int(total_countries.iloc[0, 0]))

    st.divider()

    # -------- Top Brands --------
    st.markdown("### 🚘 Top 5 Car Brands")
    df_brands = pd.read_sql("""
        SELECT car_brand, COUNT(*) AS total
        FROM cars
        GROUP BY car_brand
        ORDER BY total DESC
        LIMIT 5
    """, conn)
    st.bar_chart(df_brands.set_index("car_brand"))

    # -------- Top Models --------
    st.markdown("### 🚗 Top 5 Car Models")
    df_models = pd.read_sql("""
        SELECT car_model, COUNT(*) AS total
        FROM cars
        GROUP BY car_model
        ORDER BY total DESC
        LIMIT 5
    """, conn)
    st.bar_chart(df_models.set_index("car_model"))

    # -------- Country Distribution --------
    st.markdown("### 🌍 Country-wise Car Distribution")
    df_country = pd.read_sql("""
        SELECT country, COUNT(*) AS total
        FROM cars
        GROUP BY country
        ORDER BY total DESC
    """, conn)
    st.bar_chart(df_country.set_index("country"))

    # -------- Color Distribution --------
    st.markdown("### 🎨 Car Color Distribution")
    df_color = pd.read_sql("""
        SELECT car_color, COUNT(*) AS total
        FROM cars
        GROUP BY car_color
        ORDER BY total DESC
    """, conn)
    st.bar_chart(df_color.set_index("car_color"))

    # -------- Year Trend --------
    st.markdown("### 📈 Cars by Year of Manufacture")
    df_year = pd.read_sql("""
        SELECT year_of_manufacture, COUNT(*) AS total
        FROM cars
        GROUP BY year_of_manufacture
        ORDER BY year_of_manufacture
    """, conn)
    st.line_chart(df_year.set_index("year_of_manufacture"))

    # -------- Oldest & Newest --------
    st.markdown("### 🕰️ Oldest & Newest Cars")
    df_year_range = pd.read_sql("""
        SELECT 
            MIN(year_of_manufacture) AS oldest,
            MAX(year_of_manufacture) AS newest
        FROM cars
    """, conn)

    st.info(
        f"Oldest car year: **{df_year_range['oldest'][0]}** | "
        f"Newest car year: **{df_year_range['newest'][0]}**"
    )

    # -------- Credit Card Usage --------
    st.markdown("### 💳 Credit Card Usage by Brand")
    df_cards = pd.read_sql("""
        SELECT car_brand, credit_card_type, COUNT(*) AS total
        FROM cars
        GROUP BY car_brand, credit_card_type
        ORDER BY car_brand, total DESC
    """, conn)
    st.dataframe(df_cards)

# =================================================
# 🤖 CAR BRAND PREDICTION
# =================================================
if page == "Car Brand Prediction":

    # ---- Guard for deployment ----
    if model is None or label_encoders is None:
        st.warning(
            "⚠️ Trained ML model files are not available in this deployment.\n\n"
            "To enable predictions:\n"
            "1. Clone the repository locally\n"
            "2. Run `notebooks/analysis_and_model.ipynb`\n"
            "3. Generate the model files locally\n"
        )
        st.stop()

    st.subheader("🤖 Predict Car Brand")

    conn = get_connection()
    df = pd.read_sql("SELECT * FROM cars", conn)

    country = st.selectbox("Country", sorted(df["country"].unique()))
    car_model = st.selectbox("Car Model", sorted(df["car_model"].unique()))
    car_color = st.selectbox("Car Color", sorted(df["car_color"].unique()))
    year = st.number_input(
        "Year of Manufacture",
        min_value=int(df["year_of_manufacture"].min()),
        max_value=int(df["year_of_manufacture"].max())
    )
    credit_card = st.selectbox(
        "Credit Card Type",
        sorted(df["credit_card_type"].unique())
    )

    if st.button("Predict Brand"):
        input_data = pd.DataFrame([{
            "country": country,
            "car_model": car_model,
            "car_color": car_color,
            "year_of_manufacture": year,
            "credit_card_type": credit_card
        }])

        # Encode only categorical columns
        for col in input_data.columns:
            if col in label_encoders:
                input_data[col] = label_encoders[col].transform(input_data[col])

        prediction = model.predict(input_data)[0]
        predicted_brand = label_encoders["car_brand"].inverse_transform([prediction])[0]

        st.success(f"🚘 Predicted Car Brand: **{predicted_brand.upper()}**")
