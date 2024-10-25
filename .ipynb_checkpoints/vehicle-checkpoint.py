# import streamlit as st
# import json
# import os
#
# # File to store data
# DATA_FILE = 'vehicles.json'
#
# # Initialize the data file if it doesn't exist
# if not os.path.isfile(DATA_FILE):
#     with open(DATA_FILE, 'w') as f:
#         json.dump({}, f)  # Empty dictionary to store vehicle data
#
#
# def load_data():
#     """Load vehicle data from the JSON file."""
#     with open(DATA_FILE, 'r') as f:
#         return json.load(f)
#
#
# def save_data(data):
#     """Save vehicle data to the JSON file."""
#     with open(DATA_FILE, 'w') as f:
#         json.dump(data, f, indent=4)
#
#
# # Streamlit UI
# st.title('Vehicle Registration Application')
#
# # For creating a new vehicle record
# st.header('Create a new vehicle record')
# with st.form("create_vehicle", clear_on_submit=True):
#     new_id = st.text_input('Vehicle ID', '')
#     new_make = st.text_input('Make', '')
#     new_model = st.text_input('Model', '')
#     new_color = st.text_input('Color', '')
#     submit_new = st.form_submit_button('Create record')
#
#     if submit_new:
#         vehicles = load_data()
#         if new_id in vehicles:
#             st.error('Vehicle ID already exists.')
#         else:
#             vehicles[new_id] = {'make': new_make, 'model': new_model, 'color': new_color}
#             save_data(vehicles)
#             st.success('Record created successfully.')
#
# # For viewing and updating existing records
# st.header('View, Update, or Delete a vehicle record')
# selected_id = st.selectbox('Select a vehicle ID', options=[''] + list(load_data().keys()))
# vehicle_data = load_data().get(selected_id, {})
#
# if selected_id:
#     make = st.text_input('Make', vehicle_data.get('make', ''))
#     model = st.text_input('Model', vehicle_data.get('model', ''))
#     color = st.text_input('Color', vehicle_data.get('color', ''))
#     if st.button('Update record'):
#         vehicles = load_data()
#         vehicles[selected_id] = {'make': make, 'model': model, 'color': color}
#         save_data(vehicles)
#         st.success('Record updated successfully.')
#     if st.button('Delete record'):
#         vehicles = load_data()
#         del vehicles[selected_id]
#         save_data(vehicles)
#         st.success('Record deleted successfully.')









import streamlit as st
from pymongo import MongoClient

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')  # Connect to your MongoDB server
db = client['vehicle_registration']  # Database name
vehicles_col = db['vehicles']  # Collection name

def load_data():
    """Load vehicle data from MongoDB."""
    return {item['vehicle_id']: item for item in vehicles_col.find()}

def save_data(vehicle_id, data):
    """Save or update vehicle data to MongoDB."""
    vehicles_col.update_one({'vehicle_id': vehicle_id}, {'$set': data}, upsert=True)

def delete_data(vehicle_id):
    """Delete vehicle data from MongoDB."""
    vehicles_col.delete_one({'vehicle_id': vehicle_id})

# Streamlit UI
st.title('Vehicle Registration Application')

# Create a new vehicle record
st.header('Create a new vehicle record')
with st.form("create_vehicle", clear_on_submit=True):
    new_id = st.text_input('Vehicle ID', '')
    new_make = st.text_input('Make', '')
    new_model = st.text_input('Model', '')
    new_color = st.text_input('Color', '')
    submit_new = st.form_submit_button('Create record')

    if submit_new:
        vehicles = load_data()
        if new_id in vehicles:
            st.error('Vehicle ID already exists.')
        else:
            save_data(new_id, {'vehicle_id': new_id, 'make': new_make, 'model': new_model, 'color': new_color})
            st.success('Record created successfully.')

# View, update, or delete existing records
st.header('View, Update, or Delete a vehicle record')
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
