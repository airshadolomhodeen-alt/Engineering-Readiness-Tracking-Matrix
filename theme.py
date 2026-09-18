import streamlit as st

def apply_custom_theme():
    st.markdown("""
        <style>
        /* Executive Theme Color Palette */
        :root {
            --primary: #0f172a;
            --secondary: #1e3a8a;
            --accent: #3b82f6;
            --background: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #1e293b;
            --text-muted: #64748b;
            --border: #e2e8f0;
        }

        .main { background-color: var(--background); }
        
        /* Sidebar Professional Styling */
        [data-testid="stSidebar"] {
            background-color: #0f172a;
            color: #f1f5f9;
            border-right: 1px solid #1e293b;
        }
        [data-testid="stSidebar"] label, 
        [data-testid="stSidebar"] .stMarkdown,
        [data-testid="stSidebar"] .streamlit-expanderHeader {
            color: #cbd5e1 !important;
            font-weight: 500;
        }

        /* Typography & Headers */
        h1, h2, h3, h4 {
            color: #0f172a;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            font-weight: 700;
            letter-spacing: -0.025em;
        }

        /* Executive Header Banner */
        .pfez-header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #1d4ed8 100%);
            padding: 36px 40px;
            border-radius: 14px;
            color: white;
            margin-bottom: 28px;
            box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        .pfez-header h1 {
            color: #ffffff !important;
            font-size: 2.2rem;
            margin-bottom: 6px;
            font-weight: 800;
        }
        .pfez-header p {
            color: #93c5fd !important;
            font-size: 1.15rem;
            margin: 0px;
            font-weight: 500;
        }

        /* Metric Cards */
        div.stMetric {
            background-color: #ffffff;
            padding: 22px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
            border: 1px solid #e2e8f0;
            border-left: 5px solid #2563eb;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        div.stMetric:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
        }
        div.stMetric label {
            color: #64748b !important;
            font-weight: 600;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }
        div.stMetric [data-testid="stMetricValue"] {
            color: #0f172a !important;
            font-size: 1.7rem;
            font-weight: 800;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 12px;
            background-color: #e2e8f0;
            padding: 6px;
            border-radius: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            height: 42px;
            background-color: transparent;
            border-radius: 8px;
            color: #475569;
            font-weight: 600;
            padding: 0 20px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #ffffff !important;
            color: #0f172a !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }

        /* Dataframes & Tables */
        [data-testid="stDataFrame"] {
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.02);
        }
        </style>
    """, unsafe_allow_html=True)
