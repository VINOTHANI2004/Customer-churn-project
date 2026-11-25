import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Customer Churn Insights", page_icon="📊", layout="wide")

REQUIRED = {"churn", "subscription_type", "tenure_months", "monthly_charges"}

st.markdown("""<style>
.block-container {padding-top: 2rem; max-width: 1200px;}
[data-testid="stMetric"] {background: #f4f7fb; border: 1px solid #e8edf5; padding: 16px; border-radius: 12px;}
</style>""", unsafe_allow_html=True)
st.title("📊 Customer Churn Insights")
st.caption("Upload a customer CSV to explore churn patterns with privacy-friendly aggregate charts.")

with st.sidebar:
    st.header("Upload your data")
    uploaded = st.file_uploader("Choose a CSV file", type=["csv"])
    st.caption("Required columns: churn, subscription_type, tenure_months, monthly_charges")
    st.divider()
    st.caption("Only summary metrics and charts are displayed. Customer-level rows are never shown.")

if uploaded is None:
    st.info("Upload your customer churn CSV to get started.")
    st.markdown("### What you can explore")
    st.markdown("- Overall churn rate and customer count\n- Churn by subscription type\n- Average tenure and monthly charges by churn status\n- Missing values and basic data quality")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception as exc:
    st.error(f"Could not read this CSV: {exc}")
    st.stop()
missing_cols = sorted(REQUIRED - set(df.columns))
if missing_cols:
    st.error("Missing required columns: " + ", ".join(missing_cols))
    st.stop()
if df.empty:
    st.warning("The uploaded CSV has no data rows.")
    st.stop()

# Normalize common numeric columns safely.
for col in ("tenure_months", "monthly_charges"):
    df[col] = pd.to_numeric(df[col], errors="coerce")
df["churn"] = df["churn"].astype("string").str.strip()
df["subscription_type"] = df["subscription_type"].astype("string").str.strip()
churn_yes = df["churn"].str.casefold().isin(["yes", "true", "1", "churned"])
known = df["churn"].notna()
rate = (churn_yes & known).sum() / known.sum() if known.any() else 0

st.subheader("Dataset overview")
a, b, c, d = st.columns(4)
a.metric("Customers", f"{len(df):,}")
b.metric("Churn rate", f"{rate:.1%}")
c.metric("Avg. monthly charge", f"{df['monthly_charges'].mean():,.2f}" if df["monthly_charges"].notna().any() else "—")
d.metric("Median tenure", f"{df['tenure_months'].median():,.0f} months" if df["tenure_months"].notna().any() else "—")

left, right = st.columns(2)
with left:
    st.markdown("#### Customer count by subscription")
    counts = df["subscription_type"].fillna("Unknown").value_counts().rename_axis("Subscription").rename("Customers")
    st.bar_chart(counts, color="#5271ff")
with right:
    st.markdown("#### Churn status")
    churn_counts = df.loc[known, "churn"].value_counts().rename_axis("Status").rename("Customers")
    st.bar_chart(churn_counts, color="#ff8066")

left, right = st.columns(2)
with left:
    st.markdown("#### Churn by subscription")
    sub = df.assign(_churn=churn_yes).groupby("subscription_type", dropna=False).agg(Customers=("churn", "size"), Churned=("_churn", "sum"))
    sub["Churn rate (%)"] = (sub["Churned"] / sub["Customers"] * 100).round(1)
    st.bar_chart(sub["Churn rate (%)"], color="#9b59b6")
with right:
    st.markdown("#### Average tenure by churn status")
    tenure = df.assign(_status=df["churn"].fillna("Unknown")).groupby("_status")["tenure_months"].mean().round(1)
    st.bar_chart(tenure, color="#28a58b")

st.markdown("#### Average monthly charges by churn status")
charges = df.assign(_status=df["churn"].fillna("Unknown")).groupby("_status")["monthly_charges"].mean().round(2)
st.bar_chart(charges, color="#f0a43a")

with st.expander("Data quality summary"):
    quality = pd.DataFrame({"Missing values": df.isna().sum(), "Missing %": (df.isna().mean() * 100).round(1)})
    st.dataframe(quality, use_container_width=True)
    st.caption(f"{len(df):,} rows × {len(df.columns):,} columns")

st.caption("This dashboard describes patterns in the uploaded dataset; it does not predict which individual customer will churn.")
