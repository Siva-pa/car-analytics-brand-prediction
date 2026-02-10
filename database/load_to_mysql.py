import pandas as pd
import mysql.connector

# Load cleaned data
df = pd.read_csv(r"C:\Users\aruns\OneDrive\Desktop\Projects\car_analytics_project\notebooks\cars_cleaned.csv")

# MySQL connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Siva",
    database="car_analytics"
)

cursor = conn.cursor()

# Insert data row by row
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO cars
        (country, car_brand, car_model, car_color,
         year_of_manufacture, credit_card_type)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, tuple(row))

conn.commit()
cursor.close()
conn.close()

print("✅ Data loaded into MySQL successfully")
