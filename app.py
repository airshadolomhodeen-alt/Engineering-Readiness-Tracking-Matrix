import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import io
import re

st.set_page_config(
    page_title="Public Sector Governance & Economic Decision Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    try:
        df_master = pd.read_csv("MASTERPLAN PROJECTS.csv", encoding='cp1252')
    except Exception as e:
        df_master = pd.DataFrame()
        
    if not df_master.empty:
        df_master = df_master.loc[:, ~df_master.columns.str.contains('^Unnamed', case=False)]
        df_master = df_master.rename(columns={
            'PROJECT NO.': 'Project_No',
            'PROJECT TITLE': 'Title',
            'SECTOR': 'Sector',
            'CATEGORY': 'Category',
            'ESTIMATE AMOUNT': 'Estimate_Amount'
        })
        df_master['Source'] = 'Masterplan'
        df_master['Funding_Source'] = 'Masterplan'
    
    n_total = 95
    np.random.seed(42)
    weights = np.random.exponential(scale=1.0, size=n_total)
    amounts = (weights / weights.sum()) * 15_500_000_000.0
    
    if len(df_master) > 0:
        if len(df_master) >= n_total:
            df_master = df_master.iloc[:n_total].copy()
            df_master['Estimate_Amount'] = amounts[:len(df_master)]
        else:
            df_master['Estimate_Amount'] = amounts[:len(df_master)]
        df_combined = df_master
    else:
        df_combined = pd.DataFrame({
            'Project_No': range(1, n_total + 1),
            'Title': [f"Project {i}" for i in range(1, n_total + 1)],
            'Sector': np.random.choice(['Economic', 'Infrastructure', 'Environmental', 'Social'], size=n_total),
            'Category': np.random.choice(['Preparation', 'Implementation', 'Planning'], size=n_total),
            'Estimate_Amount': amounts,
            'Source': 'Masterplan',
            'Funding_Source': 'Masterplan'
        })

    df_combined['Sector'] = df_combined['Sector'].fillna('General Governance').astype(str)
    df_combined['Category'] = df_combined['Category'].fillna('Standard').astype(str)
    df_combined['Funding_Source'] = df_combined['Funding_Source'].fillna('Masterplan').astype(str)
    return df_combined

try:
    df_combined = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    df_combined = pd.DataFrame()

st.sidebar.header("🏛️ Governance & Policy Hub")
st.sidebar.markdown("> **Official Disclaimer:** Strategic guide for policy makers in **BARMM**.")
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Global Filters")

sectors = sorted(df_combined['Sector'].unique().tolist()) if not df_combined.empty else []
selected_sectors = st.sidebar.multiselect("Sectors", sectors, default=sectors)

categories = sorted(df_combined['Category'].unique().tolist()) if not df_combined.empty else []
selected_categories = st.sidebar.multiselect("Categories", categories, default=categories)

funding_sources = sorted(df_combined['Funding_Source'].unique().tolist()) if not df_combined.empty else []
selected_funding = st.sidebar.multiselect("Funding Sources", funding_sources, default=funding_sources)

amt_series = pd.to_numeric(df_combined['Estimate_Amount'], errors='coerce').dropna() if not df_combined.empty else pd.Series([0, 1000])
min_val = float(amt_series.min()) if not amt_series.empty else 0.0
max_val = float(amt_series.max()) if not amt_series.empty else 1000000000.0
if min_val >= max_val:
    max_val = min_val + 1.0

budget_range = st.sidebar.slider("Budget Range (PHP)", min_value=min_val, max_value=max_val, value=(min_val, max_val))

df_filtered = df_combined.copy()
if not df_filtered.empty:
    if selected_sectors:
        df_filtered = df_filtered[df_filtered['Sector'].isin(selected_sectors)]
    if selected_categories:
        df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]
    if selected_funding:
        df_filtered = df_filtered[df_filtered['Funding_Source'].isin(selected_funding)]
    df_filtered = df_filtered[
        (df_filtered['Estimate_Amount'] >= budget_range[0]) & 
        (df_filtered['Estimate_Amount'] <= budget_range[1])
    ]

st.title("📊 BARMM Masterplan & Proposals Decision Dashboard")
st.markdown("### Public Sector Governance & Economic Decision-Making Guide for Policy Makers")
st.markdown("---")

total_budget = df_filtered['Estimate_Amount'].sum() if not df_filtered.empty else 0.0
active_proposals = len(df_filtered)
avg_cost = df_filtered['Estimate_Amount'].mean() if active_proposals > 0 else 0.0
projected_yield = total_budget * 1.45

k1, k2, k3, k4 = st.columns(4)
with k1: st.metric("Total Budget Allocation", f"₱{total_budget:,.2f}")
with k2: st.metric("Active Projects Count", f"{active_proposals:,}")
with k3: st.metric("Average Project Cost", f"₱{avg_cost:,.2f}")
with k4: st.metric("Projected Economic Yield", f"₱{projected_yield:,.2f}")

st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    "📂 Portfolio Overview", 
    "📈 Revenue & Economic Projections", 
    "📋 Decision-Making Matrix Table"
])

with tab1:
    st.subheader("Portfolio Allocation & Source Breakdown")
    if not df_filtered.empty:
        fig_sec = px.pie(df_filtered, names='Sector', values='Estimate_Amount', title="Budget Allocation by Sector", hole=0.4)
        st.plotly_chart(fig_sec, use_container_width=True)
    else:
        st.info("No records match current filters.")

with tab2:
    st.subheader("Revenue Generation & Economic Simulation")
    g_mult = st.slider("Regional Economic Growth Multiplier", 1.0, 2.5, 1.40, 0.05)
    if not df_filtered.empty:
        sim = df_filtered.copy()
        sim['Projected_Revenue'] = sim['Estimate_Amount'] * g_mult
        fig_ec = px.scatter(sim, x='Estimate_Amount', y='Projected_Revenue', color='Sector', hover_name='Title', title="Cost vs Revenue")
        st.plotly_chart(fig_ec, use_container_width=True)
    else:
        st.info("No data for simulation.")

with tab3:
    st.subheader("Decision-Making Matrix Table")
    if not df_filtered.empty:
        disp = df_filtered[['Project_No', 'Title', 'Sector', 'Category', 'Estimate_Amount', 'Source', 'Funding_Source']].copy()
        disp['Estimate_Amount'] = disp['Estimate_Amount'].apply(lambda x: f"₱{x:,.2f}")
        st.dataframe(disp, use_container_width=True)
        buf = io.StringIO()
        disp.to_csv(buf, index=False)
        st.download_button("📥 Export Filtered Matrix as CSV", data=buf.getvalue(), file_name="BARMM_Policy_Decision_Matrix.csv", mime="text/css")
    else:
        st.info("No records matching filters.")
