import streamlit as st
from database import (
    create_all_tables,
    fetch_dataframe,
    add_provider, update_provider, delete_provider,
    add_receiver, update_receiver, delete_receiver,
    add_food_listing, update_food_listing, delete_food_listing,
    add_claim, update_claim, delete_claim,
    # Report functions:
    get_providers_per_city,
    get_receivers_per_city,
    get_provider_contacts_by_city,
    get_food_quantity_by_type,
    get_expiring_soon_food,
    get_claim_status_distribution,
    get_provider_donations_count,
    get_receiver_claims_count,
    get_foods_by_location,
    get_meal_type_distribution,
    get_food_listing_by_provider,
    get_food_claim_history,
    get_total_donations_over_time,
    get_avg_food_quantity_by_meal_type,
    get_top_receivers,
)
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="Food Wastage Management", layout="wide")

create_all_tables()

def dashboard():
    st.title("Food Donations Dashboard & Filters")

    # Filters
    locs = fetch_dataframe("SELECT DISTINCT Location FROM food_listings")["Location"].dropna().tolist()
    location = st.selectbox("Select Location", options=["All"] + locs)

    providers = fetch_dataframe("SELECT DISTINCT Name FROM providers")["Name"].tolist()
    provider = st.selectbox("Select Provider", options=["All"] + providers)

    food_types = fetch_dataframe("SELECT DISTINCT Food_Type FROM food_listings")["Food_Type"].dropna().tolist()
    food_type = st.selectbox("Select Food Type", options=["All"] + food_types)

    query = """
        SELECT fl.Food_ID, fl.Food_Name, fl.Quantity, fl.Expiry_Date,
               p.Name as Provider_Name, p.Contact as Provider_Contact,
               fl.Location, fl.Food_Type, fl.Meal_Type
        FROM food_listings fl
        JOIN providers p ON fl.Provider_ID = p.Provider_ID
        WHERE 1=1
    """
    params = []

    if location != "All":
        query += " AND fl.Location = ?"
        params.append(location)
    if provider != "All":
        query += " AND p.Name = ?"
        params.append(provider)
    if food_type != "All":
        query += " AND fl.Food_Type = ?"
        params.append(food_type)

    df = fetch_dataframe(query, params)
    st.write(f"Showing {len(df)} food listings")
    st.dataframe(df)

def manage_providers():
    st.title("Manage Providers")
    df = fetch_dataframe("SELECT * FROM providers")
    st.dataframe(df)

    st.subheader("Add Provider")
    with st.form("add_provider"):
        name = st.text_input("Name")
        ptype = st.text_input("Type")
        address = st.text_input("Address")
        city = st.text_input("City")
        contact = st.text_input("Contact")
        submitted = st.form_submit_button("Add")
        if submitted:
            add_provider(name, ptype, address, city, contact)
            st.success("Provider added")
            st.experimental_rerun()

    st.subheader("Update/Delete Provider")
    provider_ids = df["Provider_ID"].tolist()
    selected = st.selectbox("Select Provider ID", provider_ids)
    if selected:
        provider = df[df["Provider_ID"] == selected].iloc[0]
        with st.form("update_provider"):
            name = st.text_input("Name", value=provider["Name"])
            ptype = st.text_input("Type", value=provider["Type"])
            address = st.text_input("Address", value=provider["Address"])
            city = st.text_input("City", value=provider["City"])
            contact = st.text_input("Contact", value=provider["Contact"])
            update_submitted = st.form_submit_button("Update")
            if update_submitted:
                update_provider(selected, name, ptype, address, city, contact)
                st.success("Provider updated")
                st.experimental_rerun()
        if st.button("Delete Provider"):
            delete_provider(selected)
            st.success("Provider deleted")
            st.experimental_rerun()

def manage_receivers():
    st.title("Manage Receivers")
    df = fetch_dataframe("SELECT * FROM receivers")
    st.dataframe(df)

    st.subheader("Add Receiver")
    with st.form("add_receiver"):
        name = st.text_input("Name")
        rtype = st.text_input("Type")
        city = st.text_input("City")
        contact = st.text_input("Contact")
        submitted = st.form_submit_button("Add")
        if submitted:
            add_receiver(name, rtype, city, contact)
            st.success("Receiver added")
            st.experimental_rerun()

    st.subheader("Update/Delete Receiver")
    receiver_ids = df["Receiver_ID"].tolist()
    selected = st.selectbox("Select Receiver ID", receiver_ids)
    if selected:
        receiver = df[df["Receiver_ID"] == selected].iloc[0]
        with st.form("update_receiver"):
            name = st.text_input("Name", value=receiver["Name"])
            rtype = st.text_input("Type", value=receiver["Type"])
            city = st.text_input("City", value=receiver["City"])
            contact = st.text_input("Contact", value=receiver["Contact"])
            update_submitted = st.form_submit_button("Update")
            if update_submitted:
                update_receiver(selected, name, rtype, city, contact)
                st.success("Receiver updated")
                st.experimental_rerun()
        if st.button("Delete Receiver"):
            delete_receiver(selected)
            st.success("Receiver deleted")
            st.experimental_rerun()

def manage_food_listings():
    st.title("Manage Food Listings")
    df = fetch_dataframe("""
        SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Provider_ID, Provider_Type, Location, Food_Type, Meal_Type 
        FROM food_listings
    """)
    st.dataframe(df)

    st.subheader("Add Food Listing")
    with st.form("add_food"):
        food_name = st.text_input("Food Name")
        quantity = st.number_input("Quantity", min_value=1)
        expiry_date = st.date_input("Expiry Date")
        provider_id = st.number_input("Provider ID", min_value=1)
        provider_type = st.text_input("Provider Type")
        location = st.text_input("Location")
        food_type = st.text_input("Food Type")
        meal_type = st.text_input("Meal Type")
        submitted = st.form_submit_button("Add")
        if submitted:
            add_food_listing(food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
            st.success("Food listing added")
            st.experimental_rerun()

    st.subheader("Update/Delete Food Listing")
    food_ids = df["Food_ID"].tolist()
    selected = st.selectbox("Select Food ID", food_ids)
    if selected:
        food = df[df["Food_ID"] == selected].iloc[0]
        with st.form("update_food"):
            food_name = st.text_input("Food Name", value=food["Food_Name"])
            quantity = st.number_input("Quantity", min_value=1, value=food["Quantity"])
            expiry_date = st.date_input("Expiry Date", value=pd.to_datetime(food["Expiry_Date"]))
            provider_id = st.number_input("Provider ID", min_value=1, value=food["Provider_ID"])
            provider_type = st.text_input("Provider Type", value=food["Provider_Type"])
            location = st.text_input("Location", value=food["Location"])
            food_type = st.text_input("Food Type", value=food["Food_Type"])
            meal_type = st.text_input("Meal Type", value=food["Meal_Type"])
            update_submitted = st.form_submit_button("Update")
            if update_submitted:
                update_food_listing(selected, food_name, quantity, expiry_date, provider_id, provider_type, location, food_type, meal_type)
                st.success("Food listing updated")
                st.experimental_rerun()
        if st.button("Delete Food Listing"):
            delete_food_listing(selected)
            st.success("Food listing deleted")
            st.experimental_rerun()

def manage_claims():
    st.title("Manage Claims")
    df = fetch_dataframe("""
        SELECT Claim_ID, Food_ID, Receiver_ID, Status, Timestamp FROM claims
    """)
    st.dataframe(df)

    st.subheader("Add Claim")
    with st.form("add_claim"):
        food_id = st.number_input("Food ID", min_value=1)
        receiver_id = st.number_input("Receiver ID", min_value=1)
        status = st.selectbox("Status", ["Pending", "Approved", "Rejected"])
        submitted = st.form_submit_button("Add")
        if submitted:
            add_claim(food_id, receiver_id, status)
            st.success("Claim added")
            st.experimental_rerun()

    st.subheader("Update/Delete Claim")
    claim_ids = df["Claim_ID"].tolist()
    selected = st.selectbox("Select Claim ID", claim_ids)
    if selected:
        claim = df[df["Claim_ID"] == selected].iloc[0]
        with st.form("update_claim"):
            food_id = st.number_input("Food ID", min_value=1, value=claim["Food_ID"])
            receiver_id = st.number_input("Receiver ID", min_value=1, value=claim["Receiver_ID"])
            status = st.selectbox("Status", ["Pending", "Approved", "Rejected"], index=["Pending", "Approved", "Rejected"].index(claim["Status"]))
            update_submitted = st.form_submit_button("Update")
            if update_submitted:
                update_claim(selected, food_id, receiver_id, status)
                st.success("Claim updated")
                st.experimental_rerun()
        if st.button("Delete Claim"):
            delete_claim(selected)
            st.success("Claim deleted")
            st.experimental_rerun()

def reports():
    st.title("Reports & Analysis")

    report_functions = {
        "Providers per City": get_providers_per_city,
        "Receivers per City": get_receivers_per_city,
        "Provider Contacts by City": get_provider_contacts_by_city,
        "Food Quantity by Type": get_food_quantity_by_type,
        "Expiring Soon Food (3 days)": get_expiring_soon_food,
        "Claim Status Distribution": get_claim_status_distribution,
        "Provider Donations Count": get_provider_donations_count,
        "Receiver Claims Count": get_receiver_claims_count,
        "Foods by Location": get_foods_by_location,
        "Meal Type Distribution": get_meal_type_distribution,
        "Food Listing by Provider": get_food_listing_by_provider,
        "Food Claim History": get_food_claim_history,
        "Total Donations Over Time": get_total_donations_over_time,
        "Average Food Quantity by Meal Type": get_avg_food_quantity_by_meal_type,
        "Top Receivers": get_top_receivers,
    }

    selected_report = st.selectbox("Select Report", list(report_functions.keys()))
    func = report_functions[selected_report]

    # Handle reports that require parameters
    if selected_report == "Provider Contacts by City":
        city = st.text_input("Enter City")
        if city:
            df = func(city)
        else:
            st.warning("Please enter a city to run this report.")
            return
    elif selected_report == "Food Listing by Provider":
        provider_name = st.text_input("Enter Provider Name")
        if provider_name:
            df = func(provider_name)
        else:
            st.warning("Please enter a provider name to run this report.")
            return
    elif selected_report == "Food Claim History":
        food_id = st.number_input("Enter Food ID", min_value=1, step=1)
        if food_id > 0:
            df = func(food_id)
        else:
            st.warning("Please enter a valid Food ID to run this report.")
            return
    else:
        # Some functions accept optional args like days or limit, but default is used here
        df = func()

    if df.empty:
        st.info("No data found for this report.")
    else:
        st.dataframe(df)
        # You can add charts per report here if desired (bar charts, line charts, etc.)

# Top bar navigation using tabs
PAGES = {
    "Dashboard": dashboard,
    "Manage Providers": manage_providers,
    "Manage Receivers": manage_receivers,
    "Manage Food Listings": manage_food_listings,
    "Manage Claims": manage_claims,
    "Reports": reports,
}

tabs = st.tabs(list(PAGES.keys()))

for tab, label in zip(tabs, PAGES.keys()):
    with tab:
        PAGES[label]()
