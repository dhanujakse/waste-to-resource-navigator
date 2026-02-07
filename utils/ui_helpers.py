import streamlit as st
from typing import Dict, List


def render_safety_indicator(is_hazardous: bool, risk_level: str = "low"):
    """
    Render safety indicator with appropriate styling based on hazard status
    """
    if is_hazardous:
        if risk_level.lower() == "high":
            st.error("HIGH RISK - HAZARDOUS MATERIAL DETECTED")
        elif risk_level.lower() == "medium":
            st.warning("MEDIUM RISK - CAUTION ADVISED")
        else:
            st.warning("HAZARDOUS MATERIAL DETECTED")
    else:
        st.success("SAFE FOR RECYCLING")


def render_material_info(material_analysis: Dict):
    """
    Render material analysis information in a structured format
    """
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Material Type:**")
        st.subheader(material_analysis.get("material_type", "Unknown"))

    with col2:
        st.write("**Confidence Score:**")
        confidence = material_analysis.get("confidence_score", 0)
        st.subheader(f"{confidence}%")
        st.progress(confidence / 100)

    category = material_analysis.get("material_category", "Unknown")
    st.write(f"**Category:** {category}")

    description = material_analysis.get("description", "No description available")
    st.write("**Description:**")
    st.info(description)


def render_safety_guidelines(safety_assessment: Dict):
    """
    Render safety guidelines based on assessment
    """
    st.subheader("Safety Guidelines")

    if safety_assessment.get("is_hazardous", False):
        st.write("**Hazard Warning:** This material poses potential risks.")

        hazard_cats = safety_assessment.get("hazard_categories", [])
        if hazard_cats:
            st.write("**Risk Categories:**")
            for cat in hazard_cats:
                st.write(f"- {cat.replace('_', ' ').title()}")

        guidelines = safety_assessment.get("safety_guidelines", [])
        if guidelines:
            st.write("**Required Safety Measures:**")
            for guideline in guidelines:
                st.write(f"- {guideline}")
    else:
        st.write("**Material is safe for standard recycling procedures.**")
        st.write("Follow general waste segregation guidelines and use regular protective equipment.")


def render_compliance_info(compliance_data: Dict):
    """
    Render compliance information from legal RAG system
    """
    st.subheader("Regulatory Compliance")

    guidelines = compliance_data.get("guidelines", "No guidelines available")
    if guidelines and guidelines != "No guidelines found":
        st.write("**CPCB Disposal Guidelines:**")
        st.write(guidelines)

    citations = compliance_data.get("citations", [])
    if citations:
        st.write("**Regulatory Citations:**")
        for citation in citations:
            st.write(f"- {citation}")

    sources = compliance_data.get("sources", [])
    if sources:
        st.write("**Reference Sources:**")
        for source in sources:
            st.write(f"- {source}")


def render_recycler_options(recyclers: List[Dict]):
    """
    Render local recycler options with pricing
    """
    st.subheader("Local Recycling Options")

    if not recyclers:
        st.info("No nearby recyclers found for this material type.")
        return

    for i, recycler in enumerate(recyclers):
        rate = recycler.get("rate", "N/A")
        distance = recycler.get("distance", None)
        distance_display = f"{distance} km" if isinstance(distance, (int, float)) else "N/A"
        with st.expander(f"{recycler.get('name', 'Recycler')} - INR {rate}/kg", expanded=True):
            st.write(f"**Location:** {recycler.get('address', 'Address not available')}")
            st.write(f"**Distance:** {distance_display}")
            st.write(f"**Materials Accepted:** {', '.join(recycler.get('materials', []))}")
            if recycler.get("contact"):
                st.write(f"**Contact:** {recycler.get('contact')}")

            if st.button(f"Contact {recycler.get('name', 'Recycler')}", key=f"contact_{i}"):
                st.session_state[f"contact_{recycler.get('id', i)}"] = True
                st.success(f"Contact request sent to {recycler.get('name', 'Recycler')}!")


def render_multilanguage_header(current_lang: str = "en"):
    """
    Render multilanguage header options
    """
    col1, col2 = st.columns([3, 1])

    with col1:
        st.title("Circular AI: Waste-to-Resource Navigator")

    with col2:
        language = st.selectbox(
            "Language",
            ["English", "Hindi"],
            key="language_selector"
        )

        if language == "Hindi":
            st.session_state.lang = "hi"
        else:
            st.session_state.lang = "en"

    if st.session_state.get("lang") == "hi":
        st.subheader("Bridge waste generation and resource recovery with AI")
    else:
        st.subheader("Bridging Waste Generation and Resource Recovery with AI")


def translate_text(text_key: str, lang: str = "en") -> str:
    """
    Translate text based on language preference
    """
    translations = {
        "upload_waste": {
            "en": "Upload Waste Image",
            "hi": "Upload Waste Image"
        },
        "hazardous_detected": {
            "en": "HAZARDOUS MATERIAL DETECTED",
            "hi": "HAZARDOUS MATERIAL DETECTED"
        },
        "safe_for_recycling": {
            "en": "SAFE FOR RECYCLING",
            "hi": "SAFE FOR RECYCLING"
        },
        "processing": {
            "en": "Processing image...",
            "hi": "Processing image..."
        },
        "results": {
            "en": "Analysis Results",
            "hi": "Analysis Results"
        },
        "material_type": {
            "en": "Material Type",
            "hi": "Material Type"
        },
        "confidence": {
            "en": "Confidence",
            "hi": "Confidence"
        },
        "about": {
            "en": "About Circular AI",
            "hi": "About Circular AI"
        },
        "about_desc": {
            "en": "**Circular AI** bridges waste generation and resource recovery using multimodal GenAI.\n\n1. Upload an image of waste material\n2. AI identifies material type and properties\n3. Safety assessment determines hazard level\n4. Legal compliance info from CPCB 2016\n5. Local recycler matching for resource recovery",
            "hi": "Circular AI bridges waste generation and resource recovery using multimodal GenAI."
        },
        "settings": {
            "en": "System Settings",
            "hi": "System Settings"
        },
        "api_keys_config": {
            "en": "API Configuration Check",
            "hi": "API Configuration Check"
        },
        "api_warning": {
            "en": "Please configure your API keys in .env file",
            "hi": "Please configure your API keys in .env file"
        },
        "features": {
            "en": "Platform Features",
            "hi": "Platform Features"
        },
        "feature_list": {
            "en": "- Multimodal waste identification\n- CPCB 2016 compliance checking\n- Hazardous material detection\n- Local recycler price matching\n- Hindi/English interface\n- EPR compliance tracking",
            "hi": "- Multimodal waste identification\n- CPCB 2016 compliance checking\n- Hazardous material detection\n- Local recycler price matching\n- Hindi/English interface\n- EPR compliance tracking"
        },
        "image_details": {
            "en": "Image Metadata",
            "hi": "Image Metadata"
        },
        "analyze_button": {
            "en": "Analyze Material",
            "hi": "Analyze Material"
        },
        "welcome_title": {
            "en": "Circular AI Platform",
            "hi": "Circular AI Platform"
        },
        "welcome_info": {
            "en": "Upload an image of waste material to begin analysis. Our AI will identify the material type, assess safety, check compliance with CPCB regulations, and connect you with local recyclers.",
            "hi": "Upload an image of waste material to begin analysis. Our AI will identify the material type, assess safety, check compliance with CPCB regulations, and connect you with local recyclers."
        },
        "material_metric": {
            "en": "Material Types",
            "hi": "Material Types"
        },
        "safety_metric": {
            "en": "Safety Checks",
            "hi": "Safety Checks"
        },
        "cpcb_metric": {
            "en": "Regulatory Coverage",
            "hi": "Regulatory Coverage"
        },
        "lang_metric": {
            "en": "Supported Languages",
            "hi": "Supported Languages"
        },
        "recycling_options": {
            "en": "Local Recovery Centers",
            "hi": "Local Recovery Centers"
        },
        "safety_guidelines_title": {
            "en": "Safety Protocols",
            "hi": "Safety Protocols"
        },
        "regulatory_compliance": {
            "en": "Regulatory Compliance",
            "hi": "Regulatory Compliance"
        }
    }

    return translations.get(text_key, {}).get(lang, translations.get(text_key, {}).get("en", text_key))


def show_loading_animation():
    """
    Show loading animation while processing
    """
    with st.spinner("Analyzing waste material..."):
        import time
        time.sleep(2)
