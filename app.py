import numpy as np
import pandas as pd

# Set seed for reproducibility
np.random.seed(42)

n_projects = 95
sectors = ["Economic", "Environmental", "Infrastructure", "Social", "Institutional"]
categories = [
    "Infrastructure Preparation",
    "Marketing and Investment Promotion",
    "Environmental Baseline and Planning",
    "Social Services",
]
sources = ["Masterplan", "GAA", "LGU", "Private Partner"]

project_nos = list(range(1, n_projects + 1))
titles = [f"STRATEGIC DEVELOPMENT PROJECT {i}" for i in project_nos]

# Distribute amounts ensuring the total sums up to exactly 15.8 Billion PHP
raw_amounts = np.random.exponential(scale=1.5, size=n_projects)
scale_factor = 15_800_000_000 / raw_amounts.sum()
estimate_amounts = np.round(raw_amounts * scale_factor, 2)

df_mock = pd.DataFrame(
    {
        "Project_No": project_nos,
        "Title": titles,
        "Sector": np.random.choice(sectors, size=n_projects),
        "Category": np.random.choice(categories, size=n_projects),
        "Estimate_Amount": estimate_amounts,
        "Source": np.random.choice(sources, size=n_projects),
        "Funding_Source": np.random.choice(sources, size=n_projects),
    }
)

# Verify total sum
print(f"Total Estimate Amount: ₱{df_mock['Estimate_Amount'].sum():,.2f}")
