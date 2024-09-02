import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from st_supabase_connection import SupabaseConnection, execute_query
import pandas as pd
from datetime import datetime

st.header("Attendance")

conn = st.connection("supabase", type=SupabaseConnection)

# Fetch engineer data including ID, name, and contact number
engineers_data = pd.DataFrame(execute_query(conn.table("Engineers").select("id", "name", "contact_number", count="None"), ttl=None).data)
engineers = list(engineers_data["name"])

engineerInput = st.selectbox("Engineer", options=engineers, index=None)
contactInput = st.text_input("Phone Number")
image = st.file_uploader(label="Image", type=["png", "jpg", "jpeg", "webp"], accept_multiple_files=False)
location = streamlit_geolocation()
submit = st.button("Present")

if submit:
    if location["latitude"] is None:
        st.error("Location is required. Please allow location access.")
    else:
    # Find the engineer's ID and contact number for the selected engineer
        selected_engineer = engineers_data[engineers_data["name"] == engineerInput].iloc[0]
        selected_engineer_contact = selected_engineer["contact_number"]
        selected_engineer_id = selected_engineer["id"]
        filename = ""
        if image is not None:
            filename = "attendance_image/"+str(datetime.now())+image.__getattribute__("name")
            conn.upload("images", "local",image , filename)
        if selected_engineer_contact == contactInput:
            st.write("Contact number matches.")
            
            # Update the Attendance table with engineer ID, latitude, and longitude
            attendance_data = {
                "engineer_id": selected_engineer_id,
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "image":filename
            }
            execute_query(conn.table("attendance").insert(attendance_data), ttl="0")
            st.write("Attendance has been recorded.")
        else:
            st.write("Contact number does not match.")
