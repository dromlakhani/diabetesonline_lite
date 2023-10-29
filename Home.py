import streamlit as st
import pandas as pd
from datetime import date
from google.cloud import storage

# Initialize a client for Google Cloud Storage
def initialize_storage_client(credentials_file):
    return storage.Client.from_service_account_json(credentials_file)

# Upload a file to a Google Cloud Storage bucket
def upload_to_bucket(bucket_name, folder_name, file_name, content):
    client = initialize_storage_client("/Users/omlakhani/Library/CloudStorage/OneDrive-Personal/PROJECTS2023/Experiments_2023/Streamlit_googlecloud/dark-tenure-397604-ecbea11c3dd9.json")
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"{folder_name}/{file_name}")
    blob.upload_from_string(content)
    return blob.public_url

def calculate_bmi(height, weight):
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 2)

def convert_to_cm(feet, inches):
    total_inches = feet * 12 + inches
    cm = total_inches * 2.54
    return cm

# Function to load data from CSV
def load_data():
    try:
        df = pd.read_csv('/Users/omlakhani/Library/CloudStorage/OneDrive-Personal/PROJECTS2023/CRM2023/Database_Files/patient_crm_database_2023.csv')
    except FileNotFoundError:
        df = pd.DataFrame(columns=[
            'Patient name', 'gender', 'age', 'diagnosis', 'Contact number',
            'email', 'Online patient', 'Offline patient', 'International patient', 'Date added', 'city', 'pincode', 'height', 'weight' , 'bmi'
        ])
    return df

# Function to save data to CSV
def save_data(df):
    df.to_csv('/Users/omlakhani/Library/CloudStorage/OneDrive-Personal/PROJECTS2023/CRM2023/Database_Files/patient_crm_database_2023.csv', index=False)

st.title("Patient Details")

# Load the data
df = load_data()

# Input fields for the form
patient_name = st.text_input('Patient name', '')
gender = st.radio('Gender', ('Male', 'Female', 'Other'))
age = st.number_input('Age', min_value=0, value=0, step=1)
contact_number = st.text_input('Contact number', '')
email = st.text_input('Email', '')
date_added = date.today()
city = st.text_input("Enter the name of your city or town")
pincode = st.text_input("Enter your pincode")
weight = st.number_input("Enter your weight in kg")
st.write("Enter your height")
height_feet = st.number_input("Feet")
height_inches = st.number_input("Inches")
height = convert_to_cm(height_feet, height_inches)
bmi = 0.0
if height != 0:
    bmi = calculate_bmi(height, weight)

uploaded_files = st.file_uploader("Upload files (reports and prescriptions)", accept_multiple_files=True)

if st.button('Submit'):
    # Append the data to the dataframe and save
    new_entry = {
        'Patient name': patient_name,
        'gender': gender,
        'age': age,
        'Contact number': contact_number,
        'email': email,
        'Date added': date_added,
        'city': city,
        'pincode': pincode,
        'height': height,
        'weight': weight,
        'bmi': bmi
    }
    df = df.append(new_entry, ignore_index=True)
    save_data(df)

    txt_file_name = f"{patient_name}.txt"
    bucket_name = "reportgpt_drom"

    # Create and upload the text file with patient details
    patient_details = f"Patient Name: {patient_name}\nGender: {gender}\nAge: {age}\nContact Number: {contact_number}\nEmail: {email}\nDate Added: {date_added}\nCity: {city}\nPincode: {pincode}\nHeight: {height}\nWeight: {weight}\nBMI: {bmi}"
    upload_to_bucket(bucket_name, patient_name, txt_file_name, patient_details)

    # Upload the patient files to Google Cloud Storage
    # Upload the patient files to Google Cloud Storage
    upload_success = True
    for uploaded_file in uploaded_files:
        try:
            file_name = uploaded_file.name
            upload_to_bucket(bucket_name, patient_name, file_name, uploaded_file.getvalue())
        except Exception as e:
            upload_success = False
            st.error(f"Error uploading file {file_name}. Please email the files to dromreports@gmail.com: {str(e)}")

    if upload_success:
        st.success(f'Thank you {patient_name} for sending your details. We will check back to you within 7 days')
