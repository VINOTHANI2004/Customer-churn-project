# Customer Churn Insights

A small Streamlit dashboard based on the supplied customer churn analysis. It accepts a CSV upload and shows aggregate churn, subscription, tenure, charges, and missing-value summaries. It does not expose customer-level rows.

## Run locally

1. Install Python 3.10 or newer.
2. In this folder, run `python -m venv .venv` and activate it.
3. Run `pip install -r requirements.txt`.
4. Run `streamlit run app.py`.
5. Upload `customer_churn_dataset_10000.csv` in the sidebar.

Required CSV columns: `churn`, `subscription_type`, `tenure_months`, `monthly_charges`.

## Publish

For a public demo, create a GitHub repository containing `app.py` and `requirements.txt`, then connect it to Streamlit Community Cloud and deploy `app.py`. Upload the CSV through the app after it launches. Do not commit a customer dataset to a public repository unless you have permission to publish it and have removed sensitive fields.
