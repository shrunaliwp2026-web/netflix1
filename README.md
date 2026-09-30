# Streaming Insights Dashboard

A Streamlit dashboard for exploring streaming customer behavior, content performance, and revenue analytics.

## Run locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run plots.py
```

The dashboard loads `NF2.csv` by default. Use the sidebar CSV uploader to explore another dataset with the required dashboard columns.

## Dashboard

- Overview charts for monthly revenue, category revenue, regional revenue, subscription revenue, device usage, and payment methods
- Sidebar filters for region, subscription plan, category, and watch date
- Searchable Explore Data table and Data Quality summary
- Additional rating, language, watch-time, and 3D engagement views under “More insights”
