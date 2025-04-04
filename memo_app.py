import streamlit as st
import requests
import json
import logging
import base64
from io import BytesIO
from PIL import Image

# Backend API endpoint
# API_URL = "http://127.0.0.1:8000/memo_gen/industry_forecast/"
API_URL = "https://secfilingextractor.polynomial.ai/poc2/memo_gen/industry_forecast/"

# Load NACE codes from JSON file
def get_nace_list():
    with open("../testing_scripts/nace_code.json", "r") as file:
        nace_list = json.load(file)
    return [f"{code} : {name}" for code, name in nace_list.items()]

# Function to fetch data from the backend
def get_forecast(nace_code, country_name, forecast_years,llm_name):
    payload = {
        "nace_code": nace_code,
        "country_name": country_name,
        "forecast_years": forecast_years,
        "llm_name": llm_name
    }
    try:
        response = requests.post(API_URL, json=payload)
        
        if not response.status_code == 200:
            if response.status_code == 400:
                error_response = response.json()
                error_message = error_response.get("errors", "Invalid input parameters.")
                logging.error(f"Error: {error_message}")
                fields = ",".join([i for i in error_message.keys()])
                st.error(f"❌ Invalid input parameters. Please check your inputs: {fields}")
                return {}
            elif response.status_code == 500:
                error_data = response.json()
                error_message = error_data.get("errors", "Unknown error occurred.")
                st.error(f"❌ {error_message} from {llm_name} model.")
                return {} 
        
        response.raise_for_status()  
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"❌ Error fetching data: {e}")
        return {}

# Function to decode Base64 image
def decode_base64_image(base64_string):
    if not base64_string:
        return None
    image_data = base64.b64decode(base64_string)
    return Image.open(BytesIO(image_data))

# Function to display data
def display_data(key, data):
    if isinstance(data, dict):
        st.subheader(f"🔹 {key}")
        for sub_key, sub_value in data.items():
            if isinstance(sub_value, dict):
                st.markdown(f"**{sub_key}**")
                for inner_key, inner_value in sub_value.items():
                    st.write(f"• {inner_key}: {inner_value}")
            else:
                st.write(f"**{sub_key}:** {sub_value}")
    elif isinstance(data, list):
        st.subheader(f"🔹 {key}")
        for item in data:
            st.write(f"• {item}")
    else:
        st.subheader(f"🔹 {key}")
        st.write(data)

# Streamlit App
st.set_page_config(page_title="Industry Forecast", layout="wide")

if "page" not in st.session_state:
    st.session_state.page = "input"

if st.session_state.page == "input":
    st.title("📊 Industry Forecast Generator")
    st.subheader("Enter Industry Details")

    nace_code = st.selectbox("NACE Code", get_nace_list())
    country = st.text_input("Country Name")
    forecast_years = st.number_input("Forecast Years", step=1)
    option = ["gemini", "chatgpt"]
    llm_name = st.selectbox("Choose LLM",option, index=0)

    if st.button("Generate Dashboard"):
        with st.spinner("Fetching forecast data..."):
            response = get_forecast(nace_code, country, forecast_years, llm_name)
            if not response:
                st.warning("No Data Found.")
            elif "error" in response:
                st.error(response["error"])
            else:
                st.session_state.response = response
                st.session_state.page = "result"
                st.rerun()

elif st.session_state.page == "result":
    response = st.session_state.response

    industry_name = response.get("industry_name", "N/A")
    country_name = response.get("country_name", "N/A")
    forecast_years = response.get("forecast_years", 0)
    currency = response.get("currency", "N/A")
    market_values = response.get("market_values", "N/A")
    image_base64 = response.get("path", None)  # Get Base64 Image from API

    st.markdown("## 🌟 **Attractive and Growing Market**")
    st.write(f"**Industry:** {industry_name}  |  **Country:** {country_name}")

    data_set = response.get("market_size_and_growth_projections")
    
    if data_set:
        if len(data_set) > 2:
            first_key, first_value = list(data_set.items())[0]
            last_key, last_value = list(data_set.items())[1]  # Corrected last element extraction
            first_last_dict = {
                first_key: first_value,
                last_key: last_value
            }
        else:
            first_key, first_value = list(data_set.items())[0]
            first_last_dict = {
                first_key: first_value
            }

        col1, col2 = st.columns([2, 3])  # More space for the image on the left
        with col1:
            display_data("Market Size and Growth Projections", first_last_dict)
            
            # Decode and Display Base64 Image
            image = None
            if image_base64:
                image = decode_base64_image(image_base64)
            if image:
                st.image(image, caption="📊 Market Growth Chart", use_container_width=True)
            else:
                st.error("Graph is not generated.")

        with col2:
            display_data("Market Drivers", response.get("market_drivers", []))
            display_data("Emerging Market Trends", response.get("emerging_market_trends", []))


    # Display Other Sections
    col3, col4 = st.columns(2)
    with col3:
        # display_data("Emerging Market Trends", response.get("emerging_market_trends", []))
        display_data("Spending Figures", response.get("spending_figures", {}))
    with col4:
        # display_data("Spending Figures", response.get("spending_figures", {}))
        display_data("Market Entry Barriers", response.get("market_entry_barriers", {}))

    # Back to Input Page
    if st.button("🔄 Back to Input Page"):
        st.session_state.page = "input"
        st.rerun()
