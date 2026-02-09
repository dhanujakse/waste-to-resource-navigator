import streamlit as st
from PIL import Image
import io
import json
import pandas as pd
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.system_orchestrator import CircularAISystem
from utils.ui_helpers import (
    render_safety_indicator,
    render_material_info,
    render_safety_guidelines,
    render_compliance_info,
    render_recycler_options,
    render_multilanguage_header,
    translate_text,
    show_loading_animation
)

try:
    from streamlit_geolocation import streamlit_geolocation
except Exception:
    streamlit_geolocation = None

# Initialize session state
if "analysis_complete" not in st.session_state:
    st.session_state.analysis_complete = False
if "material_analysis" not in st.session_state:
    st.session_state.material_analysis = {}
if "safety_assessment" not in st.session_state:
    st.session_state.safety_assessment = {}
if "compliance_info" not in st.session_state:
    st.session_state.compliance_info = {}
if "nearby_options" not in st.session_state:
    st.session_state.nearby_options = []
if "system_output" not in st.session_state:
    st.session_state.system_output = {}
if "user_city" not in st.session_state:
    st.session_state.user_city = ""
if "user_lat" not in st.session_state:
    st.session_state.user_lat = None
if "user_lon" not in st.session_state:
    st.session_state.user_lon = None
if "gps_error" not in st.session_state:
    st.session_state.gps_error = ""
if "show_raw_json" not in st.session_state:
    st.session_state.show_raw_json = False


def _validate_lat_lon(lat, lon):
    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (TypeError, ValueError):
        return False
    return -90.0 <= lat_f <= 90.0 and -180.0 <= lon_f <= 180.0


def main():
    # Set page config
    st.set_page_config(
        page_title="Circular AI Enterprise",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Custom CSS for polished but theme-safe look
    st.markdown(
        """
        <style>
        .block-container {
            padding-top: 2rem;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # Render multilanguage header
    render_multilanguage_header()

    # Sidebar with instructions
    with st.sidebar:
        st.header(translate_text("about", st.session_state.get("lang", "en")))
        st.info(translate_text("about_desc", st.session_state.get("lang", "en")))

        st.header(translate_text("settings", st.session_state.get("lang", "en")))
        _ = st.checkbox(translate_text("api_keys_config", st.session_state.get("lang", "en")), value=True)
        st.text_input("City (optional)", key="user_city")
        st.checkbox("Show raw JSON output", key="show_raw_json")

        if streamlit_geolocation is None:
            st.info("Location auto-detect requires streamlit-geolocation.")
        else:
            if st.session_state.user_lat is None or st.session_state.user_lon is None:
                loc = streamlit_geolocation()
                if loc and loc.get("latitude") and loc.get("longitude"):
                    st.session_state.user_lat = loc["latitude"]
                    st.session_state.user_lon = loc["longitude"]
                    st.session_state.gps_error = ""
                else:
                    st.session_state.gps_error = "Unable to auto-detect location. You can continue without it."
            if st.session_state.gps_error:
                st.warning(st.session_state.gps_error)

        st.header(translate_text("features", st.session_state.get("lang", "en")))
        st.write(translate_text("feature_list", st.session_state.get("lang", "en")))

    # Create Tabs for different Personas
    tab1, tab2, tab3 = st.tabs(["Citizen Navigator", "Marketplace (B2B)", "EPR Dashboard"])

    # --- TAB 1: CITIZEN NAVIGATOR ---
    with tab1:
        st.markdown("### Upload Waste Image")

        uploaded_file = st.file_uploader(
            translate_text("upload_waste", st.session_state.get("lang", "en")),
            type=["jpg", "jpeg", "png"],
            accept_multiple_files=False,
            key="citizen_uploader"
        )

        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(image, caption="Uploaded Artifact", use_column_width=True)

            with col2:
                st.write(f"**{translate_text('image_details', st.session_state.get('lang', 'en'))}**")
                st.write(f"Dimensions: {image.size[0]} x {image.size[1]} px")
                st.write(f"Format: {image.format}")

            if st.button(translate_text("analyze_button", st.session_state.get("lang", "en")), type="primary", key="analyze_btn"):
                with st.spinner(translate_text("processing", st.session_state.get("lang", "en"))):
                    system = CircularAISystem()

                    img_byte_arr = io.BytesIO()
                    image.save(img_byte_arr, format=image.format)
                    img_bytes = img_byte_arr.getvalue()

                    user_lat = st.session_state.get("user_lat")
                    user_lon = st.session_state.get("user_lon")
                    if not _validate_lat_lon(user_lat, user_lon):
                        user_lat = None
                        user_lon = None

                    try:
                        result = system.run(
                            img_bytes,
                            filename=uploaded_file.name,
                            city=st.session_state.get("user_city"),
                            user_lat=user_lat,
                            user_lon=user_lon
                        )
                    except Exception as e:
                        st.error(f"GenAI pipeline failed: {e}")
                        return

                    st.session_state.material_analysis = result.get("material_analysis", {})
                    st.session_state.safety_assessment = result.get("safety_assessment", {})
                    st.session_state.compliance_info = result.get("compliance_info", {})
                    st.session_state.nearby_options = result.get("nearby_options", [])
                    st.session_state.system_output = result.get("final_output", {})
                    st.session_state.analysis_complete = True

                    st.rerun()

        if st.session_state.analysis_complete:
            st.markdown("---")
            st.header(translate_text("results", st.session_state.get("lang", "en")))

            render_safety_indicator(
                st.session_state.safety_assessment.get("is_hazardous", False),
                st.session_state.safety_assessment.get("risk_level", "low")
            )

            nudge = st.session_state.material_analysis.get("sustainability_nudge")
            if nudge:
                st.success(f"**Impact Insight:** {nudge}")

            if st.session_state.material_analysis.get("analysis_source") == "fallback":
                st.warning("Image analysis used fallback mode. Check OpenRouter API key or quota.")

            with st.container():
                render_material_info(st.session_state.material_analysis)
                render_safety_guidelines(st.session_state.safety_assessment)
                render_compliance_info(st.session_state.compliance_info)

            # 3b. Clear Instructions
            instructions = st.session_state.system_output.get("instructions", [])
            do_not = st.session_state.system_output.get("do_not", [])
            if instructions:
                st.subheader("What To Do")
                for step in instructions:
                    st.write(f"- {step}")
            if do_not:
                st.subheader("What Not To Do")
                for item in do_not:
                    st.write(f"- {item}")

            st.subheader(translate_text("recycling_options", st.session_state.get("lang", "en")))
            render_recycler_options(st.session_state.get("nearby_options", []))

            map_points = []
            for r in st.session_state.get("nearby_options", []):
                if r.get("latitude") is not None and r.get("longitude") is not None:
                    map_points.append({
                        "lat": r.get("latitude"),
                        "lon": r.get("longitude"),
                        "name": r.get("name"),
                        "distance_km": r.get("distance")
                    })
            if st.session_state.get("user_lat") is not None and st.session_state.get("user_lon") is not None:
                map_points.append({
                    "lat": st.session_state.get("user_lat"),
                    "lon": st.session_state.get("user_lon"),
                    "name": "You",
                    "distance_km": 0
                })
            if map_points:
                st.subheader("Nearby Recyclers Map")
                st.map(pd.DataFrame(map_points), latitude="lat", longitude="lon")

            if st.session_state.get("show_raw_json"):
                st.subheader("System Output (JSON)")
                st.code(json.dumps(st.session_state.get("system_output", {}), indent=2), language="json")

        else:
            st.markdown("---")
            st.subheader(translate_text("welcome_title", st.session_state.get("lang", "en")))
            st.info(translate_text("welcome_info", st.session_state.get("lang", "en")))

    # --- TAB 2: MARKETPLACE (B2B) ---
    with tab2:
        st.header("Industrial Waste Marketplace")

        col1, col2, col3 = st.columns(3)
        col1.metric("PET Price", "INR 45/kg", "+2.4%")
        col2.metric("Copper Price", "INR 720/kg", "-0.8%")
        col3.metric("OCC Price", "INR 18/kg", "+0.5%")

        st.markdown("### Active Listings")
        st.dataframe({
            "Material": ["PET Bottles (Baled)", "Cardboard (OCC)", "Aluminum Cans"],
            "Quantity": ["500 kg", "1200 kg", "300 kg"],
            "Location": ["Okhla Phase III", "Manesar", "Noida Sec 63"],
            "Highest Bid": ["INR 42/kg", "INR 18/kg", "INR 110/kg"]
        }, use_container_width=True)

        st.button("Create New Listing", type="primary")

    # --- TAB 3: EPR DASHBOARD ---
    with tab3:
        st.header("EPR Compliance Dashboard")

        col1, col2, col3 = st.columns(3)
        col1.metric("Plastic Recovered", "12,450 kg", "+15%")
        col2.metric("Carbon Credits", "450 tons", "Certified")
        col3.metric("Audit Status", "Ready", "Low Risk")

        st.markdown("### Recent Recovery Certificates")
        st.dataframe({
            "Certificate ID": ["EPR-2026-001", "EPR-2026-002"],
            "Date": ["2026-02-01", "2026-02-04"],
            "Material": ["MLP", "Rigid Plastic"],
            "Processor": ["Shakti Plastics", "Recykal"],
            "Status": ["Verified", "Verified"]
        }, use_container_width=True)

        st.button("Download Monthly Report")


if __name__ == "__main__":
    main()
