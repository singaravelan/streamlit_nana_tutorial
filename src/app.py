import os
import streamlit as st
from pymongo import MongoClient

# Database connection settings from environment variables
MONGO_HOST = os.environ.get("MONGO_HOST", "localhost")
MONGO_PORT = int(os.environ.get("MONGO_PORT", 27017))
MONGO_USER = os.environ.get("MONGO_USERNAME", "admin")
MONGO_PASS = os.environ.get("MONGO_PASSWORD", "password")

@st.cache_resource
def get_database():
    """Connect to MongoDB and return the database object."""
    client = MongoClient(
        host=MONGO_HOST,
        port=MONGO_PORT,
        username=MONGO_USER,
        password=MONGO_PASS
    )
    return client["user_db"]

db = get_database()
collection = db["profiles"]

st.title("User Profile App (MLOps Tutorial)")
st.write("This app connects to a MongoDB container.")

# Form to add a new user
with st.form("user_form"):
    st.subheader("Add a new User Profile")
    name = st.text_input("Name")
    role = st.text_input("Role (e.g. Data Scientist)")
    submitted = st.form_submit_button("Save Profile")
    
    if submitted and name and role:
        # Save to MongoDB
        collection.insert_one({"name": name, "role": role})
        st.success(f"Successfully added {name} to the database!")

# Display existing users
st.subheader("Existing Profiles")
profiles = list(collection.find({}, {"_id": 0})) # exclude the MongoDB ID for display

if profiles:
    for p in profiles:
        st.write(f"- **{p['name']}**: {p['role']}")
else:
    st.write("No profiles found. Add one above!")
