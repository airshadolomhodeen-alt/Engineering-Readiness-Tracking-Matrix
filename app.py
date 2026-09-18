import streamlit as st
import pandas as pd
import plotly.express as px
import pydeck as pdk

# --- Page Config ---
st.set_page_config(
    page_title="PFEZ Executive Dashboard (2026–2040)",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Load Data Caching ---
@st.cache_data
def load_data():
    projects_df = pd.read_csv("data/pfez_projects.csv")
    zones_df = pd.read_csv("data/pfez_zones.csv")
    return projects_df, zones_df

projects_df, zones_df = load_data()

# --- Sidebar / Official Links & Filters ---
st.sidebar.image("https://bangsamoro.gov.ph/wp-content/uploads/2019/02/barmm-logo.png", width=80)
st.sidebar.title("PFEZ Command Center")
st.sidebar.markdown("**Polloc Freeport and Economic Zone (PFEZ)** Master Development Plan & Investment Program (2026–2040).")

st.sidebar.markdown("---")
st.sidebar.subheader("Global Filters")
selected_phase = st.sidebar.selectbox("Filter by Phase", ["All Phases", "Phase 1 (2026–2030)", "Phase 2 (2029–2035)", "Phase 3 (2032–2038)", "Phase 4 (2035–2040)"])

# Filter logic
if selected_phase != "All Phases":
    filtered_df = projects_df[projects_df["phase"] == selected_phase]
else:
    filtered_df = projects_df

st.sidebar.markdown("---")
st.sidebar.subheader("Official Portals")
st.sidebar.markdown("- [BARMM Official Portal](https://bangsamoro.gov.ph/)")
st.sidebar.markdown("- [BEZA Portal](https://beza.bangsamoro.gov.ph/news)")

# --- Main Dashboard Header ---
st.title("⚓ PFEZ Executive Monitoring Dashboard")
st.markdown("Monitor high-level metrics, implementation timelines, spatial zonings, and funding modalities under the Bangsamoro Economic Zone Authority (BEZA).")
st.markdown("---")

# --- 1. High-Level Summary KPIs ---
st.subheader("1. Top-Line Investment & Impact Metrics")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Portfolio", value="PhP 5.3 Billion", delta="95 PAPs Total")
with col2:
    st.metric(label="Phase 1 (2026-30)", value="PhP 264.4M", delta="39 PAPs")
with col3:
    st.metric(label="Phase 3 Peak Cap", value="PhP 3.0 Billion", delta="16 PAPs")
with col4:
    st.metric(label="Mangrove Conservation", value="40.0 Hectares", delta="Ecopark Zone")

# Secondary metric tier for Phases 2 & 4
sub_col1, sub_col2, sub_col3 = st.columns(3)
with sub_col1:
    st.metric(label="Phase 2 Allocation", value="PhP 2.0 Billion", delta="32 PAPs")
with sub_col2:
    st.metric(label="Phase 4 Allocation", value="PhP 167.6M", delta="8 PAPs")
with sub_col3:
    st.metric(label="Est. Job Generation", value="12,450 Jobs", delta="Target 2040")

st.markdown("---")

# --- 2. Implementation Phasing & Project Tracking Module ---
st.subheader("2. Implementation Phasing & Priority Tracking")

tab1, tab2 = st.tabs(["Interactive Timeline (Gantt)", "High-Priority Initiative Status"])

with tab1:
    st.markdown("Mapping execution schedules across the 2026–2040 roadmap.")
    fig_gantt = px.timeline(
        filtered_df, 
        x_start="start_year", 
        x_end="end_year", 
        y="project_name", 
        color="phase",
        title="Project Implementation Timeline (2026–2040)"
    )
    fig_gantt.update_yaxes(autorange="reversed")
    st.plotly_chart(fig_gantt, use_container_width=True)

with tab2:
    st.markdown("Status tracking for foundational and high-priority infrastructure initiatives.")
    st.dataframe(filtered_df[["project_name", "phase", "budget_php_m", "status", "priority_type"]], use_container_width=True)

st.markdown("---")

# --- 3. Spatial & Zoning Interactive Map Component ---
st.subheader("3. Spatial & Functional Zoning Map")
st.markdown("Visual breakdown of PFEZ's functional zones, port operations, and environmental buffers.")

# Pydeck Map Configuration
view_state = pdk.ViewState(latitude=7.3890, longitude=124.2600, zoom=13, pitch=30)
layer = pdk.Layer(
    "ScatterplotLayer",
    data=zones_df,
    get_position='[lon, lat]',
    get_color='[200, 30, 0, 160]',
    get_radius=150,
    pickable=True,
    auto_highlight=True
)

r = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{zone_name}\nType: {zone_type}\nArea: {area_hectares} Ha"})
st.pydeck_chart(r)

st.markdown("---")

# --- 4. Financial & PPP Modality Tracker ---
st.subheader("4. Financial Modality & Risk Assessment Matrix")

fin_col1, fin_col2 = st.columns(2)

with fin_col1:
    st.markdown("#### Funding Source Distribution")
    funding_data = pd.DataFrame({
        "Modality": ["BARMM Appropriations", "National Government", "ODA", "PPP / Private Sector"],
        "Share_PHP_B": [0.8, 1.5, 1.0, 2.0]
    })
    fig_pie = px.pie(funding_data, names="Modality", values="Share_PHP_B", hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with fin_col2:
    st.markdown("#### High-Risk / High-Value Mitigation Matrix")
    st.dataframe(projects_df[["project_name", "funding_modality", "risk_level"]], use_container_width=True)
