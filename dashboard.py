
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ---------------- PAGE CONFIG ---------------- #

st.set_page_config(
    page_title="E-Commerce Customer Behavior Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CUSTOM CSS ---------------- #

st.markdown("""
<style>

#MainMenu{
visibility:hidden;
}

footer{
visibility:hidden;
}

header{
visibility:visible;
}

.block-container{
padding-top:1rem;
padding-bottom:2rem;
padding-left:2rem;
padding-right:2rem;
}

[data-testid="stSidebar"]{
background:linear-gradient(180deg,#0F172A,#1E3A8A);
}

[data-testid="stSidebar"] *{
color:white;
}

h1{
font-size:45px !important;
font-weight:800;
text-align:center;
color:#1E3A8A;
}

.metric-card{
background:white;
padding:20px;
border-radius:18px;
box-shadow:0px 10px 25px rgba(0,0,0,.15);
text-align:center;
}

div[data-testid="stMetric"]{
background:white;
padding:18px;
border-radius:16px;
box-shadow:0px 8px 18px rgba(0,0,0,.12);
border-left:6px solid #2563EB;
}
.stSelectbox div[data-baseweb="select"] > div{
    background:white !important;
    color:black !important;
}

.stSelectbox svg{
    fill:black !important;
}

div[role="listbox"] div{
    color:black !important;
    background:white !important;
}

/* Date input text */
input {
    color: black !important;
}

input::placeholder {
    color: black !important;
}

/* Calendar input */
[data-testid="stDateInput"] input {
    color: black !important;
    background: white !important;
}

/* Calendar icon */
[data-testid="stDateInput"] svg {
    fill: black !important;
}
[data-testid="stAppViewContainer"]{
    background:linear-gradient(135deg,#EAF4FF,#FFFFFF,#F3F8FF);
}
/* Premium Gradient Background */
[data-testid="stAppViewContainer"]{
    background: linear-gradient(
        135deg,
        #E8EEF9 0%,
        #D6E4F0 35%,
        #C8D9F2 70%,
        #EAF2FF 100%
    );
}

.main .block-container{
    background: transparent;
}

</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ---------------- #

@st.cache_data
def load_data():

    df = pd.read_csv(
        "OnlineRetail.csv",
        encoding="latin1"
    )

    cols = list(df.columns)

    cols[0] = "InvoiceNo"
    cols[1] = "StockCode"
    cols[2] = "Description"
    cols[3] = "Quantity"
    cols[4] = "InvoiceDate"
    cols[5] = "UnitPrice"
    cols[6] = "CustomerID"
    cols[7] = "Country"

    df.columns = cols

    df["Quantity"] = pd.to_numeric(
        df["Quantity"],
        errors="coerce"
    )

    df["UnitPrice"] = pd.to_numeric(
        df["UnitPrice"],
        errors="coerce"
    )

    df["InvoiceDate"] = pd.to_datetime(
        df["InvoiceDate"],
        errors="coerce"
    )

    df = df.dropna(
        subset=[
            "Quantity",
            "UnitPrice",
            "InvoiceDate"
        ]
    )

    df["Sales"] = (
        df["Quantity"] *
        df["UnitPrice"]
    )

    return df

df = load_data()

# ---------------- DASHBOARD TITLE ---------------- #

st.markdown("""
<h1>📊 E-Commerce Customer Behavior Dashboard</h1>

<p style='text-align:center;
font-size:18px;
color:gray;'>

Interactive Sales Analytics using
Python • Streamlit • Plotly

</p>

""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #

st.sidebar.image(
    "https://img.icons8.com/color/96/combo-chart--v1.png",
    width=80
)

st.sidebar.title("Dashboard Filters")

country = st.sidebar.radio(
    "🌍 Select Country",
    ["All"] + sorted(df["Country"].dropna().unique().tolist())
)

if country != "All":
    df = df[df["Country"] == country]

start_date = st.sidebar.date_input(
    "📅 Start Date",
    df["InvoiceDate"].min().date()
)

end_date = st.sidebar.date_input(
    "📅 End Date",
    df["InvoiceDate"].max().date()
)

df = df[
    (df["InvoiceDate"].dt.date >= start_date)
    &
    (df["InvoiceDate"].dt.date <= end_date)
]

st.sidebar.markdown("---")

st.sidebar.success(
    f"Filtered Records : {len(df):,}"
)

# ---------------- KPI CALCULATIONS ---------------- #

total_sales = df["Sales"].sum()

total_orders = df["InvoiceNo"].nunique()

total_customers = df["CustomerID"].nunique()

average_order = (
    total_sales / total_orders
    if total_orders
    else 0
)

# ---------------- KPI CARDS ---------------- #

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "💰 Total Sales",
    f"${total_sales:,.2f}"
)

c2.metric(
    "📦 Orders",
    f"{total_orders:,}"
)

c3.metric(
    "👥 Customers",
    f"{total_customers:,}"
)

c4.metric(
    "🛒 Avg Order",
    f"${average_order:,.2f}"
)

st.markdown("---")

st.subheader("📈 Sales Performance Overview")

# ---------------- MONTHLY SALES TREND ---------------- #

monthly_sales = (
    df.groupby(df["InvoiceDate"].dt.to_period("M"))["Sales"]
    .sum()
    .reset_index()
)

monthly_sales["InvoiceDate"] = monthly_sales["InvoiceDate"].astype(str)

fig_month = px.line(
    monthly_sales,
    x="InvoiceDate",
    y="Sales",
    markers=True,
    title="📈 Monthly Sales Trend",
    template="plotly_white"
)

fig_month.update_layout(
    title_x=0.5,
    height=450
)

st.plotly_chart(fig_month, use_container_width=True)

# ---------------- TWO COLUMN LAYOUT ---------------- #

left, right = st.columns(2)

# -------- TOP PRODUCTS -------- #

top_products = (
    df.groupby("Description")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_products = px.bar(
    top_products,
    x="Sales",
    y="Description",
    orientation="h",
    color="Sales",
    title="🏆 Top 10 Products",
    template="plotly_white"
)

fig_products.update_layout(
    title_x=0.5,
    height=500
)

left.plotly_chart(fig_products, use_container_width=True)

# -------- TOP COUNTRIES -------- #

top_country = (
    df.groupby("Country")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
    .reset_index()
)

fig_country = px.bar(
    top_country,
    x="Country",
    y="Sales",
    color="Sales",
    title="🌍 Top 10 Countries",
    template="plotly_white"
)

fig_country.update_layout(
    title_x=0.5,
    height=500
)

right.plotly_chart(fig_country, use_container_width=True)

# ---------------- PIE & DONUT CHARTS ---------------- #

col1, col2 = st.columns(2)

pie_data = (
    df.groupby("Country")["Sales"]
    .sum()
    .nlargest(5)
    .reset_index()
)

fig_pie = px.pie(
    pie_data,
    values="Sales",
    names="Country",
    title="🥧 Sales Share by Country"
)

col1.plotly_chart(fig_pie, use_container_width=True)

fig_donut = px.pie(
    pie_data,
    values="Sales",
    names="Country",
    hole=0.55,
    title="🍩 Donut Chart"
)

col2.plotly_chart(fig_donut, use_container_width=True)

# ---------------- SALES DISTRIBUTION ---------------- #

fig_hist = px.histogram(
    df,
    x="Sales",
    nbins=40,
    color_discrete_sequence=["#2563EB"],
    title="📊 Sales Distribution"
)

fig_hist.update_layout(
    title_x=0.5,
    height=450
)

st.plotly_chart(fig_hist, use_container_width=True)

# ---------------- TOP CUSTOMERS ---------------- #

st.subheader("👥 Top 10 Customers")

top_customers = (
    df.groupby("CustomerID")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(top_customers)

# ---------------- BEST SELLING PRODUCTS ---------------- #

st.subheader("🔥 Top Selling Products")

best_products = (
    df.groupby("Description")["Quantity"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

st.bar_chart(best_products)

# ---------------- MONTHLY SUMMARY TABLE ---------------- #

st.subheader("📅 Monthly Sales Summary")

summary = (
    df.groupby(df["InvoiceDate"].dt.to_period("M"))
    .agg(
        Total_Sales=("Sales","sum"),
        Orders=("InvoiceNo","nunique"),
        Customers=("CustomerID","nunique")
    )
)

summary.index = summary.index.astype(str)

st.dataframe(
    summary,
    use_container_width=True
)

# ---------------- DOWNLOAD BUTTON ---------------- #

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="📥 Download Filtered Dataset",
    data=csv,
    file_name="Filtered_Ecommerce_Data.csv",
    mime="text/csv"
)

# ---------------- DATASET PREVIEW ---------------- #

st.subheader("📄 Dataset Preview")

st.dataframe(
    df.head(25),
    use_container_width=True
)

# ---------------- PROJECT INFORMATION ---------------- #

st.markdown("---")

st.info("""
### 📊 Project Information

**Project:** E-Commerce Customer Behavior Analysis

**Technology Stack**
- Python
- Streamlit
- Pandas
- Plotly

**Features**
- KPI Dashboard
- Interactive Filters
- Sales Trend Analysis
- Country Analysis
- Product Analysis
- Customer Analysis
- Download Filtered Data
""")

# ---------------- FOOTER ---------------- #

st.markdown("---")

st.markdown(
"""
<div style="text-align:center;
padding:20px;
background:#0F172A;
border-radius:15px;
color:white;">

<h3>🚀 E-Commerce Customer Behavior Dashboard</h3>

<p>Developed using Streamlit • Pandas • Plotly • Python</p>

<p>© 2026 All Rights Reserved</p>

</div>
""",
unsafe_allow_html=True
)
















