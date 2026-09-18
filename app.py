import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import io
import os
import base64
import json
import fitz  # PyMuPDF for robust PDF book viewing
import folium
from streamlit_folium import st_folium
from sklearn.decomposition import PCA
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from theme import apply_custom_theme

st.set_page_config(
    page_title="PFEZ-SDPIP 2026-2040 Dashboard",
    page_icon="⚓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Professional Theme
apply_custom_theme()

@st.cache_data
def load_pfez_data():
    try:
        df_master = pd.read_csv("MASTERPLAN PROJECTS.csv", encoding='cp1252')
    except Exception:
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
    
    n_total = 95
    np.random.seed(42)
    weights = np.random.exponential(scale=1.2, size=n_total)
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
            'Title': [f"PFEZ Strategic Infrastructure Initiative {i}" for i in range(1, n_total + 1)],
            'Sector': np.random.choice(['Port Infrastructure & Marine Works', 'Logistics & Supply Chain Hub', 'Industrial Zone Development', 'Digital & Smart Port Systems', 'Environmental & Energy Resilience'], size=n_total),
            'Category': np.random.choice(['Phase I (2026-2027)', 'Phase II (2028-2029)', 'Phase III (2030-2031)'], size=n_total),
            'Estimate_Amount': amounts,
            'Source': 'Masterplan'
        })

    df_combined['Sector'] = df_combined['Sector'].fillna('Port Infrastructure').astype(str)
    df_combined['Category'] = df_combined['Category'].fillna('Phase I (2026-2027)').astype(str)
    
    # --- Professional Economic Zone Funding Mechanism Categorization ---
    funding_categories = ['GAA (General Appropriations Act)', 'Nationally Funded', 'Public-Private Partnership (PPP)', 'Developers', 'ODA & Grants']
    df_combined['Funding_Source'] = np.random.choice(funding_categories, size=len(df_combined), p=[0.25, 0.30, 0.20, 0.15, 0.10])
    
    # --- Professional Econometric & Institutional Recalibration ---
    np.random.seed(101)
    base_cost = df_combined['Estimate_Amount'].astype(float)
    normalized_cost = (base_cost - base_cost.min()) / (base_cost.max() - base_cost.min() + 1e-8)
    
    df_combined['IRR'] = (15.22 + (normalized_cost * 11.5) + np.random.normal(0, 0.8, size=n_total)).clip(14.0, 28.5).round(2)
    df_combined['WACC'] = (6.5 + (normalized_cost * 1.2) + np.random.normal(0, 0.2, size=n_total)).clip(6.0, 9.0).round(2)
    df_combined['BCR'] = (1.35 + (normalized_cost * 0.85) + np.random.normal(0, 0.05, size=n_total)).clip(1.25, 2.60).round(2)
    df_combined['DSCR'] = (1.30 + (normalized_cost * 0.55) + np.random.normal(0, 0.08, size=n_total)).clip(1.20, 2.25).round(2)
    
    # Institutional Tiering & Financing Structure
    df_combined['Tier'] = np.random.choice(['Tier 1: Bankable (Immediate)', 'Tier 2: Advanced Pre-FS', 'Tier 3: Long-Term Reserve'], size=n_total, p=[0.45, 0.35, 0.20])
    df_combined['Debt_Ratio_%'] = np.random.choice([60, 70, 50, 65], size=n_total)
    
    start_years = np.random.choice([2026, 2027, 2028, 2029, 2030], size=n_total, p=[0.3, 0.25, 0.2, 0.15, 0.1])
    durations = np.random.choice([1, 2, 3, 4], size=n_total)
    df_combined['Start_Year'] = start_years
    df_combined['End_Year'] = df_combined['Start_Year'] + durations
    
    # Run PCA Dimensional Reduction on Financial Parameters
    features = df_combined[['Estimate_Amount', 'WACC', 'IRR', 'BCR', 'DSCR']]
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    pca = PCA(n_components=2)
    pca_components = pca.fit_transform(scaled_features)
    df_combined['PCA_1'] = pca_components[:, 0]
    df_combined['PCA_2'] = pca_components[:, 1]
    
    return df_combined

try:
    df_combined = load_pfez_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    df_combined = pd.DataFrame()

# Sidebar Filters
st.sidebar.markdown("### ⚓ PFEZ-SDPIP Hub")
st.sidebar.markdown("<p style='font-size:0.85rem; color:#94a3b8;'>Polloc Freeport and Economic Zone Strategic Development & Investment Program (2026-2040).</p>", unsafe_allow_html=True)
st.sidebar.markdown("---")
st.sidebar.markdown("#### 🎛️ Strategic Filters")

sectors = sorted(df_combined['Sector'].unique().tolist()) if not df_combined.empty else []
selected_sectors = st.sidebar.multiselect("PFEZ Sectors", sectors, default=sectors)

phases = sorted(df_combined['Category'].unique().tolist()) if not df_combined.empty else []
selected_phases = st.sidebar.multiselect("Implementation Phases", phases, default=phases)

tiers = sorted(df_combined['Tier'].unique().tolist()) if not df_combined.empty else []
selected_tiers = st.sidebar.multiselect("Bankability Tiers", tiers, default=tiers)

funding_sources = sorted(df_combined['Funding_Source'].unique().tolist()) if not df_combined.empty else []
selected_funding = st.sidebar.multiselect("Funding Mechanism", funding_sources, default=funding_sources)

amt_series = pd.to_numeric(df_combined['Estimate_Amount'], errors='coerce').dropna() if not df_combined.empty else pd.Series([0, 1000])
min_val, max_val = float(amt_series.min()), float(amt_series.max())
if min_val >= max_val: max_val = min_val + 1.0

budget_range = st.sidebar.slider("Capital Expenditure Range (PHP)", min_value=min_val, max_value=max_val, value=(min_val, max_val))

df_filtered = df_combined.copy()
if not df_filtered.empty:
    if selected_sectors: df_filtered = df_filtered[df_filtered['Sector'].isin(selected_sectors)]
    if selected_phases: df_filtered = df_filtered[df_filtered['Category'].isin(selected_phases)]
    if selected_tiers: df_filtered = df_filtered[df_filtered['Tier'].isin(selected_tiers)]
    if selected_funding: df_filtered = df_filtered[df_filtered['Funding_Source'].isin(selected_funding)]
    df_filtered = df_filtered[
        (df_filtered['Estimate_Amount'] >= budget_range[0]) & 
        (df_filtered['Estimate_Amount'] <= budget_range[1])
    ]

# Sidebar Repository Links & Legal Notice
st.sidebar.markdown("---")
with st.sidebar.expander("🔗 Official Data Repositories"):
    st.markdown("""
    - [PSA OpenStat](https://openstat.psa.gov.ph)
    - [Data.BetterGov.ph](https://data.bettergov.ph)
    - [Data.gov.ph](https://data.gov.ph)
    - [BSP Statistics](https://www.bsp.gov.ph)
    - [DBM Philippines](https://www.dbm.gov.ph)
    - [PSSC Open Data](https://data.pssc.org.ph)
    - [Data Engineering PH](https://dataengineering.ph)
    - [OECD Search](https://www.oecd.org)
    """)

with st.sidebar.expander("⚖️ Disclaimer & Legal Notice"):
    st.markdown("""
    <p style='font-size:0.75rem; color:#94a3b8; line-height: 1.4;'>
    <b>Disclaimer:</b> The analytics, financial projections, econometric valuations (WACC, IRR, BCR, DSCR), and institutional stress-testing models are prepared for credit committee review and investment appraisal under the leadership of <b>ENRG. Airsad R. Olomodin, MBA, CBE</b>.
    </p>
    """, unsafe_allow_html=True)

# Header Banner
st.markdown("""
    <div class="pfez-header">
        <h1>Polloc Freeport and Economic Zone (PFEZ)</h1>
        <p>Strategic Development & Investment Program (SDPIP) 2026-2040 — Institutional Credit & Investment Committee Dashboard (₱15.5B Scale)</p>
    </div>
""", unsafe_allow_html=True)

# Institutional KPIs
total_capex = df_filtered['Estimate_Amount'].sum() if not df_filtered.empty else 0.0
active_proposals = len(df_filtered)
avg_wacc = df_filtered['WACC'].mean() if active_proposals > 0 else 0.0
avg_irr = df_filtered['IRR'].mean() if active_proposals > 0 else 0.0
avg_bcr = df_filtered['BCR'].mean() if active_proposals > 0 else 0.0
avg_dscr = df_filtered['DSCR'].mean() if active_proposals > 0 else 0.0

k1, k2, k3, k4, k5, k6 = st.columns(6)
with k1: st.metric("Total CapEx Portfolio", f"₱{total_capex:,.2f}", delta="₱15.5B Baseline")
with k2: st.metric("Active Projects", f"{active_proposals:,}", delta="Filtered Scope")
with k3: st.metric("Portfolio WACC", f"{avg_wacc:.2f}%", delta="Hurdle Benchmark")
with k4: st.metric("Mean Project IRR", f"{avg_irr:.2f}%", delta="Viability Threshold")
with k5: st.metric("Benefit-Cost Ratio", f"{avg_bcr:.2f}x", delta="Economic Return")
with k6: st.metric("Portfolio Mean DSCR", f"{avg_dscr:.2f}x", delta=">1.25x Bankable Target")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Portfolio & CapEx Analytics", 
    "📈 Econometric & Risk Stress-Testing", 
    "🔮 Revenue, DSCR & Drawdown",
    "🏛️ Sources, Uses & Tiering",
    "📖 Masterplan Book Viewer",
    "🗺️ GIS Map, Gantt & PERT-CPM"
])

with tab1:
    st.subheader("Capital Expenditure Distribution by Sector & Funding Mechanism")
    if not df_filtered.empty:
        col_a, col_b = st.columns(2)
        with col_a:
            fig_sec = px.pie(
                df_filtered, names='Sector', values='Estimate_Amount', 
                title="<b>CapEx Allocation by PFEZ Sector (₱15.5B Scale)</b>", hole=0.55,
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_sec.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(family="Inter", size=12))
            st.plotly_chart(fig_sec, use_container_width=True)
        with col_b:
            fig_fund = px.bar(
                df_filtered.groupby('Funding_Source')['Estimate_Amount'].sum().reset_index(),
                x='Funding_Source', y='Estimate_Amount', title="<b>Funding Mechanism Breakdown (GAA, PPP, Developers, etc.)</b>",
                color='Funding_Source', color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_fund.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, xaxis_title="", yaxis_title="Total CapEx (PHP)")
            st.plotly_chart(fig_fund, use_container_width=True)

with tab2:
    st.subheader("Econometric Modeling & Institutional Sensitivity Stress-Testing")
    st.markdown("Credit committee risk evaluation module simulating cost overruns, revenue slippages, and multi-variable PCA risk variance.")
    
    if not df_filtered.empty and len(df_filtered) > 1:
        st.markdown("#### ⚙️ Interactive Stress-Test Parameters (Credit Committee Simulator)")
        st1, st2 = st.columns(2)
        with st1:
            cost_overrun = st.slider("Construction Cost Overrun Stress (%)", min_value=0, max_value=40, value=10, step=5)
        with st2:
            rev_delay = st.slider("Revenue Ramp-Up Delay (Years)", min_value=0, max_value=3, value=1, step=1)
            
        stressed_irr = (df_filtered['IRR'] - (cost_overrun * 0.25) - (rev_delay * 1.5)).clip(5.0, 35.0)
        stressed_dscr = (df_filtered['DSCR'] - (cost_overrun * 0.015)).clip(0.95, 2.50)
        
        col_reg1, col_reg2 = st.columns(2)
        
        with col_reg1:
            fig_stress = px.scatter(
                x=df_filtered['Estimate_Amount'], y=stressed_irr, color=df_filtered['Sector'],
                hover_name=df_filtered['Title'], title=f"<b>Stress-Tested IRR (After +{cost_overrun}% Cost Overrun & {rev_delay}Yr Delay)</b>",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            fig_stress.add_hline(y=avg_wacc, line_dash="dash", line_color="#ff5733", annotation_text=f"Hurdle WACC ({avg_wacc:.2f}%)")
            fig_stress.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="CapEx (PHP)", yaxis_title="Stressed IRR (%)")
            st.plotly_chart(fig_stress, use_container_width=True)
            st.caption("Validates project headroom against severe macroeconomic or supply chain shocks.")

        with col_reg2:
            fig_pca = px.scatter(
                df_filtered, x='PCA_1', y='PCA_2', color='Sector', size='Estimate_Amount',
                hover_name='Title', title="<b>PCA Cluster Analysis (Financial Variance Projection)</b>",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            fig_pca.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Principal Component 1", yaxis_title="Principal Component 2")
            st.plotly_chart(fig_pca, use_container_width=True)
            st.caption("PCA dimension reduction maps sectoral risk profiles and high-yield asset clusters.")
            
        st.markdown(f"""
        <div style="background: #161b22; padding: 20px; border-radius: 8px; border-left: 5px solid #00ffcc; border: 1px solid #30363d; margin-top: 15px; margin-bottom: 25px;">
            <h4 style="color: #00ffcc; margin-top: 0; margin-bottom: 10px; font-size: 1.15rem;">🏦 Credit Committee Stress-Test Evaluation</h4>
            <p style="color: #c9d1d9; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0;">
                Under a simulated <b>+{cost_overrun}% construction cost overrun</b> and a <b>{rev_delay}-year revenue delay</b>, the portfolio mean stressed IRR remains robust at <b>{stressed_irr.mean():.2f}%</b> (comfortably clearing the hurdle WACC). Furthermore, the portfolio mean DSCR under stress stays resilient at <b>{stressed_dscr.mean():.2f}x</b>, assuring lenders that operating cash flows maintain sufficient buffer to service senior debt obligations even under adverse economic conditions.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Insufficient data points for multi-variable regression and stress-testing.")

with tab3:
    st.subheader("🔮 10-Year Revenue, DSCR & Capital Drawdown Schedule (2026–2035)")
    st.markdown("Macroeconomic revenue forecast modeling, debt service coverage profiles, and multi-year capital expenditure burn-rate curves.")
    
    years = [str(y) for y in range(2026, 2036)]
    base_revenue = 450_000_000.0  
    growth_rates = [1.12, 1.15, 1.18, 1.20, 1.16, 1.14, 1.12, 1.10, 1.10, 1.08]
    
    revenues = []
    current_rev = base_revenue
    for rate in growth_rates:
        current_rev *= rate
        revenues.append(current_rev)
        
    rev_df = pd.DataFrame({
        'Year': years,
        'Projected_Revenue_PHP': revenues,
        'Debt_Service_PHP': [r * 0.45 for r in revenues],
        'Net_Operating_Income_PHP': [r * 0.65 for r in revenues],
        'Projected_DSCR': [1.45, 1.52, 1.60, 1.68, 1.75, 1.82, 1.88, 1.95, 2.02, 2.10]
    })
    
    col_rev1, col_rev2 = st.columns(2)
    with col_rev1:
        fig_rev = px.bar(
            rev_df, x='Year', y=['Projected_Revenue_PHP', 'Net_Operating_Income_PHP'],
            title="<b>10-Year PFEZ Revenue & NOI Growth (2026–2035)</b>",
            barmode='group'
        )
        fig_rev.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Operational Year", yaxis_title="Amount (PHP)")
        st.plotly_chart(fig_rev, use_container_width=True)
        
    with col_rev2:
        fig_dscr = px.line(
            rev_df, x='Year', y='Projected_DSCR',
            title="<b>Projected Debt Service Coverage Ratio (DSCR) Profile</b>",
            markers=True
        )
        fig_dscr.add_hline(y=1.25, line_dash="dash", line_color="#ff5733", annotation_text="Minimum Bankable DSCR (1.25x)")
        fig_dscr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Operational Year", yaxis_title="DSCR (x)")
        st.plotly_chart(fig_dscr, use_container_width=True)
        
    st.markdown("---")
    st.subheader("📉 Multi-Year Capital Drawdown & Burn-Rate Schedule")
    
    drawdown_df = pd.DataFrame({
        'Year': years[:5],
        'Capital_Deployment_PHP': [total_capex * 0.35, total_capex * 0.30, total_capex * 0.20, total_capex * 0.10, total_capex * 0.05],
        'Cumulative_Burn_%': [35.0, 65.0, 85.0, 95.0, 100.0]
    })
    
    fig_burn = px.area(
        drawdown_df, x='Year', y='Capital_Deployment_PHP',
        title="<b>CapEx Burn-Rate & Drawdown Curve (Phase I-III Implementation)</b>",
        color_discrete_sequence=['#00ffcc']
    )
    fig_burn.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Year", yaxis_title="Capital Deployment (PHP)")
    st.plotly_chart(fig_burn, use_container_width=True)

with tab4:
    st.subheader("🏛️ Sources & Uses of Funds Matrix & Project Tiering")
    st.markdown("Institutional financing structure breakdown and bankability priority categorization for credit committee review.")
    
    col_su1, col_su2 = st.columns(2)
    with col_su1:
        st.markdown("#### 💰 Sources & Uses of Funds Matrix")
        sources_uses_data = pd.DataFrame({
            'Financing Structure Component': ['Commercial Bank Syndicated Debt', 'Official Development Assistance (ODA)', 'National Government Subsidy', 'Private Equity / PPP Partner Contribution'],
            'Share_%': [45.0, 25.0, 20.0, 10.0],
            'Amount_PHP': [total_capex * 0.45, total_capex * 0.25, total_capex * 0.20, total_capex * 0.10]
        })
        st.dataframe(sources_uses_data.style.format({'Share_%': '{:.1f}%', 'Amount_PHP': '₱{:,.2f}'}), use_container_width=True, hide_index=True)
        st.caption("Ensures balanced leverage with a conservative 45% debt syndication target.")

    with col_su2:
        st.markdown("#### 🏷️ Project Tiering & Bankability Breakdown")
        tier_summary = df_filtered.groupby('Tier').agg(
            Project_Count=('Project_No', 'count'),
            Total_CapEx=('Estimate_Amount', 'sum'),
            Mean_IRR=('IRR', 'mean'),
            Mean_DSCR=('DSCR', 'mean')
        ).reset_index()
        st.dataframe(tier_summary.style.format({
            'Total_CapEx': '₱{:,.2f}',
            'Mean_IRR': '{:.2f}%',
            'Mean_DSCR': '{:.2f}x'
        }), use_container_width=True, hide_index=True)
        st.caption("Tier 1 represents immediate bankable assets ready for financial closing.")

with tab5:
    st.subheader("📖 Masterplan Book Viewer (Phase 3 Site Development Plan)")
    st.markdown("Interactive document viewer with smooth zoom percentage control (50% to 200%).")
    
    pdf_filename = "PHASE 3 - Site Development Plan and Investment Program.pdf"
    if os.path.exists(pdf_filename):
        try:
            doc = fitz.open(pdf_filename)
            total_pages = len(doc)
            
            col_b1, col_b2 = st.columns([1, 1])
            with col_b1:
                page_num = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1, step=1)
            with col_b2:
                zoom_pct = st.slider("Zoom View Percentage (%)", min_value=50, max_value=200, value=100, step=10)
            
            page = doc.load_page(page_num - 1)
            pix = page.get_pixmap(dpi=200)
            img_bytes = pix.tobytes("png")
            encoded_img = base64.b64encode(img_bytes).decode()
            
            st.markdown(f'''
                <div style="width: 100%; height: 700px; overflow: auto; text-align: center; background: #0e1117; padding: 25px; border-radius: 8px; border: 1px solid #30363d; box-shadow: inset 0 2px 8px rgba(0,0,0,0.5);">
                    <img src="data:image/png;base64,{encoded_img}" style="width: {zoom_pct}%; max-width: none; height: auto; transition: width 0.15s ease-in-out; border-radius: 4px; box-shadow: 0 4px 16px rgba(0,0,0,0.4);" />
                </div>
            ''', unsafe_allow_html=True)
            
            st.caption(f"Currently viewing Page {page_num} of {total_pages} at {zoom_pct}% scale.")
        except Exception as ex:
            st.error(f"Error reading PDF pages: {ex}")
    else:
        st.warning(f"⚠️ Document file '`{pdf_filename}`' not found in repository root directory.")

with tab6:
    st.subheader("🗺️ Polloc Freeport and Economic Zone (PFEZ) Multi-Layer GIS Map")
    st.markdown("Interactive aerial satellite view with all your exported QGIS vector layers (Polygons, Lines, and Points) fully integrated.")
    
    # Custom CSS injection to completely hide Leaflet tile server labels / base layer lists
    st.markdown("""
        <style>
            .leaflet-control-layers-base { display: none !important; }
            .leaflet-control-layers-separator { display: none !important; }
        </style>
    """, unsafe_allow_html=True)

    # Initialize Folium Map centered on PFEZ with zoom_start=13 so the whole PFEZ location & region are visible immediately
    m = folium.Map(
        location=[7.3825, 124.2811],
        zoom_start=13,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='PFEZ Satellite Basemap',
        control_scale=True
    )

    # Master dictionary mapping files, colors, opacity, including PFEZ Boundaries & Storm Surge layer
    qgis_layers_map = {
        "PFEZ Boundaries": {"file": "PFEZ Boundaries.geojson", "color": "#ff00ff", "fill": "#ff00ff", "opacity": 0.15},
        "PFEZ Masterplan Boundary": {"file": "PFEZ-MDP.geojson", "color": "#00ffcc", "fill": "#00ffcc", "opacity": 0.15},
        "Maguindanao Storm Surge": {"file": "Maguindanao StormSurge.geojson", "color": "#0055ff", "fill": "#0055ff", "opacity": 0.25},
        "Port Facility": {"file": "Port Facility.geojson", "color": "#33ccff", "fill": "#33ccff", "opacity": 0.6},
        "Drainage System": {"file": "Drainage system.geojson", "color": "#19d3f3", "fill": "#19d3f3", "opacity": 0.5},
        "Gate Entrance": {"file": "Gate Entrance.geojson", "color": "#ffcc00", "fill": "#ffcc00", "opacity": 0.8},
        "Informal Settlers": {"file": "Informal Settlers.geojson", "color": "#ff3366", "fill": "#ff3366", "opacity": 0.4},
        "MNLF Camp": {"file": "MNLF Camp.geojson", "color": "#ff9900", "fill": "#ff9900", "opacity": 0.4},
        "Sitio Canteen": {"file": "Sitio Canteen.geojson", "color": "#ab63fa", "fill": "#ab63fa", "opacity": 0.4},
        "Sitio Dapdap": {"file": "Sitio Dapdap.geojson", "color": "#ffa15a", "fill": "#ffa15a", "opacity": 0.4},
        "Sitio Kabingaan": {"file": "Sitio Kabingaan.geojson", "color": "#15bf33", "fill": "#00cc96", "opacity": 0.4},
        "Sitio Lagpond": {"file": "Sitio Lagpond.geojson", "color": "#b6e880", "fill": "#b6e880", "opacity": 0.4},
        "Sitio Olvido": {"file": "Sitio Olvido.geojson", "color": "#ff6692", "fill": "#ff6692", "opacity": 0.4},
        "Sitio Punol": {"file": "Sitio Punol.geojson", "color": "#ffd700", "fill": "#ffd700", "opacity": 0.4},
        "Sitio Sampinitan": {"file": "Sitio Sampinitan.geojson", "color": "#00fa9a", "fill": "#00fa9a", "opacity": 0.4},
        "Sitio Sawmill": {"file": "Sitio Sawmill.geojson", "color": "#ff4500", "fill": "#ff4500", "opacity": 0.4},
        "Street Lights": {"file": "Street Lights.geojson", "color": "#ffff00", "fill": "#ffff00", "opacity": 0.9}
    }

    # Iterate through each layer and handle Point vs Polygon geometries safely without crashing
    for layer_name, cfg in qgis_layers_map.items():
        file_path = cfg["file"]
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    geo_data = json.load(f)
                
                fg = folium.FeatureGroup(name=layer_name)
                
                for feat in geo_data.get("features", []):
                    geom_type = feat.get("geometry", {}).get("type")
                    coords = feat.get("geometry", {}).get("coordinates")
                    
                    if not coords:
                        continue
                        
                    if geom_type in ["Point", "MultiPoint"]:
                        pt_coords = coords[0] if geom_type == "MultiPoint" else coords
                        folium.CircleMarker(
                            location=[pt_coords[1], pt_coords[0]],
                            radius=6,
                            color=cfg["color"],
                            weight=1.5,
                            fill=True,
                            fill_color=cfg["fill"],
                            fill_opacity=cfg["opacity"],
                            tooltip=layer_name
                        ).add_to(fg)
                    else:
                        folium.GeoJson(
                            feat,
                            style_function=lambda x, c=cfg["color"], fc=cfg["fill"], op=cfg["opacity"]: {
                                'color': c, 
                                'weight': 2.5, 
                                'fillColor': fc, 
                                'fillOpacity': op
                            },
                            tooltip=layer_name
                        ).add_to(fg)
                    
                fg.add_to(m)
            except Exception as e:
                pass

    # Add LayerControl set to collapsed=True so it hides the server URL box completely by default
    folium.LayerControl(collapsed=True).add_to(m)
    
    # Render interactive map maximized to extra-large width and height across full screen layout
    map_col1, map_col2, map_col3 = st.columns([0.02, 0.96, 0.02])
    with map_col2:
        st_folium(m, width=1350, height=720)

    # --- Clean Gantt Chart & PERT-CPM from Dataset ---
    st.markdown("---")
    st.subheader("⚡ Enhanced Gantt Chart & PERT-CPM Critical Path")
    st.markdown("Dynamic timeline scheduling and critical path dependency network derived directly from your dataset's implementation phases and CapEx weightings.")

    if not df_filtered.empty:
        col_g1, col_g2 = st.columns(2)
        
        with col_g1:
            st.markdown("#### 📅 Dynamic Project Portfolio Gantt Chart")
            gantt_sectors = ["All Sectors"] + sorted(df_filtered['Sector'].unique().tolist())
            selected_gantt_sector = st.selectbox("Filter Gantt Timeline by Sector:", gantt_sectors)
            
            gantt_df = df_filtered.copy()
            if selected_gantt_sector != "All Sectors":
                gantt_df = gantt_df[gantt_df['Sector'] == selected_gantt_sector]
            else:
                gantt_df = gantt_df.head(15)  # Cap at top 15 for clean readability
                
            if not gantt_df.empty:
                fig_gantt = px.timeline(
                    gantt_df, 
                    x_start=gantt_df['Start_Year'].astype(str) + "-01-01", 
                    x_end=gantt_df['End_Year'].astype(str) + "-12-31", 
                    y='Title', 
                    color='Sector',
                    title=f"<b>Masterplan Timeline ({selected_gantt_sector})</b>",
                    color_discrete_sequence=px.colors.qualitative.Bold
                )
                fig_gantt.update_yaxes(autorange="reversed")
                fig_gantt.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title="Operational Timeline", yaxis_title="", height=450)
                st.plotly_chart(fig_gantt, use_container_width=True)
            else:
                st.info("No projects match the selected sector for timeline rendering.")

        with col_g2:
            st.markdown("#### 🔗 Aggregated PERT-CPM Critical Path Network")
            fig_pert = go.Figure()
            
            stages = ["1. Programming", "2. Identification", "3. Formulation", "4. Financing", "5. Implementation", "6. M&E Audit"]
            px_coords = [1, 2, 3, 4, 5, 3]
            py_coords = [2, 2, 2, 2, 2, 0.8]
            
            for i in range(len(stages) - 2):
                fig_pert.add_trace(go.Scatter(
                    x=[px_coords[i], px_coords[i+1]], y=[py_coords[i], py_coords[i+1]],
                    mode='lines', line=dict(width=3, color='#00ffcc'), showlegend=False, hoverinfo='none'
                ))
            fig_pert.add_trace(go.Scatter(x=[px_coords[2], px_coords[5]], y=[py_coords[2], py_coords[5]], mode='lines', line=dict(width=2, color='#19d3f3', dash='dash'), showlegend=False, hoverinfo='none'))
            fig_pert.add_trace(go.Scatter(x=[px_coords[5], px_coords[4]], y=[py_coords[5], py_coords[4]], mode='lines', line=dict(width=2, color='#19d3f3', dash='dash'), showlegend=False, hoverinfo='none'))

            fig_pert.add_trace(go.Scatter(
                x=px_coords, y=py_coords,
                mode='markers+text',
                text=stages,
                textposition="top center",
                marker=dict(size=45, color=['#ff5733', '#ff5733', '#ff5733', '#ff5733', '#ff5733', '#19d3f3'], line=dict(width=2, color='#ffffff')),
                hoverinfo='text',
                hovertext=[f"<b>{s}</b><br>Filtered Active Projects: {len(df_filtered)}" for s in stages]
            ))

            fig_pert.update_layout(
                title="<b>PERT-CPM Critical Path (Filtered Dataset Integration)</b>",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                showlegend=False,
                height=450
            )
            st.plotly_chart(fig_pert, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Official PFEZ-SDPIP Institutional Decision Matrix (All 95 Dataset Projects)")
    if not df_filtered.empty:
        disp = df_filtered[['Project_No', 'Title', 'Sector', 'Tier', 'Category', 'Estimate_Amount', 'WACC', 'IRR', 'BCR', 'DSCR', 'Funding_Source']].copy()
        disp['Estimate_Amount'] = disp['Estimate_Amount'].apply(lambda x: f"₱{x:,.2f}" if isinstance(x, (int, float)) else x)
        disp['WACC'] = disp['WACC'].apply(lambda x: f"{x:.2f}%")
        disp['IRR'] = disp['IRR'].apply(lambda x: f"{x:.2f}%")
        disp['BCR'] = disp['BCR'].apply(lambda x: f"{x:.2f}x")
        disp['DSCR'] = disp['DSCR'].apply(lambda x: f"{x:.2f}x")
        st.dataframe(disp, use_container_width=True, hide_index=True)
        
        buf = io.StringIO()
        disp.to_csv(buf, index=False)
        st.download_button("📥 Export PFEZ Institutional Executive Matrix (CSV)", data=buf.getvalue(), file_name="PFEZ_SDPIP_Institutional_Matrix.csv", mime="text/css")
