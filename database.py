import sqlite3
import pandas as pd

# Connect DB
def create_connection():
    return sqlite3.connect("food_waste.db")

# Load CSV → SQL
def load_data():
    conn = create_connection()

    pd.read_csv("clean_providers.csv").to_sql("providers", conn, if_exists="replace", index=False)
    pd.read_csv("clean_receivers.csv").to_sql("receivers", conn, if_exists="replace", index=False)
    pd.read_csv("clean_food_listings.csv").to_sql("food_listings", conn, if_exists="replace", index=False)
    pd.read_csv("clean_claims.csv").to_sql("claims", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()

# Run Query
def run_query(query):
    conn = create_connection()
    df = pd.read_sql(query, conn)
    conn.close()
    return df


# =========================
# BASIC QUERIES
# =========================

def q_total_food():
    return run_query("SELECT SUM(Quantity) AS Total_Food FROM food_listings")

def q_common_food_types():
    return run_query("""
    SELECT Food_Type, COUNT(*) AS Count
    FROM food_listings
    GROUP BY Food_Type
    ORDER BY Count DESC
    """)

def q_top_city():
    return run_query("""
    SELECT p.City, COUNT(*) AS Listings
    FROM food_listings f
    JOIN providers p ON f.Provider_ID = p.Provider_ID
    GROUP BY p.City
    ORDER BY Listings DESC
    """)

def q_claim_status():
    return run_query("""
    SELECT Status, COUNT(*) AS Count
    FROM claims
    GROUP BY Status
    """)
# 1. Providers & Receivers per City
def q1_providers_receivers_city():
    return run_query("""
    SELECT p.City,
           COUNT(DISTINCT p.Provider_ID) AS Providers,
           COUNT(DISTINCT r.Receiver_ID) AS Receivers
    FROM providers p
    LEFT JOIN receivers r ON p.City = r.City
    GROUP BY p.City
    """)

# 2. Top Provider Type
def q2_top_provider_type():
    return run_query("""
    SELECT Type, COUNT(*) AS Total
    FROM providers
    GROUP BY Type
    ORDER BY Total DESC
    """)

# 3. Provider Contacts
def q3_provider_contacts():
    return run_query("""
    SELECT Name, City, Contact
    FROM providers
    """)

# 4. Top Receivers
def q4_top_receivers():
    return run_query("""
    SELECT Receiver_ID, COUNT(*) AS Total_Claims
    FROM claims
    GROUP BY Receiver_ID
    ORDER BY Total_Claims DESC
    """)

# 5. Total Food
def q5_total_food():
    return run_query("""
    SELECT SUM(Quantity) AS Total_Food
    FROM food_listings
    """)

# 6. City with Most Listings
def q6_top_city():
    return run_query("""
    SELECT p.City, COUNT(*) AS Listings
    FROM food_listings f
    JOIN providers p ON f.Provider_ID = p.Provider_ID
    GROUP BY p.City
    ORDER BY Listings DESC
    """)

# 7. Common Food Types
def q7_food_types():
    return run_query("""
    SELECT Food_Type, COUNT(*) AS Count
    FROM food_listings
    GROUP BY Food_Type
    ORDER BY Count DESC
    """)

# 8. Claims per Food
def q8_claims_per_food():
    return run_query("""
    SELECT Food_ID, COUNT(*) AS Claims
    FROM claims
    GROUP BY Food_ID
    """)

# 9. Top Provider (Successful)
def q9_top_provider_success():
    return run_query("""
    SELECT f.Provider_ID, COUNT(*) AS Success
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    WHERE c.Status='Completed'
    GROUP BY f.Provider_ID
    ORDER BY Success DESC
    """)

# 10. Claim Status %
def q10_claim_status():
    return run_query("""
    SELECT Status,
           COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS Percentage
    FROM claims
    GROUP BY Status
    """)

# 11. Avg Food per Receiver
def q11_avg_food_receiver():
    return run_query("""
    SELECT c.Receiver_ID, AVG(f.Quantity) AS Avg_Qty
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    GROUP BY c.Receiver_ID
    """)

# 12. Most Claimed Meal Type
def q12_top_meal():
    return run_query("""
    SELECT f.Meal_Type, COUNT(*) AS Count
    FROM claims c
    JOIN food_listings f ON c.Food_ID = f.Food_ID
    GROUP BY f.Meal_Type
    ORDER BY Count DESC
    """)

# 13. Food per Provider
def q13_food_per_provider():
    return run_query("""
    SELECT Provider_ID, SUM(Quantity) AS Total
    FROM food_listings
    GROUP BY Provider_ID
    """)

# 14. Near Expiry
def q14_near_expiry():
    return run_query("""
    SELECT * FROM food_listings
    WHERE Expiry_Date <= DATE('now','+2 day')
    """)

# 15. Expired Food
def q15_expired():
    return run_query("""
    SELECT * FROM food_listings
    WHERE Expiry_Date < DATE('now')
    """)