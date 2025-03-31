import streamlit as st
import requests
import os

# Set full-screen layout at the very beginning
st.set_page_config(layout="wide")

# Apply Full-Screen CSS & Improve Layout
st.markdown(
    """
    <style>
        .main .block-container {
            max-width: 100%;
            padding-left: 0px;
            padding-right: 0px;
        }
        .st-emotion-cache-1y4p8pa {
            padding: 0rem;
        }
        .stImage img {
            max-width: 100% !important;
            height: auto !important;
        }
        .market-data {
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 12px;
            font-size: 18px;
            color: #333;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Define available details for selection
detail_options = {
    "Revenue Growth": "revenue_graph",
    "Company Growth": "company_growth_graph",
    "Financial Market Overview": "financial_overview_graph"
}

# Initialize session state variables
if "page" not in st.session_state:
    st.session_state.page = "home"
if "response_data" not in st.session_state:
    st.session_state.response_data = None
if "selected_details" not in st.session_state:
    st.session_state.selected_details = []
if "submitted_once" not in st.session_state:
    st.session_state.submitted_once = False

# Function to send data to the API and retrieve the response
def fetch_data_from_api(payload):
    api_url = "https://1a42-106-51-85-102.ngrok-free.app/memo_gen/company-llm-flow/" 
    headers = {"Content-Type": "application/json"}
    try:
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

# Function to display graphs and market data in a structured layout
def show_graphs():
    if st.session_state.response_data:
        company_name = st.session_state.response_data.get("company_name", "Company")
        st.header(f"{company_name} Overview")

        graphs = st.session_state.response_data.get("graphs", {})
        market_data = st.session_state.response_data.get("market_data", {})
        image_dir = "static"

        # Adjust column sizes (2:3 ratio for larger graphs)
        col1, col2 = st.columns([2, 3])  # More space for graphs

        with col1:
            st.subheader("Graphs")
            for detail, graph_key in detail_options.items():
                if detail in st.session_state.selected_details and graph_key in graphs:
                    image_path = os.path.join(image_dir, graphs[graph_key])
                    if os.path.exists(image_path):
                        st.image(image_path, caption=detail, use_container_width=True)  # Bigger image
                    else:
                        st.error(f"Image not found: {image_path}")

        with col2:
            st.subheader("Market Insights")
            if market_data:
                if isinstance(market_data, list):
                    for item in market_data:
                        st.markdown(f"<div class='market-data'>✔️ {item}</div>", unsafe_allow_html=True)
                elif isinstance(market_data, str):
                    st.markdown(f"<div class='market-data'>{market_data}</div>", unsafe_allow_html=True)
                else:
                    st.warning("Market insights format is not recognized.")
            else:
                st.info("No market insights available.")

        # Back Button
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Back"):
            st.session_state.page = "home"
            st.rerun()

# Page Navigation Logic
if st.session_state.page == "home":
    st.title("Company Data Viewer")

    company_name = st.text_input("Company Name", st.session_state.get("company_name", ""))
    region_name = st.text_input("Region Name", st.session_state.get("region_name", ""))
    subregion_name = st.text_input("Subregion Name", st.session_state.get("subregion_name", ""))

    selected_details = st.multiselect("Select Data to Display:", list(detail_options.keys()), default=st.session_state.get("selected_details", []))
    from_date = st.date_input("From Date", st.session_state.get("from_date", None))
    to_date = st.date_input("To Date", st.session_state.get("to_date", None))

    # Align buttons in the same row (Submit on left, Next on right)
    col1, col2 = st.columns([3, 1])
    missing_fields = []

    with col1:
        if st.button("Submit", key="submit_button"):
            if not company_name:
                missing_fields.append("Company Name")
            if not selected_details:
                missing_fields.append("Selected Data")
            if not from_date:
                missing_fields.append("From Date")
            if not to_date:
                missing_fields.append("To Date")

            if missing_fields:
                st.warning(f"Please fill in the following fields: {', '.join(missing_fields)}")
            else:
                payload = {
                    "company_name": company_name,
                    "region_name": region_name if region_name else "",
                    "subregion_name": subregion_name if subregion_name else "",
                    "details": selected_details,
                    "from_date": from_date.strftime("%Y-%m-%d"),
                    "to_date": to_date.strftime("%Y-%m-%d")
                }

                # Fetch data
                response_data = fetch_data_from_api(payload)

                if response_data:
                    st.session_state.response_data = response_data
                    st.session_state.selected_details = selected_details
                    st.session_state.submitted_once = True
                    st.session_state.page = "graphs"
                    st.session_state.company_name = company_name
                    st.session_state.region_name = region_name
                    st.session_state.subregion_name = subregion_name
                    st.session_state.from_date = from_date
                    st.session_state.to_date = to_date
                    st.rerun()
                else:
                    st.error("Failed to retrieve data from the API.")

    with col2:
        if st.session_state.submitted_once:
            if st.button("Next", key="next_button"):
                st.session_state.page = "graphs"
                st.rerun()

elif st.session_state.page == "graphs":
    show_graphs()
