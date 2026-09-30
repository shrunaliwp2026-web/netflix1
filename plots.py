import base64
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(
    page_title="Streaming Insights",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "NF2.csv"
BACKGROUND_PATH = Path(__file__).parent / "assets" / "dashboard-bg.svg"
REQUIRED_COLUMNS = {
    "Region",
    "Subscription_Plan",
    "Category",
    "Rating",
    "Watch_Count",
    "Watch_Date",
    "Watch_Time_Minutes",
    "Language",
    "Payment_Method",
    "Monthly_Revenue",
    "Title",
    "Device",
}
COLORS = ["#E50914", "#27C7A5", "#8D78FF", "#F5B84B", "#59A7FF", "#F07C9A"]
PLOT_LAYOUT = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#E7EAF0", "family": "Inter, ui-sans-serif, sans-serif", "size": 11},
    "margin": {"l": 14, "r": 16, "t": 20, "b": 14},
    "legend": {"bgcolor": "rgba(0,0,0,0)"},
}


@st.cache_data
def load_data(file_bytes: bytes | None, file_name: str) -> pd.DataFrame:
    if file_bytes is None:
        if not DATA_PATH.is_file():
            raise FileNotFoundError(f"Could not find the dataset: {DATA_PATH.name}")
        data = pd.read_csv(DATA_PATH)
    else:
        from io import BytesIO

        data = pd.read_csv(BytesIO(file_bytes))

    missing_columns = sorted(REQUIRED_COLUMNS.difference(data.columns))
    if missing_columns:
        raise ValueError(
            f"{file_name} is missing required columns: {', '.join(missing_columns)}"
        )

    data = data.copy()
    data["Watch_Date"] = pd.to_datetime(data["Watch_Date"], errors="coerce")
    data = data.dropna(subset=["Watch_Date"])
    if data.empty:
        raise ValueError(f"{file_name} contains no rows with a valid watch date.")
    return data


def apply_plot_layout(figure, *, height: int = 270):
    figure.update_layout(**PLOT_LAYOUT, height=height)
    figure.update_xaxes(
        showgrid=False, zeroline=False, linecolor="rgba(255,255,255,.10)", automargin=True
    )
    figure.update_yaxes(
        gridcolor="rgba(255,255,255,.07)",
        zeroline=False,
        linecolor="rgba(255,255,255,.10)",
        automargin=True,
    )
    return figure


st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: #080d1a;
        background-image:
            linear-gradient(90deg, rgba(5, 10, 23, .34), rgba(5, 10, 23, .24)),
            url("data:image/svg+xml;base64,{base64.b64encode(BACKGROUND_PATH.read_bytes()).decode('ascii')}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        background-repeat: no-repeat;
        color: #f3f4f6;
    }}
    [data-testid="stAppViewContainer"] {{ background: transparent; }}
    [data-testid="stHeader"] {{ background: rgba(8, 13, 26, .56); }}
    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, rgba(5, 12, 28, .97), rgba(5, 10, 23, .94));
        border-right: 1px solid rgba(117, 153, 214, .18);
    }}
    [data-testid="stSidebar"] > div:first-child {{ padding-top: 1.25rem; }}
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h5 {{
        color: #f3f4f6 !important;
    }}
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] {{ color: #8f98a6 !important; }}
    .block-container {{ padding-top: 1.55rem; padding-bottom: 2.5rem; max-width: 1460px; }}
    h1, h2, h3 {{ color: #f5f6f8; letter-spacing: -.025em; }}
    h1 {{ font-size: clamp(1.85rem, 3vw, 2.35rem) !important; font-weight: 720 !important; }}
    h2 {{ font-size: 1.22rem !important; }}
    h3 {{ font-size: 1rem !important; }}
    p, label, [data-testid="stCaptionContainer"] {{ color: #aeb4c0; }}
    [data-testid="stFileUploader"] section {{ padding: .55rem .65rem; }}
    [data-testid="stMultiSelect"] [data-baseweb="select"] > div,
    [data-testid="stDateInput"] [data-baseweb="input"] > div {{
        background: #151922; border-color: #2a303b; border-radius: 9px; min-height: 2.35rem;
    }}
    [data-testid="stVerticalBlockBorderWrapper"] {{
        border: 1px solid #252a34 !important;
        border-radius: 15px;
        background: linear-gradient(145deg, rgba(23, 27, 35, .87), rgba(17, 20, 27, .90));
        box-shadow: 0 8px 24px rgba(0, 0, 0, .16);
    }}
    [data-testid="stVerticalBlockBorderWrapper"]:hover {{ border-color: #3a414d !important; }}
    .dashboard-header {{ padding: .15rem 0 .85rem; }}
    .dashboard-header h1 {{ margin: 0 0 .25rem; }}
    .dashboard-header p {{ margin: 0; color: #969daa; font-size: .94rem; }}
    .kpi-card {{
        min-height: 112px; padding: 15px 17px; border: 1px solid #252a34;
        border-radius: 14px; background: linear-gradient(145deg, #191d26, #13161d);
        box-shadow: 0 7px 22px rgba(0, 0, 0, .16);
        transition: transform .18s ease, border-color .18s ease, box-shadow .18s ease;
    }}
    .kpi-card:hover {{
        transform: translateY(-2px); border-color: #424956;
        box-shadow: 0 11px 26px rgba(0, 0, 0, .25);
    }}
    .kpi-label {{ color: #aeb4c0; font-size: .82rem; font-weight: 550; white-space: nowrap; }}
    .kpi-value {{
        color: #f5f6f8; margin-top: 10px; font-size: clamp(1.35rem, 2.3vw, 1.8rem);
        font-weight: 720; letter-spacing: -.035em; line-height: 1.05;
    }}
    .kpi-note {{ margin-top: 5px; color: #818895; font-size: .73rem; }}
    [data-baseweb="tab-list"] {{ gap: 8px; border-bottom: 1px solid #252a34; }}
    [data-baseweb="tab"] {{ height: 42px; padding: 0 15px; color: #9da4b0; border-radius: 9px 9px 0 0; }}
    [aria-selected="true"][data-baseweb="tab"] {{ color: #fff; border-bottom: 2px solid #E50914; }}
    [data-testid="stDataFrame"] {{ border: 1px solid #252a34; border-radius: 12px; overflow: hidden; }}
    [data-testid="stExpander"] {{ border: 1px solid #252a34; border-radius: 13px; background: rgba(19, 22, 29, .72); }}
    [data-testid="stMetric"] {{ padding: .7rem .85rem; border: 1px solid #252a34; border-radius: 12px; background: #151820; }}
    [data-testid="stMetricLabel"] {{ color: #aeb4c0; }}
    [data-testid="stMetricValue"] {{ color: #f5f6f8; }}
    footer {{ visibility: hidden; }}
    @media (max-width: 850px) {{
        .block-container {{ padding: 1.1rem 1rem 2rem; }}
        .kpi-card {{ min-height: 100px; padding: 12px; }}
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("## 🎬 Streaming Insights")
st.sidebar.caption("AUDIENCE · CONTENT · REVENUE")
st.sidebar.markdown("---")
st.sidebar.markdown("##### Dataset")
uploaded_file = st.sidebar.file_uploader("Use a different CSV", type=["csv"])

try:
    data = load_data(
        uploaded_file.getvalue() if uploaded_file else None,
        uploaded_file.name if uploaded_file else DATA_PATH.name,
    )
except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
    st.error(f"Unable to load the viewing dataset: {error}")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.markdown("##### Filters")
regions = st.sidebar.multiselect(
    "Region", sorted(data["Region"].dropna().unique()), default=sorted(data["Region"].dropna().unique())
)
plans = st.sidebar.multiselect(
    "Subscription plan",
    sorted(data["Subscription_Plan"].dropna().unique()),
    default=sorted(data["Subscription_Plan"].dropna().unique()),
)
categories = st.sidebar.multiselect(
    "Category",
    sorted(data["Category"].dropna().unique()),
    default=sorted(data["Category"].dropna().unique()),
)
date_min = data["Watch_Date"].min().date()
date_max = data["Watch_Date"].max().date()
start_date, end_date = st.sidebar.date_input(
    "Viewing dates", value=(date_min, date_max), min_value=date_min, max_value=date_max
)

filtered = data.loc[
    data["Region"].isin(regions)
    & data["Subscription_Plan"].isin(plans)
    & data["Category"].isin(categories)
    & data["Watch_Date"].dt.date.between(start_date, end_date)
].copy()

st.markdown(
    """
    <div class="dashboard-header">
      <h1>🎬 Streaming Insights</h1>
      <p>Customer behavior, content performance &amp; revenue analytics</p>
    </div>
    """,
    unsafe_allow_html=True,
)

total_revenue = filtered["Monthly_Revenue"].sum()
average_rating = filtered["Rating"].mean()
total_watch_time = filtered["Watch_Time_Minutes"].sum()


def render_kpi(column, icon: str, label: str, value: str, note: str) -> None:
    with column:
        st.markdown(
            f"""
            <div class="kpi-card">
              <div class="kpi-label">{icon}&nbsp; {label}</div>
              <div class="kpi-value">{value}</div>
              <div class="kpi-note">{note}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


metric_columns = st.columns(4, gap="medium")
render_kpi(metric_columns[0], "👥", "Total Customers", f"{len(filtered):,}", "in the selected view")
render_kpi(metric_columns[1], "💰", "Total Revenue", f"₹{total_revenue:,.0f}", "across selected records")
render_kpi(
    metric_columns[2],
    "⭐",
    "Average Rating",
    f"{average_rating:.2f} / 5" if not filtered.empty else "—",
    "viewer content rating",
)
render_kpi(
    metric_columns[3],
    "🌎",
    "Regions",
    f"{filtered['Region'].nunique():,}",
    "represented in this view",
)

if filtered.empty:
    st.info("No records match these filters. Widen your date range or select more filter values.")
    st.stop()

overview_tab, explore_tab, quality_tab = st.tabs(["Overview", "Explore Data", "Data Quality"])

with overview_tab:
    st.markdown("### Revenue overview")
    revenue_col, category_revenue_col = st.columns(2, gap="medium")
    with revenue_col:
        with st.container(border=True):
            st.markdown("#### Revenue Trend by Month")
            daily_revenue = (
                filtered.groupby("Watch_Date", as_index=False)["Monthly_Revenue"]
                .sum()
                .sort_values("Watch_Date")
            )
            figure = px.line(
                daily_revenue,
                x="Watch_Date",
                y="Monthly_Revenue",
                labels={"Watch_Date": "Watch date", "Monthly_Revenue": "Revenue (₹)"},
            )
            figure.update_traces(
                line_color="#E50914",
                line_width=2.5,
                fill="tozeroy",
                fillcolor="rgba(229,9,20,.10)",
                hovertemplate="%{x|%b %d, %Y}<br>Revenue ₹%{y:,.0f}<extra></extra>",
            )
            figure.update_xaxes(dtick="M1", tickformat="%b '%y")
            st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

    with category_revenue_col:
        with st.container(border=True):
            st.markdown("#### Revenue by Category")
            category_revenue = filtered.groupby("Category", as_index=False)["Monthly_Revenue"].sum()
            figure = px.pie(
                category_revenue,
                names="Category",
                values="Monthly_Revenue",
                hole=0.66,
                color_discrete_sequence=COLORS,
            )
            figure.update_traces(
                textposition="inside",
                textinfo="percent",
                insidetextfont={"size": 10},
                hovertemplate="%{label}<br>Revenue ₹%{value:,.0f}<br>%{percent}<extra></extra>",
            )
            figure.update_layout(
                legend={
                    "orientation": "v",
                    "x": 1.0,
                    "y": 0.5,
                    "font": {"size": 10, "color": "#E7EAF0"},
                },
                margin={"l": 8, "r": 90, "t": 8, "b": 8},
                annotations=[
                    {
                        "text": f"₹{category_revenue['Monthly_Revenue'].sum():,.0f}",
                        "x": 0.39,
                        "y": 0.5,
                        "showarrow": False,
                        "font": {"size": 15, "color": "#F3F4F6"},
                    }
                ],
            )
            st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

    st.markdown("### Audience & subscriptions")
    region_col, plan_col = st.columns(2, gap="medium")
    with region_col:
        with st.container(border=True):
            st.markdown("#### Revenue by Region")
            region_revenue = (
                filtered.groupby("Region", as_index=False)["Monthly_Revenue"]
                .sum()
                .sort_values("Monthly_Revenue", ascending=False)
            )
            figure = px.bar(
                region_revenue,
                x="Monthly_Revenue",
                y="Region",
                orientation="h",
                color="Region",
                color_discrete_sequence=COLORS,
                labels={"Monthly_Revenue": "Revenue (₹)", "Region": ""},
                text_auto=".2s",
            )
            figure.update_layout(showlegend=False)
            figure.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

    with plan_col:
        with st.container(border=True):
            st.markdown("#### Revenue by Subscription Plan")
            plan_revenue = (
                filtered.groupby("Subscription_Plan", as_index=False)["Monthly_Revenue"]
                .sum()
                .sort_values("Monthly_Revenue", ascending=False)
            )
            figure = px.bar(
                plan_revenue,
                x="Monthly_Revenue",
                y="Subscription_Plan",
                orientation="h",
                color="Subscription_Plan",
                color_discrete_sequence=COLORS,
                labels={"Monthly_Revenue": "Revenue (₹)", "Subscription_Plan": ""},
                text_auto=".2s",
            )
            figure.update_layout(showlegend=False)
            figure.update_traces(textposition="outside", cliponaxis=False)
            st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

    st.markdown("### Viewing & payments")
    device_col, payment_col = st.columns(2, gap="medium")
    with device_col:
        with st.container(border=True):
            st.markdown("#### Device Usage")
            device_counts = filtered["Device"].value_counts().rename_axis("Device").reset_index(name="Viewers")
            figure = px.pie(
                device_counts,
                names="Device",
                values="Viewers",
                hole=0.66,
                color_discrete_sequence=COLORS,
            )
            figure.update_traces(
                textposition="inside",
                textinfo="percent",
                insidetextfont={"size": 10},
                hovertemplate="%{label}<br>%{value:,} viewers<br>%{percent}<extra></extra>",
            )
            figure.update_layout(
                legend={
                    "orientation": "h",
                    "x": 0.5,
                    "xanchor": "center",
                    "y": -0.06,
                    "font": {"size": 10, "color": "#E7EAF0"},
                },
                margin={"l": 10, "r": 10, "t": 8, "b": 22},
            )
            st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

    with payment_col:
        with st.container(border=True):
            st.markdown("#### Payment Method Distribution")
            payment_counts = (
                filtered["Payment_Method"].value_counts().rename_axis("Payment method").reset_index(name="Viewers")
            )
            figure = px.pie(
                payment_counts,
                names="Payment method",
                values="Viewers",
                hole=0.66,
                color_discrete_sequence=COLORS,
            )
            figure.update_traces(
                textposition="inside",
                textinfo="percent",
                insidetextfont={"size": 10},
                hovertemplate="%{label}<br>%{value:,} viewers<br>%{percent}<extra></extra>",
            )
            figure.update_layout(
                legend={
                    "orientation": "h",
                    "x": 0.5,
                    "xanchor": "center",
                    "y": -0.06,
                    "font": {"size": 10, "color": "#E7EAF0"},
                },
                margin={"l": 10, "r": 10, "t": 8, "b": 22},
            )
            st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

    with st.expander("More insights · content, ratings & 3D engagement"):
        rating_col, watch_col = st.columns(2, gap="medium")
        with rating_col:
            with st.container(border=True):
                st.markdown("#### Ratings by Category")
                category_rating = (
                    filtered.groupby("Category", as_index=False)["Rating"].sum().sort_values("Category")
                )
                figure = px.line(
                    category_rating,
                    x="Category",
                    y="Rating",
                    markers=True,
                    labels={"Rating": "Combined rating"},
                )
                figure.update_traces(line_color="#8D78FF", line_width=2.5, marker_size=6)
                st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

        with watch_col:
            with st.container(border=True):
                st.markdown("#### Watch Count by Category")
                category_watch = (
                    filtered.groupby("Category", as_index=False)["Watch_Count"]
                    .sum()
                    .sort_values("Watch_Count", ascending=False)
                )
                figure = px.bar(
                    category_watch,
                    x="Watch_Count",
                    y="Category",
                    orientation="h",
                    color="Category",
                    color_discrete_sequence=COLORS,
                    labels={"Watch_Count": "Watch count"},
                )
                figure.update_layout(showlegend=False)
                st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

        rating_dist_col, plan_rating_col = st.columns(2, gap="medium")
        with rating_dist_col:
            with st.container(border=True):
                st.markdown("#### Rating Distribution")
                rating_counts = (
                    filtered["Rating"].value_counts().sort_index().rename_axis("Rating").reset_index(name="Viewers")
                )
                figure = px.bar(
                    rating_counts,
                    x="Rating",
                    y="Viewers",
                    color="Rating",
                    color_continuous_scale=["#4C566A", "#E50914"],
                    labels={"Rating": "Rating (out of 5)"},
                    text_auto=True,
                )
                figure.update_layout(coloraxis_showscale=False)
                st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

        with plan_rating_col:
            with st.container(border=True):
                st.markdown("#### Combined Ratings by Plan")
                plan_rating = filtered.groupby("Subscription_Plan", as_index=False)["Rating"].sum()
                figure = px.pie(
                    plan_rating,
                    names="Subscription_Plan",
                    values="Rating",
                    hole=0.62,
                    color_discrete_sequence=COLORS,
                )
                figure.update_traces(textposition="inside", textinfo="percent")
                figure.update_layout(
                    legend={
                        "orientation": "h",
                        "x": 0.5,
                        "xanchor": "center",
                        "y": -0.06,
                        "font": {"color": "#E7EAF0"},
                    }
                )
                st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

        language_col, watchtime_col = st.columns(2, gap="medium")
        with language_col:
            with st.container(border=True):
                st.markdown("#### Language Distribution")
                language_counts = (
                    filtered["Language"].value_counts().rename_axis("Language").reset_index(name="Viewers")
                )
                figure = px.bar(
                    language_counts.sort_values("Viewers"),
                    x="Viewers",
                    y="Language",
                    orientation="h",
                    color="Viewers",
                    color_continuous_scale=["#4C566A", "#27C7A5"],
                )
                figure.update_layout(coloraxis_showscale=False)
                st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

        with watchtime_col:
            with st.container(border=True):
                st.markdown("#### Watch Time Distribution")
                figure = px.box(
                    filtered,
                    y="Watch_Time_Minutes",
                    points="all",
                    labels={"Watch_Time_Minutes": "Watch time (minutes)"},
                    color_discrete_sequence=["#27C7A5"],
                )
                st.plotly_chart(apply_plot_layout(figure), width="stretch", config={"displayModeBar": False})

        with st.container(border=True):
            st.markdown("#### Viewer Engagement · 3D")
            figure = px.scatter_3d(
                filtered,
                x="Watch_Count",
                y="Watch_Time_Minutes",
                z="Monthly_Revenue",
                color="Category",
                size="Rating",
                hover_name="Title",
                hover_data={
                    "Region": True,
                    "Subscription_Plan": True,
                    "Rating": True,
                    "Watch_Count": True,
                    "Watch_Time_Minutes": True,
                    "Monthly_Revenue": ":,.0f",
                },
                color_discrete_sequence=COLORS,
                labels={
                    "Watch_Count": "Watch count",
                    "Watch_Time_Minutes": "Watch time (min)",
                    "Monthly_Revenue": "Revenue (₹)",
                },
            )
            figure.update_layout(
                **PLOT_LAYOUT,
                height=440,
                scene={
                    "bgcolor": "rgba(0,0,0,0)",
                    "xaxis": {"backgroundcolor": "rgba(0,0,0,0)", "gridcolor": "rgba(255,255,255,.09)"},
                    "yaxis": {"backgroundcolor": "rgba(0,0,0,0)", "gridcolor": "rgba(255,255,255,.09)"},
                    "zaxis": {"backgroundcolor": "rgba(0,0,0,0)", "gridcolor": "rgba(255,255,255,.09)"},
                },
            )
            st.plotly_chart(figure, width="stretch", config={"displayModeBar": False})

    st.caption(
        f"Showing {len(filtered):,} of {len(data):,} viewing records · "
        f"Data from {start_date:%b %d, %Y} to {end_date:%b %d, %Y}"
    )

with explore_tab:
    st.markdown("### Explore viewing records")
    st.caption("Search across the visible rows and inspect records in your selected filters.")
    summary_columns = st.columns(4, gap="small")
    summary_columns[0].metric("Records", f"{len(filtered):,}")
    summary_columns[1].metric("Revenue", f"₹{total_revenue:,.0f}")
    summary_columns[2].metric("Average rating", f"{average_rating:.2f} / 5")
    summary_columns[3].metric("Watch time", f"{total_watch_time:,.0f} min")
    search_query = st.text_input(
        "Search records",
        placeholder="Search titles, regions, plans, devices, languages…",
        label_visibility="collapsed",
    ).strip()
    searchable = filtered
    if search_query:
        matches = filtered.astype(str).apply(
            lambda column: column.str.contains(search_query, case=False, regex=False, na=False)
        )
        searchable = filtered.loc[matches.any(axis=1)]
    st.caption(f"{len(searchable):,} matching records")
    st.dataframe(searchable, width="stretch", hide_index=True, height=440)

with quality_tab:
    st.markdown("### Dataset health")
    st.caption("A quality check of the loaded dataset before applying dashboard filters.")
    quality_metrics = st.columns(4, gap="medium")
    render_kpi(quality_metrics[0], "▤", "Total Rows", f"{len(data):,}", "loaded records")
    render_kpi(quality_metrics[1], "▦", "Total Columns", f"{len(data.columns):,}", "available fields")
    render_kpi(quality_metrics[2], "∅", "Missing Values", f"{int(data.isna().sum().sum()):,}", "empty cells")
    render_kpi(quality_metrics[3], "⧉", "Duplicate Rows", f"{int(data.duplicated().sum()):,}", "exact duplicate records")

    st.markdown("#### Column types & completeness")
    quality_table = pd.DataFrame(
        {
            "Column": data.columns,
            "Data type": data.dtypes.astype(str).values,
            "Missing values": data.isna().sum().values,
            "Missing (%)": (data.isna().mean().values * 100).round(1),
            "Unique values": data.nunique(dropna=True).values,
        }
    )
    st.dataframe(quality_table, width="stretch", hide_index=True, height=440)
