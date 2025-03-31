import streamlit as st
import requests
from PIL import Image
import os

# Function to send data to the API and retrieve the response
def fetch_data_from_api(payload):
    api_url = "http://127.0.0.1:8000/memo_gen/company-llm-flow/"  # Replace with your actual API URL
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

# Streamlit UI
st.title("Company Data Viewer")

# Input fields
company_name = st.text_input("Company Name", "")
region_name = st.text_input("Region Name", "")
subregion_name = st.text_input("Subregion Name", "")

# Multi-select checkbox for details
detail_options = {
    "Revenue Growth": "revenue_graph",
    "Company Growth": "company_growth_graph",
    "Financial Market Overview": "financial_overview_graph"
}
selected_details = st.multiselect("Select Data to Display:", list(detail_options.keys()))

from_date = st.date_input("From Date")
to_date = st.date_input("To Date")
# Submit button
if st.button("Submit"):
    if company_name:
        # Prepare payload
        payload = {
            "company_name": company_name,
            "region_name": region_name,
            "subregion_name": subregion_name,
            "details": selected_details,
            "from_date": from_date.strftime("%Y-%m-%d"),
            "to_date": to_date.strftime("%Y-%m-%d")
        }

        # Fetch data from API
        response_data = fetch_data_from_api(payload)

        if response_data:
            st.success("Data received successfully!")
            company_name_from_api = response_data.get("company_name", "Company")
            st.header(f"📊 {company_name_from_api} Overview")

            # Get the graphs from API response
            graphs = response_data.get("graphs", {})

            # Define the directory where images are stored
            image_dir = "static"

            # Display only relevant graphs based on selection
            for detail, graph_key in detail_options.items():
                if detail in selected_details and graph_key in graphs:
                    image_path = os.path.join(image_dir, graphs[graph_key])
                    if os.path.exists(image_path):
                        image = Image.open(image_path)
                        st.image(image, caption=detail, use_container_width=True)
                    else:
                        st.error(f"Image not found: {image_path}")

        else:
            st.error("Failed to retrieve data from the API.")
    else:
        st.warning("Please enter the Company Name.")
