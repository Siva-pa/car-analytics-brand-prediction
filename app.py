import streamlit as st
import pandas as pd
import mysql.connector
import pickle
import os

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(
    page_title="Car Analytics & Brand Prediction",
    layout="wide"
)

st.title("🚗 Car Analytics & Brand Prediction System")

# =================================================
# DATABASE CONNECTION (LOCAL ONLY)
# =================================================
@st.cache_resource
def get_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="Siva",   # change if needed
            database="car_analytics"
        )
    except:
        return None

# =================================================
# LOAD DATA FALLBACK (FOR CLOUD)
# =================================================
@st.cache_data
def load_data_fallback():
    return pd.read_csv("data/cars_cleaned.csv")

# =================================================
# LOAD MODEL SAFELY
# =================================================
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

# =================================================
# SIDEBAR
# =================================================
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

    # ----- DATA SOURCE -----
    if conn is None:
        st.warning(
            "⚠️ MySQL database is not available in cloud deployment.\n\n"
            "Showing analytics using static dataset instead."
        )
        df = load_data_fallback()
    else:
        df = pd.read_sql("SELECT * FROM cars", conn)

    # ----- KPIs -----
    st.markdown("### 📌 Key Metrics")
    col1, col2, col3 = st.columns(3)

    col1.metric("Total Cars", len(df))
    col2.metric("Unique Brands", df["car_brand"].nunique())
    col3.metric("Countries Covered", df["country"].nunique())

    st.divider()

    # ----- Top Brands -----
    st.markdown("### 🚘 Top 5 Car Brands")
    top_brands = (
        df["car_brand"]
        .value_counts()
        .head(5)
        .reset_index()
    )
    top_brands.columns = ["car_brand", "total"]
    st.bar_chart(top_brands.set_index("car_brand"))

    # ----- Top Models -----
    st.markdown("### 🚗 Top 5 Car Models")
    top_models = (
        df["car_model"]
        .value_counts()
        .head(5)
        .reset_index()
    )
    top_models.columns = ["car_model", "total"]
    st.bar_chart(top_models.set_index("car_model"))

    # ----- Country Distribution -----
    st.markdown("### 🌍 Country-wise Car Distribution")
    country_dist = df["country"].value_counts().reset_index()
    country_dist.columns = ["country", "total"]
    st.bar_chart(country_dist.set_index("country"))

    # ----- Color Distribution -----
    st.markdown("### 🎨 Car Color Distribution")
    color_dist = df["car_color"].value_counts().reset_index()
    color_dist.columns = ["car_color", "total"]
    st.bar_chart(color_dist.set_index("car_color"))

    # ----- Year Trend -----
    st.markdown("### 📈 Cars by Year of Manufacture")
    year_dist = (
        df.groupby("year_of_manufacture")
        .size()
        .reset_index(name="total")
        .sort_values("year_of_manufacture")
    )
    st.line_chart(year_dist.set_index("year_of_manufacture"))

    # ----- Oldest & Newest -----
    st.markdown("### 🕰️ Oldest & Newest Cars")
    st.info(
        f"Oldest car year: **{df['year_of_manufacture'].min()}** | "
        f"Newest car year: **{df['year_of_manufacture'].max()}**"
    )

    # ----- Credit Card Usage -----
    st.markdown("### 💳 Credit Card Usage by Brand")
    cc_usage = (
        df.groupby(["car_brand", "credit_card_type"])
        .size()
        .reset_index(name="total")
        .sort_values(["car_brand", "total"], ascending=[True, False])
    )
    st.dataframe(cc_usage)

# =================================================
# 🤖 CAR BRAND PREDICTION
# =================================================
if page == "Car Brand Prediction":

    if model is None or label_encoders is None:
        st.warning(
            "⚠️ Trained ML model files are not available in this deployment.\n\n"
            "Run `notebooks/analysis_and_model.ipynb` locally to generate them."
        )
        st.stop()

    st.subheader("🤖 Predict Car Brand")

    df = load_data_fallback()

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

        for col in input_data.columns:
            if col in label_encoders:
                input_data[col] = label_encoders[col].transform(input_data[col])

        prediction = model.predict(input_data)[0]
        predicted_brand = label_encoders["car_brand"].inverse_transform([prediction])[0]

        st.success(f"🚘 Predicted Car Brand: **{predicted_brand.upper()}**")
