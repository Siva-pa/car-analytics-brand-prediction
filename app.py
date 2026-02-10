import streamlit as st
import pandas as pd
import mysql.connector
import pickle

# ------------------ PAGE CONFIG ------------------
st.set_page_config(
    page_title="Car Analytics & Prediction",
    layout="wide"
)

st.title("🚗 Car Analytics & Brand Prediction System")

# ------------------ DB CONNECTION ------------------
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Siva",
        database="car_analytics"
    )

# ------------------ LOAD MODEL ------------------
@st.cache_resource
def load_model():
    model = pickle.load(open("model/car_brand_model.pkl", "rb"))
    encoders = pickle.load(open("model/label_encoders.pkl", "rb"))
    return model, encoders

model, label_encoders = load_model()

# ------------------ SIDEBAR ------------------
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
    query = """
    SELECT car_brand, COUNT(*) AS total
    FROM cars
    GROUP BY car_brand
    ORDER BY total DESC
    LIMIT 5
    """
    df_brands = pd.read_sql(query, conn)
    st.bar_chart(df_brands.set_index("car_brand"))

    # -------- Top Models --------
    st.markdown("### 🚗 Top 5 Car Models")
    query = """
    SELECT car_model, COUNT(*) AS total
    FROM cars
    GROUP BY car_model
    ORDER BY total DESC
    LIMIT 5
    """
    df_models = pd.read_sql(query, conn)
    st.bar_chart(df_models.set_index("car_model"))

    # -------- Country Distribution --------
    st.markdown("### 🌍 Country-wise Car Distribution")
    query = """
    SELECT country, COUNT(*) AS total
    FROM cars
    GROUP BY country
    ORDER BY total DESC
    """
    df_country = pd.read_sql(query, conn)
    st.bar_chart(df_country.set_index("country"))

    # -------- Car Color Distribution --------
    st.markdown("### 🎨 Car Color Distribution")
    query = """
    SELECT car_color, COUNT(*) AS total
    FROM cars
    GROUP BY car_color
    ORDER BY total DESC
    """
    df_color = pd.read_sql(query, conn)
    st.bar_chart(df_color.set_index("car_color"))

    # -------- Year-wise Trend --------
    st.markdown("### 📈 Cars by Year of Manufacture")
    query = """
    SELECT year_of_manufacture, COUNT(*) AS total
    FROM cars
    GROUP BY year_of_manufacture
    ORDER BY year_of_manufacture
    """
    df_year = pd.read_sql(query, conn)
    st.line_chart(df_year.set_index("year_of_manufacture"))

    # -------- Oldest & Newest --------
    st.markdown("### 🕰️ Oldest & Newest Cars")
    query = """
    SELECT 
        MIN(year_of_manufacture) AS oldest,
        MAX(year_of_manufacture) AS newest
    FROM cars
    """
    df_year_range = pd.read_sql(query, conn)

    st.info(
        f"Oldest car year: **{df_year_range['oldest'][0]}** | "
        f"Newest car year: **{df_year_range['newest'][0]}**"
    )

    # -------- Credit Card Usage --------
    st.markdown("### 💳 Credit Card Usage by Brand")
    query = """
    SELECT car_brand, credit_card_type, COUNT(*) AS total
    FROM cars
    GROUP BY car_brand, credit_card_type
    ORDER BY car_brand, total DESC
    """
    df_cards = pd.read_sql(query, conn)
    st.dataframe(df_cards)

# =================================================
# 🤖 CAR BRAND PREDICTION
# =================================================
if page == "Car Brand Prediction":
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

        for col in input_data.columns:
            if col in label_encoders:  # encode only categorical
                input_data[col] = label_encoders[col].transform(input_data[col])

        prediction = model.predict(input_data)[0]
        predicted_brand = label_encoders["car_brand"].inverse_transform([prediction])[0]

        st.success(f"🚘 Predicted Car Brand: **{predicted_brand.upper()}**")
