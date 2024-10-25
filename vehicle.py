import streamlit as st
from pymongo import MongoClient
import pandas as pd
import re
import folium
from folium.plugins import *
from streamlit_folium import folium_static
import requests

# MongoDB setup
client = MongoClient('mongodb://localhost:27017')  # Connect to your MongoDB server
db = client['vehicle_registration']
vehicles_col = db['vehicles']

geo_json_data = requests.get(
    "https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States"
).json()

# Mongo CRUD Functions
def load_data(include_geo=False):
    """Load vehicle data from MongoDB. If include_geo is True, fetch geographical data too."""
    if include_geo:
        data = [(item["latitude"], item["Longitude"]) for item in vehicles_col.find() if
                "latitude" in item and "Longitude" in item]
        print(f"Loaded geographic data points: {len(data)}")  # Debug: Print how many points are loaded
        return data
    else:
        return {item['vehicle_id']: item for item in vehicles_col.find()}


def save_data(vehicle_id, data):
    """Save or update vehicle data to MongoDB."""
    vehicles_col.update_one({'vehicle_id': vehicle_id}, {'$set': data}, upsert=True)


def delete_data(vehicle_id):
    """Delete vehicle data from MongoDB."""
    vehicles_col.delete_one({'vehicle_id': vehicle_id})


def fetch_details_from_code(registration_number):
    """Extracts the code from the vehicle ID and fetches corresponding details from an Excel file."""
    match = re.search(r"([A-Z]{2}\s*\d{2})", registration_number)
    if match:
        code = match.group(1)
        return get_details_from_excel(code)
    return None, None


def get_details_from_excel(code, excel_file='Book1_Modified.xlsx'):
    """Retrieve details from an Excel file based on the code."""
    df = pd.read_excel(excel_file)
    print("Columns in Excel:", df.columns)  # This will print the list of columns
    details = df[df['Code'] == code]
    if not details.empty:
        office_location = details['Office location'].values[0]
        state_name = details['State'].values[0]
        latitude = details['Latitude'].values[0]
        longitude = details['Longitude'].values[0]
        return office_location, state_name, longitude, latitude
    else:
        return "Code not found in Excel", "Code not found in Excel", None, None


# Streamlit UI
st.title('Vehicle Registration Application')

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Create New Record", "Update/Delete Record", "View All Records", "Map"])

# Tab 1: Create a new vehicle record
with tab1:
    st.header('Create a new vehicle record')
    with st.form("create_vehicle", clear_on_submit=True):
        new_id = st.text_input('Vehicle ID', placeholder="EX - UP 80 AB 1234")
        new_make = st.text_input('Make', placeholder="EX - 2019")
        new_model = st.text_input('Model', placeholder="EX - Tata")
        new_color = st.text_input('Color', placeholder="EX - Red")
        submit_new = st.form_submit_button('Create record')

        if submit_new:
            vehicles = load_data()
            if new_id in vehicles:
                st.error('Vehicle ID already exists.')
            else:
                # Fetch details from Excel based on vehicle ID
                office_location, state_name, longitude, latitude = fetch_details_from_code(new_id)
                vehicle_info = {'vehicle_id': new_id, 'make': new_make, 'model': new_model, 'color': new_color,
                                'office_location': office_location, 'state_name': state_name, 'Longitude': longitude,
                                'latitude': latitude}
                save_data(new_id, vehicle_info)
                st.success(
                    f'Record created successfully with office location: {office_location} and state name: {state_name}')

# Tab 2: Update or delete existing records
with tab2:
    st.header('Update or Delete a vehicle record')
    selected_id = st.selectbox('Select a vehicle ID', options=[''] + list(load_data().keys()))
    vehicle_data = load_data().get(selected_id, {})

    if selected_id:
        make = st.text_input('Make', vehicle_data.get('make', ''))
        model = st.text_input('Model', vehicle_data.get('model', ''))
        color = st.text_input('Color', vehicle_data.get('color', ''))
        if st.button('Update record'):
            save_data(selected_id, {'make': make, 'model': model, 'color': color})
            st.success('Record updated successfully.')
        if st.button('Delete record'):
            delete_data(selected_id)
            st.success('Record deleted successfully.')

# Tab 3: View all vehicle records
with tab3:
    st.header('All Vehicle Records')
    all_vehicles = load_data()
    if all_vehicles:
        for vehicle_id, vehicle_info in all_vehicles.items():
            st.write(
                f"Vehicle ID: {vehicle_id}, Make: {vehicle_info.get('make', '')}, Model: {vehicle_info.get('model', '')}, Color: {vehicle_info.get('color', '')}, Office Location: {vehicle_info.get('office_location', '')}, State: {vehicle_info.get('state_name', '')}")
    else:
        st.warning("No vehicle records found.")

# Tab 4: Display Map
with tab4:
    st.header('Vehicle Distribution Heatmap')
    location_data = load_data(include_geo=True)  # Fetch geo data
    print(location_data)  # Debug: Print loaded data to check

    if location_data:
        # Create a map centered around an average location or a specific point

        avg_lat = sum(lat for lat, _ in location_data) / len(location_data)
        avg_lon = sum(lon for _, lon in location_data) / len(location_data)
        map_center = [avg_lat, avg_lon]

        map = folium.Map(location=map_center, zoom_start=6)
        HeatMap(location_data).add_to(map)
        MiniMap(toggle_display=True).add_to(map)
        MousePosition(position="topright").add_to(map)
        Fullscreen(
            position="topright",
            title="Expand me",
            title_cancel="Exit me",
            force_separate_button=True,
        ).add_to(map)
        # Draw(export=True).add_to(map)
        # folium.GeoJson(geo_json_data).add_to(map)

        folium_static(map)
    else:
        st.error("No geographic data available to display the heatmap. Please check the database.")
