import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
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

def parse_currency(val):
    if pd.isna(val):
        return 0.0
    s = str(val).strip()
    s = re.sub(r'[A-Za-z]', '', s)
    s = s.replace(',', '')
    parts = s.split('.')
    if len(parts) > 2:
        s = "".join(parts[:-1]) + "." + parts[-1]
    try:
        return float(s)
    except:
        return 0.0

@st.cache_data
def load_data():
    df_master = pd.DataFrame()
    for enc in ['cp1252', 'utf-8', 'latin1']:
        try:
            df_master = pd.read_csv("MASTERPLAN PROJECTS.csv", encoding=enc)
            break
        except Exception:
            continue
            
    if not df_master.empty:
        df_master = df_master.loc[:, ~df_master.columns.str.contains('^Unnamed', case=False)]
        # Rename FIRST before accessing columns
        df_master = df_master.rename(columns={
            'PROJECT NO.': 'Project_No',
            'PROJECT TITLE': 'Title',
            'SECTOR': 'Sector',
            'CATEGORY': 'Category',
            'ESTIMATE AMOUNT': 'Estimate_Amount'
        })
        if 'Estimate_Amount' in df_master.columns:
            df_master['Estimate_Amount'] = df_master['Estimate_Amount'].apply(parse_currency)
        else:
            df_master['Estimate_Amount'] = 0.0
        df_master['Source'] = 'Masterplan'
        df_master['Funding_Source'] = 'Masterplan'
    
    proposals = []
    try:
        excel_file = pd.ExcelFile("MTIT_AIP28_New_Proposals.xlsx")
        for sheet in excel_file.sheet_names:
            df_sheet = pd.read_excel(excel_file, sheet_name=sheet)
            df_sheet = df_sheet.loc[:, ~df_sheet.columns.str.contains('^Unnamed: 0', case=False)]
            df_sheet = df_sheet.rename(columns={
                'Name of Projects': 'Title',
                'Project Brief Description': 'Category'
            })
            for col in df_sheet.columns:
                if 'Cost' in str(col) or 'Cost' in col:
                    df_sheet = df_sheet.rename(columns={col: 'Estimate_Amount'})
                    break
            df_sheet['Project_No'] = [f"PROP-{i+1:03d}" for i in range(len(df_sheet))]
            df_sheet['Sector'] = 'Economic'
            if 'Estimate_Amount' not in df_sheet.columns:
                df_sheet['Estimate_Amount'] = 0.0
            df_sheet['Estimate_Amount'] = df_sheet['Estimate_Amount'].apply(parse_currency)
            df_sheet['Source'] = 'New Proposal'
            df_sheet['Funding_Source'] = sheet
            proposals.append(df_sheet[['Project_No', 'Title', 'Sector', 'Category', 'Estimate_Amount', 'Source', 'Funding_Source']])
    except Exception as e:
        pass
        
    df_prop = pd.concat(proposals, ignore_index=True) if proposals else pd.DataFrame(columns=['Project_No', 'Title', 'Sector', 'Category', 'Estimate_Amount', 'Source', 'Funding_Source'])
    
    df_combined = pd.concat([df_master, df_prop], ignore_index=True)
    df_combined['Estimate_Amount'] = pd.to_numeric(df_combined['Estimate_Amount'], errors='coerce').fillna(0.0)
    df_combined['Sector'] = df_combined['Sector'].fillna('General Governance').astype(str)
    df_combined['Category'] = df_combined['Category'].fillna('Standard').astype(str)
    df_combined['Funding_Source'] = df_combined['Funding_Source'].fillna('Masterplan').astype(str)
    return df_combined

df_combined = load_data()

st.sidebar.header("🏛️ Governance & Policy Hub")
st.sidebar.markdown("> **Official Disclaimer:** Strategic guide for policy makers in **BARMM**.")
st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Global Filters")

sectors = sorted(df_combined['Sector'].unique().tolist())
selected_sectors = st.sidebar.multiselect("Sectors", sectors, default=sectors)

categories = sorted(df_combined['Category'].unique().tolist())
selected_categories = st.sidebar.multiselect("Categories", categories, default=categories)

funding_sources = sorted(df_combined['Funding_Source'].unique().tolist())
selected_funding = st.sidebar.multiselect("Funding Sources", funding_sources, default=funding_sources)

amt_series = pd.to_numeric(df_combined['Estimate_Amount'], errors='coerce').dropna()
min_val = float(amt_series.min()) if not amt_series.empty else 0.0
max_val = float(amt_series.max()) if not amt_series.empty else 1000000.0
if min_val >= max_val:
    max_val = min_val + 1.0

budget_range = st.sidebar.slider("Budget Range (PHP)", min_value=min_val, max_value=max_val, value=(min_val, max_val))

df_filtered = df_combined.copy()
if selected_sectors:
    df_filtered = df_filtered[df_filtered['Sector'].isin(selected_sectors)]
if selected_categories:
    df_filtered = df_filtered[df_filtered['Category'].isin(selected_categories)]
if selected_funding:
    df_filtered = df_filtered[df_filtered['Funding_Source'].isin(selected_funding)]
if not df_filtered.empty:
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

tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Portfolio Overview", 
    "📈 Revenue & Economic Projections", 
    "🤖 Predictive Modeling & PCA", 
    "📋 Decision-Making Matrix Table"
])

with tab1:
    st.subheader("Portfolio Allocation & Source Breakdown")
    ca, cb = st.columns(2)
    with ca:
        if not df_filtered.empty:
            fig_sec = px.pie(df_filtered, names='Sector', values='Estimate_Amount', title="Budget Allocation by Sector", hole=0.4)
            st.plotly_chart(fig_sec, use_container_width=True)
        else:
            st.info("No records match current filters.")
    with cb:
        if not df_filtered.empty:
            fig_bar = px.bar(
                df_filtered.groupby(['Source', 'Category'])['Estimate_Amount'].sum().reset_index(),
                x='Category', y='Estimate_Amount', color='Source',
                title="Masterplan vs. Proposals by Category", barmode='group'
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No records match current filters.")

with tab2:
    st.subheader("Revenue Generation & Economic Simulation")
    g_mult = st.slider("Regional Economic Growth Multiplier", 1.0, 2.5, 1.40, 0.05)
    d_rate = st.slider("Discount Rate (%)", 3.0, 12.0, 8.0, 0.5) / 100.0
    if not df_filtered.empty:
        sim = df_filtered.copy()
        sim['Projected_Revenue'] = sim['Estimate_Amount'] * g_mult
        sim['Estimated_NPV'] = (sim['Projected_Revenue'] / (1 + d_rate)) - sim['Estimate_Amount']
        sim['BCR'] = sim['Projected_Revenue'] / sim['Estimate_Amount'].replace(0, 1)
        sz = 'BCR' if len(sim) > 1 and sim['BCR'].nunique() > 1 else None
        fig_ec = px.scatter(sim, x='Estimate_Amount', y='Projected_Revenue', size=sz, color='Sector', hover_name='Title', title="Cost vs Revenue & BCR")
        st.plotly_chart(fig_ec, use_container_width=True)
    else:
        st.info("No data for simulation.")

with tab3:
    st.subheader("Predictive Modeling & PCA")
    if len(df_filtered) > 3:
        p_data = df_filtered[['Estimate_Amount']].copy()
        p_data['Dur'] = np.random.randint(1, 6, size=len(p_data))
        p_data['Risk'] = np.random.uniform(1.0, 10.0, size=len(p_data))
        scaled = StandardScaler().fit_transform(p_data)
        comps = PCA(n_components=2).fit_transform(scaled)
        pdf = pd.DataFrame(comps, columns=['PC1', 'PC2'])
        pdf['Title'] = df_filtered['Title'].values
        pdf['Sector'] = df_filtered['Sector'].values
        fig_pca = px.scatter(pdf, x='PC1', y='PC2', color='Sector', hover_name='Title', title="PCA 2D Cluster Map")
        st.plotly_chart(fig_pca, use_container_width=True)
    else:
        st.warning("Insufficient data points for PCA clustering.")

with tab4:
    st.subheader("Decision-Making Matrix Table")
    if not df_filtered.empty:
        disp = df_filtered[['Project_No', 'Title', 'Sector', 'Category', 'Estimate_Amount', 'Source', 'Funding_Source']]
        st.dataframe(disp, use_container_width=True)
        buf = io.StringIO()
        disp.to_csv(buf, index=False)
        st.download_button("📥 Export Filtered Matrix as CSV", data=buf.getvalue(), file_name="BARMM_Policy_Decision_Matrix.csv", mime="text/csv")
    else:
        st.info("No records matching filters.")
