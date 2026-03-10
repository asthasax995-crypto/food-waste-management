import streamlit as st
import plotly.express as px
from database import *

st.set_page_config(page_title="Food Waste Dashboard", layout="wide")

# ---------------------------
# LOAD DATA ONCE
# ---------------------------

@st.cache_data
def load_data():

    data = {}

    data["providers_city"] = providers_receivers_per_city()
    data["provider_food"] = provider_type_most_food()
    data["food_types"] = common_food_types()
    data["city_listings"] = city_highest_listings()
    data["donations"] = total_donation_provider()
    data["claim_status"] = claim_status_percentage()
    data["meal_claims"] = most_claimed_meal()
    data["receivers_top"] = receivers_most_food()

    data["total_food"] = total_food_quantity()

    return data

data = load_data()

# ---------------------------
# TITLE
# ---------------------------

st.title("🍲 Food Wastage Management Dashboard")

st.markdown("Smart analytics to reduce food waste and improve food distribution.")

st.divider()

# ---------------------------
# FILTERS (Power BI style)
# ---------------------------

st.sidebar.header("🔎 Filters")

city_filter = st.sidebar.selectbox(
    "Select City",
    ["All"] + list(data["providers_city"]["City"].unique())
)

food_filter = st.sidebar.selectbox(
    "Food Type",
    ["All"] + list(data["food_types"]["Food_Type"].unique())
)

# ---------------------------
# KPI CARDS
# ---------------------------

col1,col2,col3,col4 = st.columns(4)

total_food = int(data["total_food"].iloc[0][0])

providers = fetch_dataframe("SELECT COUNT(*) FROM providers").iloc[0][0]
receivers = fetch_dataframe("SELECT COUNT(*) FROM receivers").iloc[0][0]
claims = fetch_dataframe("SELECT COUNT(*) FROM claims").iloc[0][0]

col1.metric("🍛 Total Food", total_food)
col2.metric("🏪 Providers", providers)
col3.metric("🏢 Receivers", receivers)
col4.metric("📦 Claims", claims)

st.divider()

# ---------------------------
# CHART ROW 1
# ---------------------------

col1,col2 = st.columns(2)

with col1:

    st.subheader("Top Food Providers")

    fig = px.bar(
        data["donations"],
        x="Name",
        y="Total_Donated",
        color="Total_Donated"
    )

    st.plotly_chart(fig,use_container_width=True)


with col2:

    st.subheader("Food Listings by City")

    fig = px.bar(
        data["city_listings"],
        x="Location",
        y="Listings",
        color="Listings"
    )

    st.plotly_chart(fig,use_container_width=True)

st.divider()

# ---------------------------
# CHART ROW 2
# ---------------------------

col1,col2 = st.columns(2)

with col1:

    st.subheader("Food Type Distribution")

    fig = px.pie(
        data["food_types"],
        names="Food_Type",
        values="Count"
    )

    st.plotly_chart(fig,use_container_width=True)


with col2:

    st.subheader("Most Claimed Meal Type")

    fig = px.bar(
        data["meal_claims"],
        x="Meal_Type",
        y="Claims",
        color="Claims"
    )

    st.plotly_chart(fig,use_container_width=True)

st.divider()

# ---------------------------
# CLAIM STATUS
# ---------------------------

st.subheader("Claim Status Analysis")

fig = px.pie(
    data["claim_status"],
    names="Status",
    values="Percentage"
)

st.plotly_chart(fig,use_container_width=True)

st.divider()

# ---------------------------
# TOP RECEIVERS
# ---------------------------

st.subheader("Receivers Claiming Most Food")

fig = px.bar(
    data["receivers_top"],
    x="Name",
    y="Total_Claims",
    color="Total_Claims"
)

st.plotly_chart(fig,use_container_width=True)

st.divider()

# ---------------------------
# REPORT TABLES
# ---------------------------

st.header("📊 Analytical Reports")

reports = {
    "Providers & Receivers per City": data["providers_city"],
    "Provider Type Contribution": data["provider_food"],
    "Food Type Availability": data["food_types"],
    "City With Highest Listings": data["city_listings"],
    "Top Food Providers": data["donations"],
    "Claim Status": data["claim_status"],
    "Most Claimed Meal Type": data["meal_claims"],
    "Top Receivers": data["receivers_top"]
}

for title,df in reports.items():

    with st.expander(title):

        st.dataframe(df)