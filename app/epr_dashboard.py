import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np
import sys
import os

# Add the project root to the path so imports work correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.localization import get_text

def show_epr_dashboard():
    """
    Display the Extended Producer Responsibility (EPR) compliance dashboard
    """
    st.title("🏭 EPR Compliance Dashboard")
    
    st.info("""
    Extended Producer Responsibility (EPR) requires manufacturers to manage 
    the entire lifecycle of their products, including post-consumer waste.
    This dashboard tracks compliance with CPCB EPR guidelines.
    """)
    
    # Sidebar for EPR configuration
    with st.sidebar:
        st.header("⚙️ EPR Configuration")
        
        company_name = st.text_input("Company Name", "Sample Company Pvt Ltd")
        industry_sector = st.selectbox(
            "Industry Sector",
            ["Plastic Packaging", "Electronics", "Batteries", "Tyres", "Paper", "Textiles"]
        )
        fiscal_year = st.selectbox(
            "Fiscal Year",
            [f"FY {year}-{year+1}" for year in range(2020, 2027)]
        )
        
        # EPR targets based on sector
        epr_targets = {
            "Plastic Packaging": 50,  # % recovery target
            "Electronics": 60,
            "Batteries": 40,
            "Tyres": 80,
            "Paper": 70,
            "Textiles": 30
        }
        
        target_recovery_rate = st.slider(
            "Target Recovery Rate (%)",
            min_value=10,
            max_value=100,
            value=epr_targets[industry_sector],
            step=5
        )
        
        st.subheader("Reporting Period")
        start_date = st.date_input("Start Date", value=datetime.now() - timedelta(days=365))
        end_date = st.date_input("End Date", value=datetime.now())
    
    # Generate mock EPR data
    st.subheader(f"EPR Performance for {company_name}")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "📋 Reports", "🎯 Targets"])
    
    with tab1:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Waste Generated",
                value="1,245 tons",
                delta="+12% from last quarter"
            )
        
        with col2:
            st.metric(
                label="Waste Collected",
                value="789 tons",
                delta="+18% from last quarter"
            )
        
        with col3:
            st.metric(
                label="Recovery Rate",
                value="63.4%",
                delta="+3.2% from target"
            )
        
        with col4:
            st.metric(
                label="Compliance Status",
                value="✅ Compliant",
                delta="On track"
            )
    
    with tab2:
        # Generate trend data
        dates = pd.date_range(start=start_date, end=end_date, freq='M')
        waste_generated = np.random.normal(100, 20, len(dates))  # tons per month
        waste_collected = waste_generated * np.random.uniform(0.6, 0.8, len(dates))  # 60-80% collection
        recovery_rate = (waste_collected / waste_generated) * 100
        
        trend_df = pd.DataFrame({
            'Date': dates,
            'Waste Generated (tons)': waste_generated,
            'Waste Collected (tons)': waste_collected,
            'Recovery Rate (%)': recovery_rate
        })
        
        fig = px.line(trend_df, x='Date', y=['Waste Generated (tons)', 'Waste Collected (tons)'], 
                     title='Monthly Waste Generation vs Collection Trend')
        st.plotly_chart(fig, use_container_width=True)
        
        fig2 = px.line(trend_df, x='Date', y='Recovery Rate (%)', 
                      title='Monthly Recovery Rate Trend',
                      range_y=[0, 100])
        fig2.add_hline(y=target_recovery_rate, line_dash="dash", line_color="red", 
                       annotation_text=f"Target: {target_recovery_rate}%")
        st.plotly_chart(fig2, use_container_width=True)
    
    with tab3:
        st.subheader("EPR Compliance Reports")
        
        # Create mock report data
        report_data = {
            "Report Type": [
                "Quarterly EPR Report Q1",
                "Annual EPR Report FY 2023-24", 
                "Self Declaration Form",
                "EPR Certificate Application",
                "Annual Return to CPCB"
            ],
            "Due Date": [
                "2024-05-31",
                "2024-04-30",
                "2024-03-31", 
                "2024-02-29",
                "2024-07-31"
            ],
            "Status": [
                "✅ Submitted",
                "✅ Submitted",
                "✅ Submitted",
                "✅ Approved",
                "📅 Pending"
            ],
            "Action": [
                "Download",
                "Download", 
                "Download",
                "Download",
                "Submit"
            ]
        }
        
        reports_df = pd.DataFrame(report_data)
        st.dataframe(reports_df, use_container_width=True)
        
        st.subheader("Documentation Checklist")
        st.markdown("""
        - ✅ Producer registration certificate
        - ✅ EPR authorization from CPCB
        - ✅ Annual compliance report
        - ✅ Waste collection agreements
        - ✅ Recycling facility certifications
        - 📅 Quarterly progress reports
        """)
    
    with tab4:
        st.subheader("EPR Targets & Obligations")
        
        # Show obligations based on sector
        obligations = {
            "Plastic Packaging": [
                "Minimum 50% collection rate by 2024",
                "Maintain records of plastic waste",
                "Submit annual returns to SPCB",
                "Implement plastic waste management plan"
            ],
            "Electronics": [
                "Minimum 60% collection rate by 2023",
                "Establish collection centers",
                "Ensure environmentally sound dismantling",
                "Provide consumer awareness programs"
            ],
            "Batteries": [
                "Minimum 40% collection rate by 2023",
                "Register with Central Pollution Control Board",
                "Maintain producer responsibility organization",
                "Submit half-yearly returns"
            ],
            "Tyres": [
                "Minimum 80% collection rate by 2025",
                "Ensure authorized channel utilization",
                "Maintain dealer registration records",
                "Implement take-back system"
            ],
            "Paper": [
                "Minimum 70% collection rate by 2024",
                "Promote recycled paper usage",
                "Maintain waste management records",
                "Support waste paper collection"
            ],
            "Textiles": [
                "Minimum 30% collection rate by 2025",
                "Develop sustainable textile practices",
                "Promote circular economy models",
                "Implement textile waste management"
            ]
        }
        
        st.write(f"**Sector:** {industry_sector}")
        st.write(f"**Target Recovery Rate:** {target_recovery_rate}%")
        
        st.write("**Key Obligations:**")
        for obligation in obligations[industry_sector]:
            st.write(f"- {obligation}")
        
        # Progress toward target
        st.write("**Progress Tracking:**")
        
        # Simulated progress
        current_recovery = 63.4  # This would come from actual data
        
        fig_progress = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=current_recovery,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Recovery Rate vs Target ({target_recovery_rate}%)"},
            delta={'reference': target_recovery_rate},
            gauge={'axis': {'range': [None, 100]},
                   'bar': {'color': "darkblue"},
                   'steps': [
                       {'range': [0, 50], 'color': "lightgray"},
                       {'range': [50, 80], 'color': "yellow"},
                       {'range': [80, 100], 'color': "green"}],
                   'threshold': {
                       'line': {'color': "red", 'width': 4},
                       'thickness': 0.75,
                       'value': target_recovery_rate}}))
        
        st.plotly_chart(fig_progress, use_container_width=True)
    
    # Additional EPR information
    st.subheader("CPCB EPR Guidelines Summary")
    
    epr_guidelines = {
        "Legal Framework": [
            "E-Waste (Management) Rules, 2016",
            "Plastic Waste Management Rules, 2016",
            "Battery Waste Management Rules, 2022",
            "Tyre Waste Management Rules, 2018"
        ],
        "Key Requirements": [
            "Producer registration with CPCB/SPCB",
            "Setting up collection channels",
            "Ensuring environmentally sound management",
            "Maintaining detailed records",
            "Submitting periodic returns"
        ],
        "Penalties": [
            "Fine up to ₹50,000 for non-compliance",
            "Additional ₹5,000 per day for continuing violation",
            "Criminal liability under Environment Protection Act",
            "Cancellation of manufacturing license"
        ]
    }
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Legal Framework**")
        for item in epr_guidelines["Legal Framework"]:
            st.write(f"- {item}")
    
    with col2:
        st.write("**Key Requirements**")
        for item in epr_guidelines["Key Requirements"]:
            st.write(f"- {item}")
    
    with col3:
        st.write("**Penalties**")
        for item in epr_guidelines["Penalties"]:
            st.write(f"- {item}")
    
    # Contact for EPR compliance
    st.subheader("Need Help with EPR Compliance?")
    st.info("""
    Our platform can connect you with authorized EPR service providers and 
    help track your compliance metrics. Contact us for specialized EPR 
    consulting services tailored to your industry.
    """)
    
    if st.button("📞 Request EPR Consultation"):
        st.success("Thank you! Our EPR compliance team will contact you shortly.")

def main():
    """
    Main function to run the EPR dashboard
    """
    # Set page config
    st.set_page_config(
        page_title="EPR Compliance Dashboard - Circular AI",
        page_icon="🏭",
        layout="wide"
    )
    
    # Show the EPR dashboard
    show_epr_dashboard()

if __name__ == "__main__":
    main()