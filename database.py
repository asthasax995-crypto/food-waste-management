import sqlite3
import pandas as pd

DB_NAME = "food_waste.db"

def get_connection():
    return sqlite3.connect(DB_NAME)
def create_all_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Define your tables with proper schema here
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers (
        Provider_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Type TEXT,
        Address TEXT,
        City TEXT,
        Contact TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receivers (
        Receiver_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Type TEXT,
        City TEXT,
        Contact TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Food_Name TEXT,
        Quantity INTEGER,
        Expiry_Date TEXT,
        Provider_ID INTEGER,
        Provider_Type TEXT,
        Location TEXT,
        Food_Type TEXT,
        Meal_Type TEXT,
        FOREIGN KEY(Provider_ID) REFERENCES providers(Provider_ID)
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims (
        Claim_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Food_ID INTEGER,
        Receiver_ID INTEGER,
        Status TEXT,
        Timestamp TEXT,
        FOREIGN KEY(Food_ID) REFERENCES food_listings(Food_ID),
        FOREIGN KEY(Receiver_ID) REFERENCES receivers(Receiver_ID)
    )
    """)
    conn.commit()
    conn.close()

def clear_table(table_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name}")
    conn.commit()
    conn.close()

def insert_dataframe(df, table_name):
    conn = sqlite3.connect(DB_NAME)
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()

def fetch_dataframe(query, params=None):
    conn = sqlite3.connect(DB_NAME)
    try:
        if params:
            df = pd.read_sql_query(query, conn, params=params)
        else:
            df = pd.read_sql_query(query, conn)
    finally:
        conn.close()
    return df

def execute_query(query, params=None):
    conn = get_connection()
    c = conn.cursor()
    if params:
        c.execute(query, params)
    else:
        c.execute(query)
    conn.commit()
    conn.close()

# CRUD Providers
def add_provider(name, ptype, address, city, contact):
    execute_query(
        "INSERT INTO providers (Name, Type, Address, City, Contact) VALUES (?, ?, ?, ?, ?)",
        (name, ptype, address, city, contact)
    )

def update_provider(pid, name, ptype, address, city, contact):
    execute_query(
        "UPDATE providers SET Name=?, Type=?, Address=?, City=?, Contact=? WHERE Provider_ID=?",
        (name, ptype, address, city, contact, pid)
    )

def delete_provider(pid):
    execute_query("DELETE FROM providers WHERE Provider_ID=?", (pid,))

# CRUD Receivers
def add_receiver(name, rtype, city, contact):
    execute_query(
        "INSERT INTO receivers (Name, Type, City, Contact) VALUES (?, ?, ?, ?)",
        (name, rtype, city, contact)
    )

def update_receiver(rid, name, rtype, city, contact):
    execute_query(
        "UPDATE receivers SET Name=?, Type=?, City=?, Contact=? WHERE Receiver_ID=?",
        (name, rtype, city, contact, rid)
    )

def delete_receiver(rid):
    execute_query("DELETE FROM receivers WHERE Receiver_ID=?", (rid,))

# CRUD Food Listings
def add_food_listing(food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type):
    if hasattr(expiry_date, 'strftime'):
        expiry_date = expiry_date.strftime('%Y-%m-%d')
    execute_query(
        """INSERT INTO food_listings 
        (Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
    )

def update_food_listing(fid, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type):
    if hasattr(expiry_date, 'strftime'):
        expiry_date = expiry_date.strftime('%Y-%m-%d')
    execute_query(
        """UPDATE food_listings SET Food_Name=?, Quantity=?, Expiry_Date=?, Provider_ID=?, Provider_Type=?, Location=?, Food_Type=?, Meal_Type=? 
        WHERE Food_ID=?""",
        (food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type, fid)
    )

def delete_food_listing(fid):
    execute_query("DELETE FROM food_listings WHERE Food_ID=?", (fid,))

# CRUD Claims
def add_claim(food_id, receiver_id, status, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif hasattr(timestamp, 'strftime'):
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    execute_query(
        "INSERT INTO claims (Food_ID, Receiver_ID, Status, Timestamp) VALUES (?, ?, ?, ?)",
        (food_id, receiver_id, status, timestamp)
    )

def update_claim(claim_id, food_id, receiver_id, status, timestamp=None):
    if timestamp is None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    elif hasattr(timestamp, 'strftime'):
        timestamp = timestamp.strftime('%Y-%m-%d %H:%M:%S')
    execute_query(
        "UPDATE claims SET Food_ID=?, Receiver_ID=?, Status=?, Timestamp=? WHERE Claim_ID=?",
        (food_id, receiver_id, status, timestamp, claim_id)
    )

def delete_claim(claim_id):
    execute_query("DELETE FROM claims WHERE Claim_ID=?", (claim_id,))

def clear_table(table_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"DELETE FROM {table_name}")
    conn.commit()
    conn.close()


# Report Query Functions

def get_providers_per_city():
    return fetch_dataframe("SELECT City, COUNT(*) as Provider_Count FROM providers GROUP BY City")

def get_receivers_per_city():
    return fetch_dataframe("SELECT City, COUNT(*) as Receiver_Count FROM receivers GROUP BY City")

def get_provider_contacts_by_city(city):
    return fetch_dataframe("SELECT Name, Contact FROM providers WHERE City = ?", [city])

def get_food_quantity_by_type():
    return fetch_dataframe("SELECT Food_Type, SUM(Quantity) as Total_Quantity FROM food_listings GROUP BY Food_Type")

def get_expiring_soon_food(days=3):
    return fetch_dataframe(f"""
        SELECT Food_Name, Expiry_Date FROM food_listings 
        WHERE DATE(Expiry_Date) <= DATE('now', '+{days} days')
        ORDER BY Expiry_Date
    """)

def get_claim_status_distribution():
    return fetch_dataframe("SELECT Status, COUNT(*) as Count FROM claims GROUP BY Status")

def get_provider_donations_count():
    return fetch_dataframe("""
        SELECT p.Name, COUNT(fl.Food_ID) as Donations
        FROM providers p
        JOIN food_listings fl ON p.Provider_ID = fl.Provider_ID
        GROUP BY p.Name
    """)

def get_receiver_claims_count():
    return fetch_dataframe("""
        SELECT r.Name, COUNT(c.Claim_ID) as Claims
        FROM receivers r
        JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        GROUP BY r.Name
    """)

def get_foods_by_location():
    return fetch_dataframe("""
        SELECT Location, COUNT(*) as Food_Count 
        FROM food_listings GROUP BY Location
    """)

def get_meal_type_distribution():
    return fetch_dataframe("SELECT Meal_Type, COUNT(*) as Count FROM food_listings GROUP BY Meal_Type")

def get_food_listing_by_provider(provider_name):
    return fetch_dataframe("""
        SELECT Food_Name, Quantity, Expiry_Date 
        FROM food_listings fl
        JOIN providers p ON fl.Provider_ID = p.Provider_ID
        WHERE p.Name = ?
    """, [provider_name])

def get_food_claim_history(food_id):
    return fetch_dataframe("""
        SELECT c.Claim_ID, r.Name AS Receiver, c.Status, c.Timestamp
        FROM claims c
        JOIN receivers r ON c.Receiver_ID = r.Receiver_ID
        WHERE c.Food_ID = ?
    """, [food_id])

def get_total_donations_over_time():
    return fetch_dataframe("""
        SELECT DATE(Timestamp) as Date, COUNT(*) as Total_Claims
        FROM claims
        GROUP BY DATE(Timestamp)
        ORDER BY Date
    """)

def get_avg_food_quantity_by_meal_type():
    return fetch_dataframe("""
        SELECT Meal_Type, AVG(Quantity) as Avg_Quantity
        FROM food_listings
        GROUP BY Meal_Type
    """)

def get_top_receivers(limit=5):
    return fetch_dataframe(f"""
        SELECT r.Name, COUNT(c.Claim_ID) as Total_Claims
        FROM receivers r
        JOIN claims c ON r.Receiver_ID = c.Receiver_ID
        GROUP BY r.Name
        ORDER BY Total_Claims DESC
        LIMIT {limit}
    """)

