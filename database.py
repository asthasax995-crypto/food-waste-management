import sqlite3
import pandas as pd

DB_NAME = "food_waste.db"

# ------------------------------------------------
# Database Connection
# ------------------------------------------------

def get_connection():
    return sqlite3.connect(DB_NAME)


# ------------------------------------------------
# Helper to return dataframe
# ------------------------------------------------

def fetch_dataframe(query, params=None):

    conn = get_connection()

    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)

    conn.close()
    return df


# ------------------------------------------------
# Create Tables
# ------------------------------------------------

def create_all_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS providers(
        Provider_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Type TEXT,
        Address TEXT,
        City TEXT,
        Contact TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS receivers(
        Receiver_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT,
        Type TEXT,
        City TEXT,
        Contact TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS food_listings(
        Food_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Food_Name TEXT,
        Quantity INTEGER,
        Expiry_Date DATE,
        Provider_ID INTEGER,
        Provider_Type TEXT,
        Location TEXT,
        Food_Type TEXT,
        Meal_Type TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS claims(
        Claim_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Food_ID INTEGER,
        Receiver_ID INTEGER,
        Status TEXT,
        Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# ------------------------------------------------
# CRUD Providers
# ------------------------------------------------

def add_provider(name,ptype,address,city,contact):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO providers(Name,Type,Address,City,Contact)
    VALUES(?,?,?,?,?)
    """,(name,ptype,address,city,contact))

    conn.commit()
    conn.close()


def update_provider(pid,name,ptype,address,city,contact):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE providers
    SET Name=?,Type=?,Address=?,City=?,Contact=?
    WHERE Provider_ID=?
    """,(name,ptype,address,city,contact,pid))

    conn.commit()
    conn.close()


def delete_provider(pid):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM providers WHERE Provider_ID=?",(pid,))

    conn.commit()
    conn.close()


# ------------------------------------------------
# CRUD Receivers
# ------------------------------------------------

def add_receiver(name,rtype,city,contact):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO receivers(Name,Type,City,Contact)
    VALUES(?,?,?,?)
    """,(name,rtype,city,contact))

    conn.commit()
    conn.close()


def update_receiver(rid,name,rtype,city,contact):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE receivers
    SET Name=?,Type=?,City=?,Contact=?
    WHERE Receiver_ID=?
    """,(name,rtype,city,contact,rid))

    conn.commit()
    conn.close()


def delete_receiver(rid):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM receivers WHERE Receiver_ID=?",(rid,))

    conn.commit()
    conn.close()


# ------------------------------------------------
# CRUD Food Listings
# ------------------------------------------------

def add_food_listing(fname,qty,expiry,provider,ptype,location,food_type,meal_type):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO food_listings
    (Food_Name,Quantity,Expiry_Date,Provider_ID,Provider_Type,Location,Food_Type,Meal_Type)
    VALUES(?,?,?,?,?,?,?,?)
    """,(fname,qty,expiry,provider,ptype,location,food_type,meal_type))

    conn.commit()
    conn.close()


def update_food_listing(fid,fname,qty,expiry,provider,ptype,location,food_type,meal_type):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE food_listings
    SET Food_Name=?,Quantity=?,Expiry_Date=?,Provider_ID=?,Provider_Type=?,Location=?,Food_Type=?,Meal_Type=?
    WHERE Food_ID=?
    """,(fname,qty,expiry,provider,ptype,location,food_type,meal_type,fid))

    conn.commit()
    conn.close()


def delete_food_listing(fid):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM food_listings WHERE Food_ID=?",(fid,))

    conn.commit()
    conn.close()


# ------------------------------------------------
# CRUD Claims
# ------------------------------------------------

def add_claim(food_id,receiver_id,status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO claims(Food_ID,Receiver_ID,Status)
    VALUES(?,?,?)
    """,(food_id,receiver_id,status))

    conn.commit()
    conn.close()


def update_claim(cid,food_id,receiver_id,status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE claims
    SET Food_ID=?,Receiver_ID=?,Status=?
    WHERE Claim_ID=?
    """,(food_id,receiver_id,status,cid))

    conn.commit()
    conn.close()


def delete_claim(cid):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM claims WHERE Claim_ID=?",(cid,))

    conn.commit()
    conn.close()


# ------------------------------------------------
# REPORT QUERIES (13)
# ------------------------------------------------

def providers_receivers_per_city():

    return fetch_dataframe("""
    SELECT City,
    COUNT(DISTINCT Provider_ID) as Providers,
    COUNT(DISTINCT Receiver_ID) as Receivers
    FROM providers
    LEFT JOIN receivers USING(City)
    GROUP BY City
    """)


def provider_type_most_food():

    return fetch_dataframe("""
    SELECT Provider_Type,SUM(Quantity) as Total_Food
    FROM food_listings
    GROUP BY Provider_Type
    ORDER BY Total_Food DESC
    """)


def provider_contacts_city():

    return fetch_dataframe("""
    SELECT Name,Contact,City
    FROM providers
    """)


def receivers_most_food():

    return fetch_dataframe("""
    SELECT r.Name,COUNT(c.Claim_ID) as Total_Claims
    FROM claims c
    JOIN receivers r ON c.Receiver_ID=r.Receiver_ID
    GROUP BY r.Name
    ORDER BY Total_Claims DESC
    """)


def total_food_quantity():

    return fetch_dataframe("""
    SELECT SUM(Quantity) as Total_Food
    FROM food_listings
    """)


def city_highest_listings():

    return fetch_dataframe("""
    SELECT Location,COUNT(*) as Listings
    FROM food_listings
    GROUP BY Location
    ORDER BY Listings DESC
    """)


def common_food_types():

    return fetch_dataframe("""
    SELECT Food_Type,COUNT(*) as Count
    FROM food_listings
    GROUP BY Food_Type
    ORDER BY Count DESC
    """)


def claims_per_food():

    return fetch_dataframe("""
    SELECT Food_ID,COUNT(*) as Total_Claims
    FROM claims
    GROUP BY Food_ID
    """)


def provider_success_claims():

    return fetch_dataframe("""
    SELECT p.Name,COUNT(c.Claim_ID) as Successful_Claims
    FROM claims c
    JOIN food_listings f ON c.Food_ID=f.Food_ID
    JOIN providers p ON f.Provider_ID=p.Provider_ID
    WHERE c.Status='Completed'
    GROUP BY p.Name
    ORDER BY Successful_Claims DESC
    """)


def claim_status_percentage():

    return fetch_dataframe("""
    SELECT Status,
    COUNT(*)*100.0/(SELECT COUNT(*) FROM claims) as Percentage
    FROM claims
    GROUP BY Status
    """)


def avg_food_per_receiver():

    return fetch_dataframe("""
    SELECT r.Name,AVG(f.Quantity) as Avg_Food
    FROM claims c
    JOIN receivers r ON c.Receiver_ID=r.Receiver_ID
    JOIN food_listings f ON c.Food_ID=f.Food_ID
    GROUP BY r.Name
    """)


def most_claimed_meal():

    return fetch_dataframe("""
    SELECT Meal_Type,COUNT(*) as Claims
    FROM claims c
    JOIN food_listings f ON c.Food_ID=f.Food_ID
    GROUP BY Meal_Type
    ORDER BY Claims DESC
    """)


def total_donation_provider():

    return fetch_dataframe("""
    SELECT p.Name,SUM(f.Quantity) as Total_Donated
    FROM food_listings f
    JOIN providers p ON f.Provider_ID=p.Provider_ID
    GROUP BY p.Name
    ORDER BY Total_Donated DESC
    """)