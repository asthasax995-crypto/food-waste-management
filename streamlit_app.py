import streamlit as st
import database as db
import matplotlib.pyplot as plt

st.set_page_config(page_title="Food Waste Dashboard", layout="wide")

# =========================
# 🎨 CUSTOM CSS
# =========================
st.markdown("""
<style>
body {
    background-color: #f5f7fa;
}
.header {
    padding: 20px;
    border-radius: 15px;
    background: linear-gradient(90deg, #4CAF50, #2E7D32);
    color: white;
    text-align: center;
    font-size: 28px;
    font-weight: bold;
}
.card {
    padding: 20px;
    border-radius: 12px;
    background-color: white;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================
# 🌟 HEADER
# =========================
st.markdown('<div class="header">🍱 Food Waste Management System</div>', unsafe_allow_html=True)

# =========================
# LOAD DATA
# =========================
if st.button("🔄 Load Data"):
    db.load_data()
    st.success("Data Loaded Successfully!")

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("🔍 Filters")

city = st.sidebar.text_input("City")
food_type = st.sidebar.selectbox("Food Type", ["All", "veg", "non-veg"])
meal_type = st.sidebar.selectbox("Meal Type", ["All", "breakfast", "lunch", "dinner"])

query = "SELECT * FROM food_listings WHERE 1=1"

if food_type != "All":
    query += f" AND Food_Type='{food_type}'"

if meal_type != "All":
    query += f" AND Meal_Type='{meal_type}'"

if city:
    query += f"""
    AND Provider_ID IN (
        SELECT Provider_ID FROM providers WHERE City LIKE '%{city}%'
    )
    """

data = db.run_query(query)

# =========================
# 📊 TABS
# =========================
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📈 Analysis", "📞 Contacts"])

# =========================
# DASHBOARD
# =========================
with tab1:
    st.subheader("📊 Overview")

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"<div class='card'><h2>{len(data)}</h2><p>Total Items</p></div>", unsafe_allow_html=True)
    col2.markdown(f"<div class='card'><h2>{int(data['Quantity'].sum()) if not data.empty else 0}</h2><p>Total Quantity</p></div>", unsafe_allow_html=True)
    col3.markdown(f"<div class='card'><h2>{data['Provider_ID'].nunique() if not data.empty else 0}</h2><p>Providers</p></div>", unsafe_allow_html=True)

    st.subheader("📋 Food Listings")
    st.dataframe(data, use_container_width=True)

# =========================
# ANALYSIS
# =========================
with tab2:
    st.subheader("📈 Insights")

    option = st.selectbox("Choose Analysis", [
        "Food Types",
        "Top Cities",
        "Claim Status"
    ])

    if option == "Food Types":
        df = db.q7_food_types()
        fig, ax = plt.subplots()
        ax.bar(df["Food_Type"], df["Count"])
        ax.set_title("Food Type Distribution")
        st.pyplot(fig)

    elif option == "Top Cities":
        df = db.q6_top_city()
        fig, ax = plt.subplots()
        ax.bar(df["City"], df["Listings"])
        ax.set_title("Top Cities")
        st.pyplot(fig)

    elif option == "Claim Status":
        df = db.q10_claim_status()
        fig, ax = plt.subplots()
        ax.pie(df["Percentage"], labels=df["Status"], autopct="%1.1f%%")
        st.pyplot(fig)

# =========================
# CONTACTS
# =========================
with tab3:
    st.subheader("📞 Provider Contacts")

    contacts = db.q3_provider_contacts()
    st.dataframe(contacts, use_container_width=True)

# =========================
# REPORTS SECTION
# =========================
st.markdown("### 📊 SQL Reports + Visualization")

queries = {
    "Food Types": db.q7_food_types,
    "Top City": db.q6_top_city,
    "Claim Status %": db.q10_claim_status,
    "Top Provider Type": db.q2_top_provider_type
}

# SQL text mapping
query_texts = {
    "Food Types": """
SELECT Food_Type, COUNT(*) AS Count
FROM food_listings
GROUP BY Food_Type
ORDER BY Count DESC
""",

    "Top City": """
SELECT p.City, COUNT(*) AS Listings
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
GROUP BY p.City
ORDER BY Listings DESC
""",

    "Claim Status %": """
SELECT Status,
COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims) AS Percentage
FROM claims
GROUP BY Status
""",

    "Top Provider Type": """
SELECT Type, COUNT(*) AS Total
FROM providers
GROUP BY Type
ORDER BY Total DESC
"""
}

choice = st.selectbox("Select Report", list(queries.keys()))

# =========================
# SHOW SQL QUERY
# =========================
st.subheader("🧠 SQL Query")
st.code(query_texts[choice], language="sql")

# =========================
# RUN QUERY
# =========================
df = queries[choice]()
st.subheader("📋 Result")
st.dataframe(df, use_container_width=True)

# =========================
# SHOW CHART
# =========================
st.subheader("📈 Visualization")

fig, ax = plt.subplots()

if choice == "Food Types":
    ax.bar(df["Food_Type"], df["Count"])

elif choice == "Top City":
    ax.bar(df["City"], df["Listings"])

elif choice == "Claim Status %":
    ax.pie(df["Percentage"], labels=df["Status"], autopct="%1.1f%%")

elif choice == "Top Provider Type":
    ax.bar(df["Type"], df["Total"])

st.pyplot(fig)