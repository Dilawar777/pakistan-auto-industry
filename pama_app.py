# ============================================================
# PAKISTAN AUTOMOTIVE INDUSTRY ANALYSIS
# Step 6 — Streamlit App
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(
    page_title="Pakistan Auto Industry",
    page_icon="🚗",
    layout="wide"
)

st.markdown("""
<style>
    .main-title { font-size:2.2rem; font-weight:700; color:#1A56A0; }
    .sub-title  { font-size:1rem; color:#6B7280; margin-top:-10px; }
    .kpi-card   { background:#F0F7FF; border-left:4px solid #1A56A0;
                  padding:14px 18px; border-radius:8px; margin:4px 0; }
    .kpi-val    { font-size:1.8rem; font-weight:700; color:#1A56A0; }
    .kpi-lbl    { font-size:0.82rem; color:#6B7280; }
    .insight-blue  { background:#EBF4FF; border-left:4px solid #1A56A0;
                     padding:12px 16px; border-radius:8px; margin:6px 0;
                     word-wrap:break-word; white-space:normal; width:100%; color:#1A1A2E;  }
    .insight-red   { background:#FEE2E2; border-left:4px solid #DC2626;
                     padding:12px 16px; border-radius:8px; margin:6px 0;
                     word-wrap:break-word; white-space:normal; width:100%; color:#1A1A2E;  }
    .insight-green { background:#D1FAE5; border-left:4px solid #059669;
                     padding:12px 16px; border-radius:8px; margin:6px 0;
                     word-wrap:break-word; white-space:normal; width:100%; color:#1A1A2E;  }
    .insight-amber { background:#FFF8E7; border-left:4px solid #F39C12;
                     padding:12px 16px; border-radius:8px; margin:6px 0;
                     word-wrap:break-word; white-space:normal; width:100%; color:#1A1A2E; }
    .section    { font-size:1.1rem; font-weight:600; color:#1A1A2E;
                  border-bottom:2px solid #1A56A0;
                  padding-bottom:4px; margin:20px 0 12px; }
    footer { visibility:hidden; }
</style>
""", unsafe_allow_html=True)

BLUE  = "#1A56A0"
RED   = "#E74C3C"
GREEN = "#27AE60"
AMBER = "#F39C12"

@st.cache_data
def load_data():
    DATA_URL = "https://raw.githubusercontent.com/Dilawar777/pakistan-auto-industry/main/pama.csv"
    try:
        df = pd.read_csv(DATA_URL, encoding="latin1")
    except Exception as e:
        st.error(f"Could not load dataset: {e}")
        st.stop()
   
    df["Date"]    = pd.to_datetime(df["Month"].astype(str) + " " + df["Year"].astype(str),
                                   format="%b %Y", errors="coerce")
    df = df.dropna(subset=["Date"]).sort_values("Date")
    return df

df    = load_data()
sales = df[df["Column1"] == "Sale"]
prod  = df[df["Column1"].isin(["Prod.", "Prod"])]

yearly     = sales.groupby("Year")["Units"].sum()
cat_totals = sales.groupby("Category.1")["Units"].sum().sort_values(ascending=False)
moto       = sales[sales["Category.1"] == "MOTORCYCLES"].groupby("Year")["Units"].sum()
cars_s     = sales[sales["Category.1"] == "CARS"].groupby("Year")["Units"].sum()
moto_share = (moto / yearly * 100).fillna(0)

cars_df      = sales[sales["Category.1"] == "CARS"].copy()
cars_df["Brand"] = cars_df["Vehicles"].str.split().str[0]
top_brands   = cars_df.groupby("Brand")["Units"].sum().sort_values(ascending=False).head(4).index
brand_yearly = cars_df.groupby(["Brand","Year"])["Units"].sum().unstack(fill_value=0)
brand_yearly = brand_yearly.loc[top_brands].T

month_order  = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
sales_copy   = sales.copy()
sales_copy["Month_Name"] = pd.Categorical(sales_copy["Month"], categories=month_order, ordered=True)
seasonal     = sales_copy.groupby("Month_Name")["Units"].mean()
yoy          = yearly.pct_change() * 100


st.markdown('<p class="main-title">🚗 Pakistan Automotive Industry Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">PAMA Dataset · 2007–2024 · 17,723 Records · Source: opendata.com.pk</p>', unsafe_allow_html=True)
st.markdown("")


st.sidebar.markdown("### 🔧 Filters")
year_range = st.sidebar.slider("Year Range",
                                int(df["Year"].min()), int(df["Year"].max()),
                                (int(df["Year"].min()), 2024))
selected_cats = st.sidebar.multiselect(
    "Vehicle Categories",
    options=sorted(df["Category.1"].dropna().unique()),
    default=["MOTORCYCLES","CARS","TRUCKS"]
)

sales_f = sales[(sales["Year"] >= year_range[0]) &
                (sales["Year"] <= year_range[1]) &
                (sales["Category.1"].isin(selected_cats))]


k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.markdown(f'<div class="kpi-card"><div class="kpi-val">{sales["Units"].sum()/1e6:.1f}M</div><div class="kpi-lbl">Total Units Sold</div></div>', unsafe_allow_html=True)
with k2:
    st.markdown('<div class="kpi-card"><div class="kpi-val">73.2%</div><div class="kpi-lbl">Motorcycle Market Share</div></div>', unsafe_allow_html=True)
with k3:
    st.markdown('<div class="kpi-card"><div class="kpi-val">Suzuki</div><div class="kpi-lbl">Top Car Brand</div></div>', unsafe_allow_html=True)
with k4:
    st.markdown('<div class="kpi-card"><div class="kpi-val">May</div><div class="kpi-lbl">Peak Sales Month</div></div>', unsafe_allow_html=True)
with k5:
    st.markdown('<div class="kpi-card"><div class="kpi-val">ZERO</div><div class="kpi-lbl">Cycle Local Production</div></div>', unsafe_allow_html=True)

st.markdown(""); st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📈 Trends", "🏍️ Categories", "🚗 Brands", "💡 Insights"])


with tab1:
    yearly_f = sales_f.groupby("Year")["Units"].sum()
    yoy_f    = yearly_f.pct_change() * 100

    st.markdown('<p class="section">Yearly Sales Trend</p>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)

    with c1:
        fig, ax = plt.subplots(figsize=(7, 4))
        ax.fill_between(yearly_f.index, yearly_f.values, alpha=0.25, color=BLUE)
        ax.plot(yearly_f.index, yearly_f.values, color=BLUE, linewidth=2.5, marker="o", markersize=5)
        if 2020 in yearly_f.index:
            ax.axvline(2020, color=RED, linestyle="--", linewidth=1)
            ax.text(2020.1, yearly_f.max()*0.9, "COVID", fontsize=8, color=RED)
        ax.set_title("Yearly Total Sales", fontweight="bold")
        ax.set_ylabel("Units"); ax.set_xlabel("Year")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e6:.1f}M"))
        ax.tick_params(axis="x", rotation=45)
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with c2:
        fig, ax = plt.subplots(figsize=(7, 4))
        colors_yoy = [RED if v < 0 else GREEN for v in yoy_f.values]
        ax.bar(yoy_f.index, yoy_f.values, color=colors_yoy, alpha=0.85)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_title("Year-over-Year Growth (%)", fontweight="bold")
        ax.set_ylabel("Growth (%)")
        ax.tick_params(axis="x", rotation=45)
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown('<p class="section">Seasonal Pattern</p>', unsafe_allow_html=True)
    c3, c4 = st.columns(2)

    with c3:
        fig, ax = plt.subplots(figsize=(7, 4))
        colors_m = [RED if v == seasonal.max() else
                    "#9CA3AF" if k in ["Jul","Sep"] else BLUE
                    for k, v in seasonal.items()]
        ax.bar(seasonal.index, seasonal.values, color=colors_m, alpha=0.85)
        ax.set_title("Average Monthly Sales\n(Red=Peak · Gray=Monsoon dip)", fontweight="bold")
        ax.set_ylabel("Avg Units")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1000:.0f}K"))
        ax.tick_params(axis="x", rotation=45)
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with c4:
        covid_sales = sales[sales["Year"].isin([2019,2020,2021])].copy()
        covid_sales["Month_Name"] = pd.Categorical(covid_sales["Month"],
                                                    categories=month_order, ordered=True)
        covid_monthly = covid_sales.groupby(["Year","Month_Name"])["Units"].sum().unstack(level=0)
        fig, ax = plt.subplots(figsize=(7, 4))
        covid_colors = {2019: GREEN, 2020: RED, 2021: BLUE}
        for col in covid_monthly.columns:
            ax.plot(covid_monthly.index.astype(str), covid_monthly[col],
                    marker="o", linewidth=2, markersize=4,
                    label=str(col), color=covid_colors.get(col, "#333"))
        ax.set_title("COVID Impact\n2019 vs 2020 vs 2021", fontweight="bold")
        ax.set_xlabel("Month"); ax.set_ylabel("Units")
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1000:.0f}K"))
        ax.legend(title="Year", fontsize=8)
        ax.tick_params(axis="x", rotation=45)
        for s in ["top","right"]: ax.spines[s].set_visible(False)
        plt.tight_layout(); st.pyplot(fig); plt.close()


with tab2:
    c1, c2 = st.columns(2)
    colors_pie = [BLUE,RED,GREEN,AMBER,"#8E44AD","#16A085","#E67E22","#2ECC71","#9B59B6","#1ABC9C"]

    with c1:
        fig, ax = plt.subplots(figsize=(6, 5))
        ax.pie(cat_totals.values, labels=cat_totals.index,
               colors=colors_pie[:len(cat_totals)],
               autopct="%1.1f%%", startangle=90, textprops={"fontsize": 8})
        ax.set_title("Market Share by Category (2007–2024)", fontweight="bold")
        plt.tight_layout(); st.pyplot(fig); plt.close()

    with c2:
        fig, axes = plt.subplots(2, 1, figsize=(6, 5), sharex=True)
        axes[0].plot(moto.index, moto.values, color=RED, linewidth=2.5,
                     marker="o", markersize=4, label="Motorcycles")
        axes[0].plot(cars_s.index, cars_s.values, color=BLUE, linewidth=2.5,
                     marker="o", markersize=4, label="Cars")
        axes[0].set_title("Motorcycles vs Cars", fontweight="bold")
        axes[0].set_ylabel("Units")
        axes[0].yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e6:.1f}M"))
        axes[0].legend(fontsize=8)
        for s in ["top","right"]: axes[0].spines[s].set_visible(False)
        axes[1].fill_between(moto_share.index, moto_share.values, alpha=0.3, color=RED)
        axes[1].plot(moto_share.index, moto_share.values, color=RED, linewidth=2)
        axes[1].set_title("Motorcycle Market Share (%)", fontweight="bold")
        axes[1].set_ylabel("%"); axes[1].set_ylim(0, 100)
        for s in ["top","right"]: axes[1].spines[s].set_visible(False)
        plt.tight_layout(); st.pyplot(fig); plt.close()

  
    st.markdown('<p class="section">Cycle — Fully Imported</p>', unsafe_allow_html=True)
    cycle_sales = sales[sales["Category.1"] == "CYCLE"].groupby("Year")["Units"].sum()
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.bar(cycle_sales.index, cycle_sales.values, color=BLUE, alpha=0.85, label="Sales")
    ax.set_title("CYCLE Sales — Zero Local Production (Fully Imported)", fontweight="bold")
    ax.set_xlabel("Year"); ax.set_ylabel("Units Sold")
    ax.legend()
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    plt.tight_layout(); st.pyplot(fig); plt.close()


with tab3:
    st.markdown('<p class="section">Car Brand Competition</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(12, 5))
    brand_colors = [BLUE, RED, GREEN, AMBER]
    for i, brand in enumerate(brand_yearly.columns):
        ax.plot(brand_yearly.index, brand_yearly[brand],
                linewidth=2.5, marker="o", markersize=4,
                label=brand, color=brand_colors[i])
    ax.set_title("Top 4 Car Brands — Yearly Sales (2007–2024)", fontweight="bold")
    ax.set_ylabel("Units Sold")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1000:.0f}K"))
    ax.legend(title="Brand")
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    plt.tight_layout(); st.pyplot(fig); plt.close()

    st.markdown('<p class="section">Top 10 Best Selling Models</p>', unsafe_allow_html=True)
    top10 = sales.groupby("Vehicles")["Units"].sum().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(12, 5))
    top10_sorted = top10.sort_values()
    ax.barh(range(len(top10_sorted)), top10_sorted.values, color=BLUE, alpha=0.85)
    ax.set_yticks(range(len(top10_sorted)))
    ax.set_yticklabels(top10_sorted.index)
    ax.set_title("Top 10 Vehicle Models — Total Sales (2007–2024)", fontweight="bold")
    ax.set_xlabel("Total Units")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e6:.1f}M"))
    for s in ["top","right"]: ax.spines[s].set_visible(False)
    plt.tight_layout(); st.pyplot(fig); plt.close()


with tab4:
    st.markdown('<p class="section">Market Insights</p>', unsafe_allow_html=True)

    st.markdown('<div class="insight-red"><b>🏍️ Motorcycle Dominance (73.2% market share)</b><br>Pakistan is primarily a motorcycle economy. Motorcycles account for 73.2% of all vehicle sales — affordable price point and fuel efficiency make them the transport of choice for the majority of Pakistanis.</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-blue"><b>🚗 Suzuki Leads Car Sales</b><br>Suzuki has consistently dominated car sales across 2007–2024, followed by Honda and Toyota. Affordable pricing and wide service network give Suzuki a strong competitive advantage in Pakistan.</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-amber"><b>🚴 Cycles Fully Imported — Zero Local Production</b><br>The CYCLE category shows absolutely zero local production across 17 years of data. All cycles sold in Pakistan are imported — highlighting a significant gap in domestic manufacturing that represents a potential investment opportunity.</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-green"><b>📅 May = Peak Sales Month</b><br>May is consistently the highest sales month every year — driven by Eid season demand. Manufacturers and dealers should plan maximum inventory for April–May period.</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-blue"><b>☔ July & September = Monsoon Dip</b><br>July and September show consistently low sales every year across all categories — not just COVID years. Heavy monsoon rains reduce mobility and purchasing activity. This is a structural seasonal pattern, not an anomaly.</div>', unsafe_allow_html=True)
    st.markdown('<div class="insight-green"><b>⚡ Electric Vehicles Emerging</b><br>EVs are beginning to appear in the dataset. Still negligible in volume but the trend is upward — a space worth monitoring for future investment and policy decisions.</div>', unsafe_allow_html=True)

    st.markdown('<p class="section">Economic Decline Years — Root Causes</p>', unsafe_allow_html=True)

    declines = [
        ("📉 2009 (-24.5%)", "red",   "Global Financial Crisis 2008 — Pakistan felt the full impact in 2009. Rupee depreciation, inflation spike, and rising fuel prices destroyed consumer purchasing power."),
        ("📉 2012–2014 (-3% to -6.4%)", "amber", "Pakistan's worst energy crisis — 12 to 18 hours of load shedding daily. Factory production cut, unemployment rose, and consumer spending collapsed across all sectors."),
        ("📉 2018–2020 (-14.4% to -11.4%)", "red", "IMF bailout period — government austerity measures, massive rupee devaluation (PKR went from 110 to 160 per USD), interest rates hiked to 13.25%. Car financing became unaffordable for the middle class."),
        ("📉 2020 (-11.4%)", "red",   "COVID-19 lockdowns — April and May 2020 sales completely collapsed. Industry recovered strongly in second half of 2020 and surpassed pre-COVID levels by 2021."),
        ("📉 2022–2023 (-18.3% to -22.8%)", "red", "Perfect storm: political instability after government change + devastating floods 2022 + PKR crashed to 300 per USD + import restrictions on CBU vehicles + interest rates hit 22%. All factors combined to crush auto demand."),
        ("⚠️ 2025 (-51.8%)", "amber", "Data only covers January to May 2025 — this is NOT a real decline. Full year data will be available later and will show a normal trend."),
    ]

    for title, color, text in declines:
        st.markdown(f'<div class="insight-{"red" if color=="red" else "amber"}"><b>{title}</b><br>{text}</div>', unsafe_allow_html=True)

st.divider()
st.markdown(
    '<p style="text-align:center;color:#9CA3AF;font-size:0.8rem;">'
    'Built by <b>Dilawar Mahar</b> · Data Analyst · Sukkur IBA University · '
    'Data: PAMA via opendata.com.pk · '
    '<a href="https://github.com/Dilawar777" style="color:#1A56A0">GitHub</a></p>',
    unsafe_allow_html=True
)
