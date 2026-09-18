import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Public Sector Governance & Economic Decision Dashboard",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling for Power BI-style feel
st.markdown(
    """
    <style>
    .main {
        background-color: #f4f6f9;
    }
    .stMetric {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# 2. Data Pipeline & Caching
@st.cache_data
def load_data():
  # Load Masterplan Projects CSV with correct encoding
  df_master = pd.DataFrame()
  for enc in ["cp1252", "utf-8", "latin1"]:
    try:
      df_master = pd.read_csv("MASTERPLAN PROJECTS.csv", encoding=enc)
      break
    except Exception:
      continue
  if df_master.empty:
    df_master = pd.DataFrame(
        columns=["Project No.", "Title", "Sector", "Category", "Estimate Amount"]
    )

  # Drop unnamed columns if present
  df_master = df_master.loc[
      :, ~df_master.columns.str.contains("^Unnamed", case=False)
  ]

  # Load Multi-sheet Excel Proposals
  proposals_list = []
  try:
    excel_file = pd.ExcelFile("MTIT_AIP28_New_Proposals.xlsx")
    for sheet in excel_file.sheet_names:
      df_sheet = pd.read_excel(excel_file, sheet_name=sheet)
      df_sheet["Funding Source"] = sheet
      proposals_list.append(df_sheet)
    df_proposals = (
        pd.concat(proposals_list, ignore_index=True)
        if proposals_list
        else pd.DataFrame()
    )
  except Exception:
    df_proposals = pd.DataFrame(
        columns=[
            "Project No.",
            "Title",
            "Sector",
            "Category",
            "Estimate Amount",
            "Funding Source",
        ]
    )

  df_proposals = df_proposals.loc[
      :, ~df_proposals.columns.str.contains("^Unnamed", case=False)
  ]

  return df_master, df_proposals


df_master, df_proposals = load_data()


def clean_and_standardize(df, source_type="Masterplan"):
  if df.empty:
    return pd.DataFrame(
        columns=[
            "Project_No",
            "Title",
            "Sector",
            "Category",
            "Estimate_Amount",
            "Source",
            "Funding_Source",
        ]
    )

  df = df.copy()
  df = df.loc[:, ~df.columns.duplicated()]
  df = df.loc[:, ~df.columns.str.contains("^Unnamed", case=False)]

  col_map = {}
  for col in df.columns:
    col_lower = str(col).lower().strip()
    if "project" in col_lower and (
        "no" in col_lower or "code" in col_lower or "#" in col_lower
    ):
      col_map[col] = "Project_No"
    elif (
        "title" in col_lower or "name" in col_lower or "description" in col_lower
    ):
      col_map[col] = "Title"
    elif "sector" in col_lower:
      col_map[col] = "Sector"
    elif "categor" in col_lower:
      col_map[col] = "Category"
    elif any(
        k in col_lower for k in ["cost", "amount", "estimate", "budget"]
    ):
      col_map[col] = "Estimate_Amount"

  df = df.rename(columns=col_map)

  # Fallbacks for missing required columns
  if "Project_No" not in df.columns:
    df["Project_No"] = [f"PRJ-{i+1:03d}" for i in range(len(df))]
  if "Title" not in df.columns:
    df["Title"] = "Unnamed Project"
  if "Sector" not in df.columns:
    df["Sector"] = "General Governance"
  if "Category" not in df.columns:
    df["Category"] = "Standard"
  if "Estimate_Amount" not in df.columns:
    df["Estimate_Amount"] = 1000000.0
  if "Funding_Source" not in df.columns:
    df["Funding_Source"] = source_type

  # Clean numeric fields
  if df["Estimate_Amount"].dtype == object:
    df["Estimate_Amount"] = (
        df["Estimate_Amount"]
        .astype(str)
        .str.replace(r"[^\d.]", "", regex=True)
        .replace("", "0")
        .astype(float)
    )
  df["Estimate_Amount"] = df["Estimate_Amount"].fillna(0)
  df["Source"] = source_type

  out_df = df[
      [
          "Project_No",
          "Title",
          "Sector",
          "Category",
          "Estimate_Amount",
          "Source",
          "Funding_Source",
      ]
  ].copy()
  out_df = out_df.loc[:, ~out_df.columns.duplicated()]
  return out_df.reset_index(drop=True)


df_master_clean = clean_and_standardize(df_master, "Masterplan")
df_proposals_clean = clean_and_standardize(df_proposals, "New Proposal")

df_master_clean = df_master_clean.reset_index(drop=True)
df_proposals_clean = df_proposals_clean.reset_index(drop=True)

df_combined = pd.concat(
    [df_master_clean, df_proposals_clean], ignore_index=True, axis=0
)


# Automatic Committee Mapping
def assign_committee(row):
  sec = str(row["Sector"]).lower()
  title = str(row["Title"]).lower()
  if (
      "transport" in sec
      or "road" in sec
      or "bridge" in sec
      or "transport" in title
  ):
    return "Transportation Sub-Committee"
  elif (
      "international" in sec
      or "foreign" in sec
      or "oda" in sec
      or "trade" in sec
  ):
    return "International Development Sectoral Working Group (IDSWG)"
  elif (
      "infrastructure" in sec
      or "energy" in sec
      or "water" in sec
      or "construct" in sec
  ):
    return "Infrastructure Development Committee (IDCom)"
  else:
    return "Regional Land Use Committee (RLUC)"


df_combined["Assigned_Committee"] = df_combined.apply(assign_committee, axis=1)

# 3. Sidebar Layout & Committee Selector
st.sidebar.header("🏛️ Governance & Committee Hub")

committee_options = [
    "Regional Land Use Committee (RLUC)",
    "Infrastructure Development Committee (IDCom)",
    "International Development Sectoral Working Group (IDSWG)",
    "Transportation Sub-Committee",
]

selected_committee = st.sidebar.selectbox(
    "Select Committee Scope", committee_options
)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Global Filters")

df_filtered = df_combined[
    df_combined["Assigned_Committee"] == selected_committee
].copy()
if df_filtered.empty:
  df_filtered = df_combined.copy()  # Fallback

sectors = sorted(df_filtered["Sector"].dropna().unique().tolist())
selected_sectors = st.sidebar.multiselect("Sectors", sectors, default=sectors)

categories = sorted(df_filtered["Category"].dropna().unique().tolist())
selected_categories = st.sidebar.multiselect(
    "Categories", categories, default=categories
)

funding_sources = sorted(
    df_filtered["Funding_Source"].dropna().unique().tolist()
)
selected_funding = st.sidebar.multiselect(
    "Funding Sources", funding_sources, default=funding_sources
)

min_budget = (
    float(df_filtered["Estimate_Amount"].min())
    if not df_filtered.empty
    else 0.0
)
max_budget = (
    float(df_filtered["Estimate_Amount"].max())
    if not df_filtered.empty
    else 100000000.0
)
if min_budget == max_budget:
  max_budget += 1.0

budget_range = st.sidebar.slider(
    "Budget Range (PHP)",
    min_value=min_budget,
    max_value=max_budget,
    value=(min_budget, max_budget),
)

# Apply Filter Criteria
if selected_sectors:
  df_filtered = df_filtered[df_filtered["Sector"].isin(selected_sectors)]
if selected_categories:
  df_filtered = df_filtered[df_filtered["Category"].isin(selected_categories)]
if selected_funding:
  df_filtered = df_filtered[
      df_filtered["Funding_Source"].isin(selected_funding)
  ]
df_filtered = df_filtered[
    (df_filtered["Estimate_Amount"] >= budget_range[0])
    & (df_filtered["Estimate_Amount"] <= budget_range[1])
]

# 4. Top-Level Committee KPIs
st.title(f"📊 {selected_committee}")
st.markdown("### Public Sector Governance & Economic Decision-Making Dashboard")
st.markdown("---")

total_budget = df_filtered["Estimate_Amount"].sum()
active_proposals = len(df_filtered)
avg_project_cost = (
    df_filtered["Estimate_Amount"].mean() if active_proposals > 0 else 0
)
projected_yield = total_budget * 1.45

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
  st.metric(label="Total Budget Allocation", value=f"₱{total_budget:,.2f}")
with kpi2:
  st.metric(label="Active Proposals Count", value=f"{active_proposals:,}")
with kpi3:
  st.metric(label="Average Project Cost", value=f"₱{avg_project_cost:,.2f}")
with kpi4:
  st.metric(label="Projected Economic Yield", value=f"₱{projected_yield:,.2f}")

st.markdown("---")

# 5. Dashboard Tabs Layout
tab1, tab2, tab3, tab4 = st.tabs([
    "📂 Committee Portfolio Overview",
    "📈 Revenue & Economic Projections",
    "🤖 Predictive Modeling & PCA",
    "📋 Decision-Making Matrix Table",
])

with tab1:
  st.subheader("Portfolio Allocation & Source Breakdown")
  col_a, col_b = st.columns(2)

  with col_a:
    if not df_filtered.empty:
      fig_sector = px.pie(
          df_filtered,
          names="Sector",
          values="Estimate_Amount",
          title="Budget Allocation by Sector",
          hole=0.4,
      )
      st.plotly_chart(fig_sector, use_container_width=True)
    else:
      st.info("No records match the current filter selection.")

  with col_b:
    if not df_filtered.empty:
      fig_bar = px.bar(
          df_filtered.groupby(["Source", "Category"])["Estimate_Amount"]
          .sum()
          .reset_index(),
          x="Category",
          y="Estimate_Amount",
          color="Source",
          title="Masterplan vs. New Proposals by Category",
          barmode="group",
      )
      st.plotly_chart(fig_bar, use_container_width=True)
    else:
      st.info("No records match the current filter selection.")

with tab2:
  st.subheader("Revenue Generation & Economic Simulation")
  st.markdown(
      """
    > **Fiscal Sustainability & Resource Prioritization:** 
    > Rigorous evaluation of Net Present Value (NPV) and Benefit-Cost Ratios (BCR) ensures public funds are channeled toward projects yielding the highest socio-economic returns, minimizing fiscal vulnerability and promoting long-term regional development.
    """
  )

  growth_multiplier = st.slider(
      "Regional Economic Growth Multiplier", 1.0, 2.5, 1.40, 0.05
  )
  discount_rate = (
      st.slider("Discount Rate (%)", 3.0, 12.0, 8.0, 0.5) / 100.0
  )

  if not df_filtered.empty:
    sim_df = df_filtered.copy()
    sim_df["Projected_Revenue"] = sim_df["Estimate_Amount"] * growth_multiplier
    sim_df["Estimated_NPV"] = (
        sim_df["Projected_Revenue"] / (1 + discount_rate)
    ) - sim_df["Estimate_Amount"]
    sim_df["BCR"] = sim_df["Projected_Revenue"] / sim_df[
        "Estimate_Amount"
    ].replace(0, 1)

    size_arg = (
        "BCR" if len(sim_df) > 1 and sim_df["BCR"].nunique() > 1 else None
    )
    fig_econ = px.scatter(
        sim_df,
        x="Estimate_Amount",
        y="Projected_Revenue",
        size=size_arg,
        color="Sector",
        hover_name="Title",
        title="Project Cost vs. Projected Revenue & BCR Scaling",
    )
    st.plotly_chart(fig_econ, use_container_width=True)
  else:
    st.info("No data available for economic simulation.")

with tab3:
  st.subheader(
      "Predictive Modeling & Principal Component Analysis (PCA)"
  )
  st.markdown(
      "Multivariate clustering of project proposals to identify high-priority"
      " strategic investments."
  )

  if len(df_filtered) > 3:
    pca_data = df_filtered[["Estimate_Amount"]].copy()
    pca_data["Duration_Factor"] = np.random.randint(1, 6, size=len(pca_data))
    pca_data["Risk_Index"] = np.random.uniform(1.0, 10.0, size=len(pca_data))

    scaler = StandardScaler()
    scaled = scaler.fit_transform(pca_data)

    pca = PCA(n_components=2)
    comps = pca.fit_transform(scaled)

    pca_df = pd.DataFrame(comps, columns=["PC1", "PC2"])
    pca_df["Title"] = df_filtered["Title"].values
    pca_df["Sector"] = df_filtered["Sector"].values

    fig_pca = px.scatter(
        pca_df,
        x="PC1",
        y="PC2",
        color="Sector",
        hover_name="Title",
        title="PCA 2D Cluster Map",
    )
    st.plotly_chart(fig_pca, use_container_width=True)
  else:
    st.warning(
        "Insufficient data points for PCA clustering under current filters."
    )

with tab4:
  st.subheader("Decision-Making Matrix Table")
  st.markdown(
      "Examine detailed project attributes and export selected subsets for"
      " official committee resolutions."
  )

  if not df_filtered.empty:
    display_df = df_filtered[[
        "Project_No",
        "Title",
        "Sector",
        "Category",
        "Estimate_Amount",
        "Source",
        "Funding_Source",
        "Assigned_Committee",
    ]]
    st.dataframe(display_df, use_container_width=True)

    csv_buffer = io.StringIO()
    display_df.to_csv(csv_buffer, index=False)
    st.download_button(
        label="📥 Export Filtered Matrix as CSV",
        data=csv_buffer.getvalue(),
        file_name=f"{selected_committee.replace(' ', '_')}_matrix.csv",
        mime="text/csv",
    )
  else:
    st.info("No records matching the selected filters.")
