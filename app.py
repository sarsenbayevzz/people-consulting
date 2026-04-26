# app.py — People Consulting Employer Intelligence Dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from html import escape

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="People Consulting",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# GLOBAL STYLE
# =========================================================
st.markdown("""
<style>
    /* Import fonts */
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;700;800&display=swap');

    /* Root variables */
    :root {
        --want: #2ECC71;
        --not-want: #E74C3C;
        --unsure: #F1C40F;
        --unknown: #95A5A6;
        --bg: #0D0F14;
        --surface: #161920;
        --surface2: #1E2230;
        --border: #2A2F40;
        --text: #E8EAF0;
        --muted: #6B7280;
        --accent: #4F8EF7;
    }

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        background-color: var(--bg);
        color: var(--text);
        zoom: 0.90;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--surface) !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown p {
        color: var(--text) !important;
    }

    /* Headings */
    h1, h2, h3, h4 {
        font-family: 'DM Sans', sans-serif !important;
        color: var(--text) !important;
        letter-spacing: -0.02em;
    }
    h1 { font-size: 2.8rem !important; font-weight: 800 !important; }
    h2 { font-size: 28px !important; font-weight: 700 !important; }
    h3 { font-size: 28px !important; font-weight: 600 !important; }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
    }
    [data-testid="stMetricValue"] {
        font-family: 'DM Sans', sans-serif !important;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        color: var(--text) !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.8rem !important;
        color: var(--text) !important;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.75rem !important;
    }

    /* Tabs */
    [data-testid="stTabs"] [role="tab"] {
        font-family: 'DM Sans', sans-serif;
        font-weight: 700;
        font-size: 0.98rem;
        color: var(--muted) !important;
        border-radius: 6px 6px 0 0 !important;
        min-height: 46px;
        padding: 10px 16px !important;
    }
    [data-testid="stTabs"] [role="tab"] p {
        font-size: 0.98rem !important;
        line-height: 1.2 !important;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--text) !important;
        border-bottom: 3px solid var(--accent) !important;
    }

    /* Select boxes & multiselects */
    [data-baseweb="select"] {
        background: var(--surface2) !important;
        border-color: var(--border) !important;
        border-radius: 6px !important;
    }

    /* Radio nav */
    [data-testid="stRadio"] label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.8rem;
    }

    /* Divider */
    hr {
        border-color: var(--border) !important;
        margin: 1.3rem 0 !important;
    }

    /* Section cards */
    .section-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 18px 22px;
        margin-bottom: 14px;
    }

    /* Page title bar */
    .page-title {
        padding: 6px 0 22px 0;
        border-bottom: 1px solid var(--border);
        margin-bottom: 26px;
    }
    .page-title h1 { margin: 0 !important; }
    .page-subtitle {
        font-size: 1.3rem;
        color: var(--muted);
        margin-top: 2px;
        font-family: 'DM Sans', sans-serif;
    }

    /* Badge */
    .badge {
        display: inline-block;
        padding: 1px 8px;
        border-radius: 18px;
        font-size: 0.62rem;
        font-weight: 600;
        font-family: 'Syne', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-want { background: rgba(46,204,113,0.15); color: #2ECC71; border: 1px solid #2ECC71; }
    .badge-reject { background: rgba(231,76,60,0.15); color: #E74C3C; border: 1px solid #E74C3C; }
    .badge-neutral { background: rgba(149,165,166,0.15); color: #95A5A6; border: 1px solid #95A5A6; }

    /* Hide default streamlit branding, keep header so sidebar toggle stays visible */
    #MainMenu, footer { visibility: hidden; }

    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly {
        background: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# =========================================================
# COLOR CONSTANTS
# =========================================================
COLOR_WANT = "#2ECC71"
COLOR_NOT_WANT = "#E74C3C"
COLOR_UNSURE = "#F1C40F"
COLOR_UNKNOWN = "#6B7280"
COLOR_ACCENT = "#4F8EF7"
COLOR_SURFACE = "#161920"
COLOR_BORDER = "#2A2F40"
COLOR_TEXT = "#E8EAF0"
COLOR_MAN = "#3498DB"
COLOR_WOMAN = "#E91E63"
COLOR_MUTED = "#6B7280"
PLOT_FONT_SIZE = 13
PLOT_TITLE_SIZE = 23
PLOT_LEGEND_SIZE = 18
PLOT_TICK_SIZE = 14
PLOT_TEXT_SIZE = 18
PLOT_AXIS_TITLE_SIZE = 18


PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans", color=COLOR_TEXT, size=PLOT_FONT_SIZE),
    margin=dict(l=8, r=8, t=34, b=8),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLOR_TEXT, size=PLOT_LEGEND_SIZE)
    ),
    xaxis=dict(gridcolor=COLOR_BORDER, linecolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
    yaxis=dict(gridcolor=COLOR_BORDER, linecolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
)

def update_layout_with_defaults(fig, **kwargs):
    kwargs.pop("title", None)
    if "showlegend" not in kwargs:
        visible_traces = [
            trace for trace in fig.data
            if getattr(trace, "visible", None) not in ("legendonly", False)
        ]
        single_non_pie_trace = (
            len(visible_traces) <= 1
            and not any(getattr(trace, "type", "") == "pie" for trace in visible_traces)
        )
        kwargs["showlegend"] = not single_non_pie_trace
    layout = {**PLOTLY_LAYOUT, **kwargs}
    fig.update_layout(**layout)
    return fig

def apply_layout(fig, title="", height=358):
    update_layout_with_defaults(fig,
        height=height,
    )
    return fig

# =========================================================
# LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    try:
        return {
            "respondents": pd.read_csv("respondents.csv"),
            "company_2026": pd.read_csv("company_2026.csv"),
            "company_2025": pd.read_csv("company_2025.csv"),
            "factors": pd.read_csv("factors.csv"),
            "yoy": pd.read_csv("yoy_compare.csv"),
            "fcv": pd.read_csv("factor_categories_viz.csv"),
            "ftv": pd.read_csv("factor_tokens_viz.csv"),
            "scv": pd.read_csv("survey_categories_viz.csv"),
            "stv": pd.read_csv("survey_tokens_viz.csv"),
            "tmc": pd.read_csv("top_missed_companies.csv")
        }
    except FileNotFoundError as e:
        st.error(f"CSV file not found: {e}. Place all CSV files in the same directory as app.py.")
        st.stop()

data = load_data()

r   = data["respondents"]
c26 = data["company_2026"]
c25 = data["company_2025"]
f   = data["factors"]
y   = data["yoy"]
fcv = data["fcv"]
ftv = data["ftv"]
scv = data["scv"]
stv = data["stv"]
tmc = data["tmc"]

# =========================================================
# SORTING HELPERS
# =========================================================
GRADE_ORDER = ["Junior","Middle","Senior","Team Lead","Tribe Leader","C-level","C-level (CEO + CEO-1)"]
EXPERIENCE_ORDER = ["Менее 2 лет","3 - 6","7 - 10","11 - 14","15 - 19","Более 20 лет"]
AGE_ORDER = ["Младше 21","22 - 26","27 - 31","32 - 36","37 - 41","42 - 46","Старше 46"]
SORT_ORDERS = {"grade": GRADE_ORDER, "experience_group": EXPERIENCE_ORDER, "age_group": AGE_ORDER}

def sort_values(values, column):
    order = SORT_ORDERS.get(column)
    if not order:
        return sorted(values)
    idx = {v: i for i, v in enumerate(order)}
    return sorted(values, key=lambda v: (idx.get(v, len(idx)), str(v)))

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## ФИЛЬТРЫ")
    st.markdown("---")

    def multiselect_filter(label, column):
        opts = sort_values(r[column].dropna().unique().tolist(), column)
        return st.multiselect(label, options=opts)

    filters = {
        "city":           multiselect_filter("Город",         "city"),
        "grade":          multiselect_filter("Грейд",         "grade"),
        "experience":     multiselect_filter("Опыт",          "experience_group"),
        "gender":         multiselect_filter("Пол",           "gender"),
        "age":            multiselect_filter("Возраст",       "age_group"),
        "industry":       multiselect_filter("Индустрия",     "current_industry"),
        "specialization": multiselect_filter("Специализация", "specialization"),
    }

    st.markdown("---")

    page = st.radio(
        "Навигация",
        [
            "Главная",
            "Профиль респондентов",
            "Факторы",
            "Общий рейтинг",
            "Динамика",
            "Аналитика компании",
            "Аналитика опроса"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown(
        "<div style='font-size:0.6rem;color:#6B7280;text-align:center;'>"
        "People Consulting © 2026<br>Employer Intelligence Platform"
        "</div>",
        unsafe_allow_html=True
    )

# =========================================================
# APPLY FILTERS
# =========================================================
col_map = {
    "city": "city",
    "grade": "grade",
    "experience": "experience_group",
    "gender": "gender",
    "age": "age_group",
    "industry": "current_industry",
    "specialization": "specialization"
}

filtered_r = r.copy()
for key, values in filters.items():
    if values:
        filtered_r = filtered_r[filtered_r[col_map[key]].isin(values)]

any_filter = any(v for v in filters.values())

# When filters are applied, scale company data proportionally
# (in real integration this would join respondent choices to company data)
# For now, use full company data but show filter indicator
filtered_c26 = c26.copy()
filtered_c25 = c25.copy()
filtered_y   = y.copy()

filter_active = any_filter
filter_label = f"Фильтр активен · {len(filtered_r)} / {len(r)} респондентов" if filter_active else f"Все данные · {len(r)} респондентов"

# =========================================================
# REUSABLE CHART BUILDERS
# =========================================================

def bar_chart_horizontal(df, x_col, y_col, color=COLOR_ACCENT, title="", height=358, text_col=None):
    df = df.copy()
    fig = go.Figure()
    text = df[text_col] if text_col and text_col in df.columns else None
    max_val = df[x_col].max()
    fig.add_trace(go.Bar(
        y=df[y_col],
        x=df[x_col],
        orientation='h',
        marker_color=color,
        text=text,
        textposition='outside',
        textfont=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE),
        hovertemplate=f"<b>%{{y}}</b><br>{x_col}: %{{x}}<extra></extra>"
    ))
    update_layout_with_defaults(fig,
        height=height,
        yaxis=dict(autorange=True, gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
        xaxis=dict(gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT), range=[0, max_val * 1.15]),
        bargap=0.25,
    )
    return fig


def bar_chart_vertical(df, x_col, y_col, color=COLOR_ACCENT, title="", height=318, text_template=None):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df[x_col],
        y=df[y_col],
        marker_color=color,
        text=df[y_col].apply(lambda v: f"{v:.1f}%" if isinstance(v, float) else str(v)) if text_template == "pct" else None,
        textposition='outside',
        textfont=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE),
        hovertemplate=f"<b>%{{x}}</b><br>{y_col}: %{{y}}<extra></extra>"
    ))
    update_layout_with_defaults(fig,
        height=height,
        xaxis=dict(tickangle=-30, gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
        yaxis=dict(gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT)),
        bargap=0.3,
    )
    return fig


def donut_chart(labels, values, colors, title="", height=318):
    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.5,
        marker=dict(colors=colors, line=dict(color="#0D0F14", width=2)),
        textposition="outside",
        textinfo='percent',
        textfont=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE),
        hovertemplate="<b>%{label}</b><br>%{value:.1f}%<extra></extra>"
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans", color=COLOR_TEXT),
        height=height,
        margin=dict(l=38, r=38, t=34, b=52),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COLOR_TEXT, size=PLOT_LEGEND_SIZE))
    )
    return fig


def scatter_chart(df, x_col, y_col, label_col=None, color=COLOR_ACCENT, title="", height=398,
                  xref_line=None, yref_line=None, color_col=None, color_map=None):
    kwargs = dict(
        data_frame=df, x=x_col, y=y_col,
        hover_name=label_col if label_col else None,
        color=color_col if color_col else None,
        color_discrete_map=color_map if color_map else None,
    )
    if not color_col:
        kwargs['color_discrete_sequence'] = [color]
    fig = px.scatter(**kwargs)
    if label_col:
        fig.update_traces(
            text=df[label_col],
            textposition="top center",
            textfont=dict(size=PLOT_TEXT_SIZE, color=COLOR_TEXT),
            mode="markers+text",
            marker=dict(size=7)
        )
    if xref_line is not None:
        fig.add_vline(x=xref_line, line_dash="dash", line_color=COLOR_MUTED, line_width=1)
    if yref_line is not None:
        fig.add_hline(y=yref_line, line_dash="dash", line_color=COLOR_MUTED, line_width=1)
    update_layout_with_defaults(fig,
        height=height,
    )
    return fig


def grouped_bar(df, x_col, y_cols, colors, title="", height=358, names=None, show_values_inside=False):
    fig = go.Figure()
    for i, yc in enumerate(y_cols):
        trace_kwargs = dict(
            name=names[i] if names else yc,
            x=df[x_col],
            y=df[yc],
            marker_color=colors[i],
            hovertemplate=f"<b>%{{x}}</b><br>{yc}: %{{y:.1%}}<extra></extra>"
        )
        if show_values_inside:
            trace_kwargs.update({
                "text": df[yc].apply(lambda v: f"{v:.1%}"),
                "textposition": "outside",
                "texttemplate": "%{text}",
                "textfont": dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE - 2),
            })
        fig.add_trace(go.Bar(**trace_kwargs))
    update_layout_with_defaults(fig,
        barmode='group',
        height=height,
        xaxis=dict(tickangle=-30, gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
        yaxis=dict(tickformat=".0%", gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE), range=[0, 0.8], showticklabels=not show_values_inside)
    )
    return fig


def kpi_delta_color(val):
    """Return delta string with sign for metric."""
    if pd.isna(val):
        return None
    return f"{val:+.1%}"


def pct_metric(val):
    if pd.isna(val):
        return "—"
    return f"{val:.1%}"


def rank_delta(val):
    if pd.isna(val):
        return None
    if val == 0:
        return "0"
    direction = "↑" if val > 0 else "↓"
    return f"{direction}{abs(int(val))}"


def rank_delta_color(val):
    if pd.isna(val) or val == 0:
        return "off"
    return "normal" if val > 0 else "inverse"


def yoy_metric_color(metric, value):
    if pd.isna(value):
        return COLOR_MUTED
    if metric == "Want %":
        return COLOR_WANT if value >= 0 else COLOR_NOT_WANT
    return COLOR_NOT_WANT if value >= 0 else COLOR_WANT


def format_rank_with_change_html(rank, change, is_new=False):
    if pd.isna(rank):
        return "—"
    rank_text = f"#{int(rank)}"
    if is_new:
        return f"{rank_text} <span class='rank-new'>New</span>"
    if pd.isna(change) or change == 0:
        return rank_text
    direction = "↑" if change > 0 else "↓"
    delta_class = "rank-up" if change > 0 else "rank-down"
    return f"{rank_text} <span class='{delta_class}'>{direction}{abs(int(change))}</span>"


def render_quadrant_table(table_df, height):
    headers = "".join(f"<th>{escape(str(col))}</th>" for col in table_df.columns)
    rows = []
    for _, row in table_df.iterrows():
        cells = "".join(
            f"<td>{value if col == 'rank_want' else escape(str(value))}</td>"
            for col, value in row.items()
        )
        rows.append(f"<tr>{cells}</tr>")
    st.markdown(
        f"""
        <style>
            .quadrant-table-wrap {{
                max-height: {height}px;
                overflow: auto;
                border: 1px solid {COLOR_BORDER};
                border-radius: 6px;
            }}
            .quadrant-table {{
                width: 100%;
                border-collapse: collapse;
                background: {COLOR_SURFACE};
                color: {COLOR_TEXT};
                font-size: 14px;
            }}
            .quadrant-table th {{
                position: sticky;
                top: 0;
                z-index: 1;
                background: #1E2230;
                color: {COLOR_TEXT};
                font-size: 14px;
                font-weight: 700;
                text-align: left;
                padding: 8px 10px;
                border-bottom: 1px solid {COLOR_BORDER};
            }}
            .quadrant-table td {{
                padding: 9px 12px;
                border-bottom: 1px solid {COLOR_BORDER};
                font-size: 14px;
            }}
            .quadrant-table tr:last-child td {{
                border-bottom: 0;
            }}
            .rank-up {{
                color: {COLOR_WANT};
                font-weight: 800;
            }}
            .rank-down {{
                color: {COLOR_NOT_WANT};
                font-weight: 800;
            }}
            .rank-new {{
                color: {COLOR_ACCENT};
                font-weight: 800;
            }}
        </style>
        <div class="quadrant-table-wrap">
            <table class="quadrant-table">
                <thead><tr>{headers}</tr></thead>
                <tbody>{''.join(rows)}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True
    )


def format_rank_change_label(change, is_new=False):
    if is_new:
        return "New"
    if pd.isna(change):
        return ""
    if change == 0:
        return "0"
    direction = "↑" if change > 0 else "↓"
    return f"{direction}{abs(int(change))}"


def want_change_bar(df, color, sort_ascending, height=318, x_range_mode="auto"):
    chart_df = df.sort_values("want_pct_change", ascending=sort_ascending).copy()
    max_abs = chart_df["want_pct_change"].abs().max()
    if x_range_mode == "negative_to_zero":
        x_range = [-max_abs * 1.45, 0]
    else:
        x_range = [-max_abs * 1.45 if chart_df["want_pct_change"].min() < 0 else 0, max_abs * 1.45]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=chart_df["company_name"],
        x=chart_df["want_pct_change"],
        orientation="h",
        marker_color=color,
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Want % Δ: %{x:.1%}<br>"
            "Ранг: %{customdata}<extra></extra>"
        ),
        customdata=chart_df["rank_change_label"],
    ))
    for _, row in chart_df.iterrows():
        is_negative = row["want_pct_change"] < 0
        fig.add_annotation(
            x=row["want_pct_change"],
            y=row["company_name"],
            text=row["rank_change_label"],
            showarrow=False,
            xshift=10 if is_negative else -10,
            xanchor="left" if is_negative else "right",
            yanchor="middle",
            font=dict(color="#000000", size=PLOT_TEXT_SIZE),
        )
        fig.add_annotation(
            x=row["want_pct_change"],
            y=row["company_name"],
            text=row["pct_label"],
            showarrow=False,
            xshift=-12 if is_negative else 12,
            xanchor="right" if is_negative else "left",
            yanchor="middle",
            font=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE),
        )
    update_layout_with_defaults(
        fig,
        height=height,
        showlegend=False,
        yaxis=dict(autorange=True, gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
        xaxis=dict(
            tickformat=".0%",
            gridcolor=COLOR_BORDER,
            zeroline=True,
            zerolinewidth=2,
            range=x_range,
        ),
        bargap=0.25,
    )
    return fig


# =========================================================
# PAGE: ГЛАВНАЯ
# =========================================================
if page == "Главная":

    st.markdown(
        f"<div class='page-title'><h1>Рейтинг работодателей Казахстан 2026</h1>"
        f"<div class='page-subtitle'>{filter_label}</div></div>",
        unsafe_allow_html=True
    )

    # --- KPI ---
    n_resp = len(filtered_r)
    avg_score = filtered_r["survey_score"].mean() if "survey_score" in filtered_r.columns else None
    n_industry = filtered_r["current_industry"].nunique() if "current_industry" in filtered_r.columns else None
    n_city = filtered_r["city"].nunique() if "city" in filtered_r.columns else None
    pct_new = None
    if "participated_2025" in filtered_r.columns:
        participated = filtered_r["participated_2025"].astype(str).str.lower()
        pct_new = round((participated != "да").sum() / len(filtered_r) * 100) if len(filtered_r) > 0 else 0

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Респондентов", f"{n_resp}")
    k2.metric("Оценка рейтинга", f"{avg_score:.1f} / 5" if avg_score else "—")
    k3.metric("Индустрий", str(n_industry) if n_industry else "—")
    k4.metric("Городов", str(n_city) if n_city else "—")
    k5.metric("Впервые участвующих", f"{pct_new}%" if pct_new is not None else "—")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Топ-10 компаний")
        top10 = filtered_c26.nlargest(10, "want_pct")[["company_name", "want_pct", "not_want_pct"]].reset_index(drop=True)
        if not top10.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=top10["company_name"],
                x=top10["want_pct"],
                name="Хотят",
                orientation="h",
                marker_color=COLOR_WANT,
                text=top10["want_pct"].apply(lambda v: f"{v*100:.1f}%"),
                textposition="outside",
                textfont=dict(color=COLOR_TEXT, size=14),
            ))
            update_layout_with_defaults(fig,
                height=358,
                yaxis=dict(autorange="reversed", gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=14)),
                xaxis=dict(title="Want %", gridcolor=COLOR_BORDER, range=[0,1], title_font=dict(color=COLOR_TEXT, size=PLOT_AXIS_TITLE_SIZE)),
                bargap=0.2,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных")

    with col2:
        st.markdown("### Анти-топ компаний")
        anti10 = filtered_c26.nlargest(10, "not_want_pct")[["company_name", "not_want_pct", "want_pct"]].reset_index(drop=True)
        if not anti10.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=anti10["company_name"],
                x=anti10["not_want_pct"],
                name="Не хотят",
                orientation="h",
                marker_color=COLOR_NOT_WANT,
                text=anti10["not_want_pct"].apply(lambda v: f"{v*100:.1f}%"),
                textposition="outside",
                textfont=dict(color=COLOR_TEXT, size=14),
            ))
            update_layout_with_defaults(fig,
                height=358,
                yaxis=dict(autorange="reversed", gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=14)),
                xaxis=dict(title="Not Want %", gridcolor=COLOR_BORDER, range=[0,1], title_font=dict(color=COLOR_TEXT, size=PLOT_AXIS_TITLE_SIZE)),
                bargap=0.2,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных")

    st.markdown("---")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("### Гендерное распределение")
        if "gender" in filtered_r.columns:
            gender_counts = filtered_r["gender"].value_counts().reset_index()
            gender_counts.columns = ["gender", "count"]
            fig = donut_chart(
                gender_counts["gender"].tolist(),
                gender_counts["count"].tolist(),
                [COLOR_MAN, COLOR_WOMAN, COLOR_UNSURE, COLOR_UNKNOWN],
                height=278
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных")

    with col4:
        st.markdown("### Рыночный сентимент")
        avg_want = filtered_c26["want_pct"].mean()
        avg_not_want = filtered_c26["not_want_pct"].mean()
        avg_unsure = filtered_c26["unsure_pct"].mean()
        avg_unknown = filtered_c26["unknown_brand_pct"].mean()
        fig = donut_chart(
            ["Хотят", "Не хотят", "Неуверены", "Не знают"],
            [avg_want, avg_not_want, avg_unsure, avg_unknown],
            [COLOR_WANT, COLOR_NOT_WANT, COLOR_UNSURE, COLOR_UNKNOWN],
            height=278
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    # Want change from YoY
    if not filtered_y.empty and "want_pct_change" in filtered_y.columns:
        st.markdown("### Изменение Want % (год к году)")
        yoy_sorted = filtered_y.dropna(subset=["want_pct_change"]).sort_values("want_pct_change", ascending=False).head(20)
        colors_bar = [COLOR_WANT if v >= 0 else COLOR_NOT_WANT for v in yoy_sorted["want_pct_change"]]
        fig = go.Figure(go.Bar(
            x=yoy_sorted["company_name"],
            y=yoy_sorted["want_pct_change"],
            marker_color=colors_bar,
            text=yoy_sorted["want_pct_change"].apply(lambda v: f"{v*100:+.1f}%"),
            textposition="outside",
            textfont=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE),
        ))
        update_layout_with_defaults(fig,
            height=498,
            xaxis=dict(tickangle=-35, tickfont=dict(color=COLOR_TEXT, size=15)),
            yaxis=dict(range=[0, 0.4], showticklabels=False))
        st.plotly_chart(fig, use_container_width=True)


# =========================================================
# PAGE: ПРОФИЛЬ РЕСПОНДЕНТОВ
# =========================================================
elif page == "Профиль респондентов":

    st.markdown(
        f"<div class='page-title'><h1>Профиль респондентов</h1>"
        f"<div class='page-subtitle'>{filter_label}</div></div>",
        unsafe_allow_html=True
    )

    row1_col1, row1_col2, row1_col3 = st.columns([2, 2, 1.5])

    with row1_col1:
        st.markdown("### Возраст")
        if "age_group" in filtered_r.columns:
            age_data = filtered_r["age_group"].value_counts().reindex(AGE_ORDER).dropna().reset_index()
            age_data.columns = ["age_group", "count"]
            age_data["pct"] = (age_data["count"] / age_data["count"].sum() * 100).round(1)
            age_data["text"] = age_data["pct"].astype(str) + "%"
            fig = bar_chart_horizontal(age_data, "count", "age_group", color=COLOR_ACCENT, height=318, text_col="text")
            st.plotly_chart(fig, use_container_width=True)

    with row1_col2:
        st.markdown("### Опыт работы")
        if "experience_group" in filtered_r.columns:
            exp_data = filtered_r["experience_group"].value_counts().reindex(EXPERIENCE_ORDER).dropna().reset_index()
            exp_data.columns = ["experience_group", "count"]
            exp_data["pct"] = (exp_data["count"] / exp_data["count"].sum() * 100).round(1)
            exp_data["text"] = exp_data["pct"].astype(str) + "%"
            fig = bar_chart_horizontal(exp_data, "count", "experience_group", color=COLOR_UNSURE, height=318, text_col="text")
            st.plotly_chart(fig, use_container_width=True)

    with row1_col3:
        st.markdown("### Пол")
        if "gender" in filtered_r.columns:
            g = filtered_r["gender"].value_counts().reset_index()
            g.columns = ["gender", "count"]
            fig = donut_chart(g["gender"].tolist(), g["count"].tolist(),
                              [COLOR_MAN, COLOR_WOMAN, COLOR_UNSURE], height=298)
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    row2_col1, row2_col2 = st.columns(2)

    with row2_col1:
        st.markdown("### Грейд")
        if "grade" in filtered_r.columns:
            grade_data = filtered_r["grade"].value_counts().reindex(GRADE_ORDER).dropna().reset_index()
            grade_data.columns = ["grade", "count"]
            grade_data["pct"] = (grade_data["count"] / grade_data["count"].sum() * 100).round(1)
            grade_data["text"] = grade_data["pct"].astype(str) + "%"
            fig = bar_chart_horizontal(grade_data, "count", "grade", color=COLOR_WANT, height=318, text_col="text")
            st.plotly_chart(fig, use_container_width=True)

    with row2_col2:
        st.markdown("### Специализации")
        if "specialization" in filtered_r.columns:
            spec_data = filtered_r["specialization"].value_counts().head(7).reset_index()
            spec_data.columns = ["specialization", "count"]
            spec_data["pct"] = (spec_data["count"] / spec_data["count"].sum() * 100).round(1)
            spec_data["text"] = spec_data["pct"].astype(str) + "%"
            fig = bar_chart_horizontal(spec_data, "count", "specialization", color=COLOR_NOT_WANT, height=318, text_col="text")
            st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    row3_col1, row3_col2 = st.columns(2)

    with row3_col1:
        st.markdown("### Индустрии")
        if "current_industry" in filtered_r.columns:
            ind_data = filtered_r["current_industry"].value_counts().head(15).reset_index().sort_values("count", ascending=True)
            ind_data.columns = ["industry", "count"]
            ind_data["pct"] = (ind_data["count"] / ind_data["count"].sum() * 100).round(1)
            ind_data["text"] = ind_data["pct"].astype(str) + "%"
            fig = bar_chart_horizontal(ind_data, "count", "industry", color="#9B59B6", height=418, text_col="text")
            st.plotly_chart(fig, use_container_width=True)

    with row3_col2:
        st.markdown("### Города")
        if "city" in filtered_r.columns:
            city_data = filtered_r["city"].value_counts().head(15).reset_index().sort_values("count", ascending=True)
            city_data.columns = ["city", "count"]
            city_data["pct"] = (city_data["count"] / city_data["count"].sum() * 100).round(1)
            city_data["text"] = city_data["pct"].astype(str) + "%"
            fig = bar_chart_horizontal(city_data, "count", "city", color="#E67E22", height=418, text_col="text")
            st.plotly_chart(fig, use_container_width=True)


# =========================================================
# PAGE: ФАКТОРЫ
# =========================================================
elif page == "Факторы":

    st.markdown(
        f"<div class='page-title'><h1>Факторы принятия решений</h1>"
        f"<div class='page-subtitle'>{filter_label}</div></div>",
        unsafe_allow_html=True
    )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Выбор компании",
        "Отказ от оффера",
        "Причины увольнения",
        "Категории",
        "Источники решений"
    ])

    def factor_chart(factor_type, color, title):
        df = f[f["factor_type"] == factor_type].copy() if "factor_type" in f.columns else pd.DataFrame()
        if df.empty:
            st.info("Нет данных")
            return
        sort_col = "weighted_score" if "weighted_score" in df.columns else "mentions"
        df = df.nlargest(20, sort_col).sort_values(sort_col)
        df["pct"] = (df[sort_col] / df[sort_col].sum() * 100).round(1)
        df["text"] = df["pct"].astype(str) + "%"
        fig = bar_chart_horizontal(
            df, sort_col, "factor_name_clean", color=color,
            title=title, height=max(318, len(df) * 26), text_col="text"
        )
        st.plotly_chart(fig, use_container_width=True)

        if "mentions" in df.columns and "respondents" in df.columns:
            c1, c2 = st.columns(2)
            c1.metric("Всего упоминаний", f"{df['mentions'].sum():,}")
            c2.metric("Уникальных факторов", f"{len(df):,}")

    with tab1:
        factor_chart("choose", COLOR_WANT, "Топ факторов выбора работодателя")

    with tab2:
        factor_chart("reject", COLOR_NOT_WANT, "Топ причин отказа от оффера")

    with tab3:
        factor_chart("quit", COLOR_UNSURE, "Топ причин увольнения")

    with tab4:
        st.markdown("### Категории факторов")
        if not fcv.empty and "category" in fcv.columns and "count" in fcv.columns:
            fcv_sorted = fcv.sort_values("count", ascending=True)
            fcv_sorted["pct"] = (fcv_sorted["count"] / fcv_sorted["count"].sum() * 100).round(1)
            fcv_sorted["text"] = fcv_sorted["pct"].astype(str) + "%"
            c1, c2 = st.columns(2)
            with c1:
                fig = bar_chart_horizontal(fcv_sorted, "count", "category",
                                           color=COLOR_ACCENT,
                                           title="Категории по количеству упоминаний",
                                           height=max(298, len(fcv_sorted)*26),
                                           text_col="text")
                st.plotly_chart(fig, use_container_width=True)
            with c2:
                if "pct" in fcv_sorted.columns:
                    fig = donut_chart(
                        fcv_sorted["category"].tolist(),
                        fcv_sorted["pct"].tolist(),
                        px.colors.qualitative.Set2[:len(fcv_sorted)],
                        title="Доли категорий",
                        height=498
                    )
                    fig.update_layout(
                        margin=dict(t=60, b=100, l=40, r=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных")
            
        st.markdown("### Токены факторов")
        if not ftv.empty and "token" in ftv.columns and "count" in ftv.columns:
            cats = ftv["category"].unique().tolist() if "category" in ftv.columns else []
            sel_cat = st.selectbox("Категория", ["Все"] + cats)
            df_tok = ftv if sel_cat == "Все" else ftv[ftv["category"] == sel_cat]
            df_tok = df_tok.nlargest(25, "count").sort_values("count")
            fig = bar_chart_horizontal(df_tok, "count", "token", color="#9B59B6",
                                       title=f"Топ токенов: {sel_cat}", height=max(318, len(df_tok)*24))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных")

        
    with tab5:
        # Decision source
        if "main_decision_source" in filtered_r.columns:
            st.markdown("### Источники принятия решений")
            source_options = [
                "Рекомендации и отзывы сотрудников (нынешних или бывших)",
                "Впечатление от общения с HR или ИТ-рекрутером компании",
                "Репутация компании на рынке (обсуждение в чатах, пабликах, каналах)",
                "Личный опыт использования цифрового продукта или услуги компании",
                "Рейтинги",
                "Корпоративные профили на специализированных платформах",
                "Личный бренд основателя или руководителя компании",
                "Официальный сайт компании",
                "Реклама компании на профессиональных",
                "Другое: "
            ]
            source_counts = []
            for source in source_options:
                count = filtered_r["main_decision_source"].fillna("").str.contains(source, regex=False).sum()
                source_counts.append({"source": source, "count": count})
            ds = pd.DataFrame(source_counts)
            ds = ds.sort_values("count", ascending=True)
            fig = bar_chart_horizontal(ds, "count", "source", color="#E67E22",
                                       title="Источники принятия решений", height=max(278, len(ds)*26))
            st.plotly_chart(fig, use_container_width=True)



# =========================================================
# PAGE: ОБЩИЙ РЕЙТИНГ
# =========================================================
elif page == "Общий рейтинг":

    st.markdown(
        f"<div class='page-title'><h1>Общий рейтинг компаний</h1>"
        f"<div class='page-subtitle'>{filter_label}</div></div>",
        unsafe_allow_html=True
    )

    # Quadrant classification
    want_med = filtered_c26["want_pct"].median()
    nwant_med = filtered_c26["not_want_pct"].median()

    leaders       = filtered_c26[(filtered_c26["want_pct"] >= want_med) & (filtered_c26["not_want_pct"] <= nwant_med)]
    anti_top      = filtered_c26[(filtered_c26["want_pct"] < want_med)  & (filtered_c26["not_want_pct"] > nwant_med)]
    neutral       = filtered_c26[(filtered_c26["want_pct"] < want_med)  & (filtered_c26["not_want_pct"] <= nwant_med)]
    controversial = filtered_c26[(filtered_c26["want_pct"] >= want_med) & (filtered_c26["not_want_pct"] > nwant_med)]

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Меньше всего известные",
        "Лидеры",
        "Анти-топ",
        "Нейтральные",
        "Противоречивые",
        "Топ пропущенных"
    ])

    with tab1:

        # Awareness
        st.markdown("### Компании которые меньше всего известны на рынке")
        if "unknown_brand_pct" in filtered_c26.columns:
            unk_df = filtered_c26.nlargest(15, "unknown_brand_pct")[["company_name", "unknown_brand_pct"]].sort_values("unknown_brand_pct", ascending=True)
            unk_df["unknown_brand_pct"] = unk_df["unknown_brand_pct"].round(3)
            unk_df["text"] = unk_df["unknown_brand_pct"].apply(lambda v: f"{v*100:.1f}%")
            fig = bar_chart_horizontal(unk_df, "unknown_brand_pct", "company_name",
                                       color=COLOR_UNKNOWN, title="Компании с наибольшей неизвестностью (%)", height=378, text_col="text")
            st.plotly_chart(fig, use_container_width=True)

    def quadrant_table(df, label, color, title_color,sort_col="want_pct"):
        st.markdown(
            f"### <span style='color:{title_color}'>{label}</span> — {len(df)} компаний",
            unsafe_allow_html=True
        )
        if df.empty:
            st.info("Нет компаний в этом сегменте")
            return
        show_cols = [
            c for c in [
                "company_name", "want_pct", "not_want_pct",
                "unsure_pct", "unknown_brand_pct", "rank_want"
            ] if c in df.columns
        ]
        table_df = df[show_cols].sort_values(sort_col, ascending=False).reset_index(drop=True).copy()
        if "rank_want" in table_df.columns and "company_name" in filtered_c25.columns:
            companies_2025 = set(filtered_c25["company_name"].dropna().astype(str))
            table_df["_is_new_company"] = ~table_df["company_name"].astype(str).isin(companies_2025)
        if "rank_want" in table_df.columns and "rank_want_change" in filtered_y.columns:
            rank_change = filtered_y[["company_name", "rank_want_change"]].drop_duplicates("company_name")
            table_df = table_df.merge(rank_change, on="company_name", how="left")
            table_df["rank_want"] = table_df.apply(
                lambda row: format_rank_with_change_html(
                    row["rank_want"],
                    row["rank_want_change"],
                    row.get("_is_new_company", False)
                ),
                axis=1
            )
            table_df = table_df.drop(columns=["rank_want_change"])
        elif "rank_want" in table_df.columns:
            table_df["rank_want"] = table_df.apply(
                lambda row: format_rank_with_change_html(
                    row["rank_want"],
                    None,
                    row.get("_is_new_company", False)
                ),
                axis=1
            )
        if "_is_new_company" in table_df.columns:
            table_df = table_df.drop(columns=["_is_new_company"])
        pct_cols = ["want_pct", "not_want_pct", "unsure_pct", "unknown_brand_pct"]
        for col in pct_cols:
            if col in table_df.columns:
                table_df[col] = table_df[col].apply(lambda x: f"{x*100:.1f}%")
        render_quadrant_table(table_df, height=min(398, 38 + len(table_df) * 34))
        chart_df = df.nlargest(12, sort_col).copy()
        chart_df["not_want_negative"] = -chart_df["not_want_pct"]
        chart_df = chart_df.sort_values(sort_col)
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=chart_df["company_name"],
            x=chart_df["not_want_negative"],
            orientation="h",
            name="Not want",
            marker_color=COLOR_NOT_WANT,
            text=chart_df["not_want_pct"].apply(lambda v: f"{v*100:.1f}%"),
            textposition="outside",
        ))
        fig.add_trace(go.Bar(
            y=chart_df["company_name"],
            x=chart_df["want_pct"],
            orientation="h",
            name="Want",
            marker_color=color,
            text=chart_df["want_pct"].apply(lambda v: f"{v*100:.1f}%"),
            textposition="outside",
        ))
        update_layout_with_defaults(
            fig,
            height=max(278, min(12, len(chart_df)) * 33),
            barmode="relative",
            xaxis=dict(
                zeroline=True,
                zerolinewidth=2,
                tickformat=".0%",
                range=[
                    -chart_df["not_want_pct"].max() * 1.25,
                    chart_df["want_pct"].max() * 1.25
                ],
            ),
            yaxis=dict(
                tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE),
            ),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        quadrant_table(leaders, "Лидеры", COLOR_WANT, COLOR_WANT)

    with tab3:
        quadrant_table(anti_top, "Анти-топ", COLOR_WANT, COLOR_NOT_WANT, sort_col="not_want_pct")

    with tab4:
        quadrant_table(neutral, "Нейтральные", COLOR_WANT, COLOR_UNKNOWN)

    with tab5:
        quadrant_table(controversial, "Противоречивые", COLOR_WANT, COLOR_UNSURE)

    with tab6:
        st.markdown("### Топ пропущенных компаний по мнению респондентов")
        if tmc.empty:
            st.info("Нет данных top_missed_companies")
        else:
            top_missed = tmc.sort_values("count", ascending=False).head(20) if "count" in tmc.columns else tmc.head(20)
            company_col = "company" if "company" in top_missed.columns else top_missed.columns[0]
            count_col = "count" if "count" in top_missed.columns else top_missed.columns[1]
            top_missed = top_missed.sort_values(count_col, ascending=True).copy()

            fig = go.Figure(go.Bar(
                y=top_missed[company_col],
                x=top_missed[count_col],
                orientation="h",
                marker_color=COLOR_ACCENT,
                text=top_missed[count_col],
                textposition="outside",
                textfont=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE),
                hovertemplate=f"<b>%{{y}}</b><br>{count_col}: %{{x}}<extra></extra>",
            ))
            update_layout_with_defaults(
                fig,
                height=max(498, len(top_missed) * 26),
                showlegend=False,
                yaxis=dict(gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
                xaxis=dict(gridcolor=COLOR_BORDER, range=[0, top_missed[count_col].max() * 1.2], tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
                bargap=0.25,
            )
            st.plotly_chart(fig, use_container_width=True)


# =========================================================
# PAGE: ДИНАМИКА
# =========================================================
elif page == "Динамика":

    st.markdown(
        f"<div class='page-title'><h1>Динамика привлекательности</h1>"
        f"<div class='page-subtitle'>{filter_label}</div></div>",
        unsafe_allow_html=True
    )

    if filtered_y.empty:
        st.warning("Нет данных year-over-year")
    else:
        companies_2025 = set(filtered_c25["company_name"].dropna().astype(str)) if "company_name" in filtered_c25.columns else set()
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### Взлёт года (Want %)")
            if "want_pct_change" in filtered_y.columns:
                gainers = filtered_y.dropna(subset=["want_pct_change"])\
                    .sort_values("want_pct_change", ascending=False).head(5)
                if gainers.empty:
                    st.info("Нет данных для взлёта")
                else:
                    gainers = gainers.copy()
                    gainers["_is_new_company"] = ~gainers["company_name"].astype(str).isin(companies_2025)
                    gainers["rank_change_label"] = gainers.apply(
                        lambda row: format_rank_change_label(row.get("rank_want_change"), row["_is_new_company"]),
                        axis=1
                    )
                    gainers["pct_label"] = gainers["want_pct_change"].apply(lambda v: f"{v:+.1%}")
                    fig = want_change_bar(gainers, COLOR_WANT, sort_ascending=True, height=318)
                    st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Падение года (Want %)")
            if "want_pct_change" in filtered_y.columns:
                decliners = filtered_y.dropna(subset=["want_pct_change"])\
                    .sort_values("want_pct_change", ascending=True).head(5)
                if decliners.empty:
                    st.info("Нет данных для падения")
                else:
                    decliners = decliners.copy()
                    decliners["_is_new_company"] = ~decliners["company_name"].astype(str).isin(companies_2025)
                    decliners["rank_change_label"] = decliners.apply(
                        lambda row: format_rank_change_label(row.get("rank_want_change"), row["_is_new_company"]),
                        axis=1
                    )
                    decliners["pct_label"] = decliners["want_pct_change"].apply(lambda v: f"{v:+.1%}")
                    fig = want_change_bar(
                        decliners,
                        COLOR_NOT_WANT,
                        sort_ascending=False,
                        height=318,
                        x_range_mode="negative_to_zero"
                    )
                    st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.markdown("### Новые компании в рейтинге")
        if "company_name" in filtered_c26.columns and companies_2025:
            new_co = filtered_c26[~filtered_c26["company_name"].astype(str).isin(companies_2025)].copy()
            if new_co.empty:
                st.info("Нет новых компаний")
            elif "want_pct" in new_co.columns:
                new_co = new_co.nlargest(6, "want_pct").sort_values("want_pct", ascending=True)
                new_co["rank_label"] = new_co.apply(
                    lambda row: f"#{int(row['rank_want'])}" if "rank_want" in row and pd.notna(row["rank_want"]) else "",
                    axis=1
                )
                new_co["pct_label"] = new_co["want_pct"].apply(lambda v: f"{v:.1%}")
                max_want = new_co["want_pct"].max()
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    y=new_co["company_name"],
                    x=new_co["want_pct"],
                    orientation="h",
                    marker_color=COLOR_ACCENT,
                    hovertemplate="<b>%{y}</b><br>Want %: %{x:.1%}<extra></extra>",
                ))
                for _, row in new_co.iterrows():
                    fig.add_annotation(
                        x=row["want_pct"],
                        y=row["company_name"],
                        text=row["rank_label"],
                        showarrow=False,
                        xshift=-10,
                        xanchor="right",
                        yanchor="middle",
                        font=dict(color="#000000", size=PLOT_TEXT_SIZE),
                    )
                    fig.add_annotation(
                        x=row["want_pct"],
                        y=row["company_name"],
                        text=row["pct_label"],
                        showarrow=False,
                        xshift=12,
                        xanchor="left",
                        yanchor="middle",
                        font=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE),
                    )
                update_layout_with_defaults(
                    fig,
                    height=max(278, min(15, len(new_co)) * 34),
                    showlegend=False,
                    yaxis=dict(gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
                    xaxis=dict(tickformat=".0%", gridcolor=COLOR_BORDER, range=[0, max_want * 1.45]),
                    bargap=0.25,
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Нет данных Want % для новых компаний")
        else:
            st.info("Нет данных 2025 для сравнения")


# =========================================================
# PAGE: АНАЛИТИКА КОМПАНИИ
# =========================================================
elif page == "Аналитика компании":

    st.markdown(
        f"<div class='page-title'><h1>Аналитика компании</h1>"
        f"<div class='page-subtitle'>{filter_label}</div></div>",
        unsafe_allow_html=True
    )

    tab_company, tab_compare = st.tabs(["Аналитика компании", "Сравнение компаний"])

    with tab_company:
        company = st.selectbox("Выберите компанию", sorted(filtered_c26["company_name"].unique()))

        co_row = filtered_c26[filtered_c26["company_name"] == company]
        if co_row.empty:
            st.warning("Нет данных по выбранной компании")
        else:
            co = co_row.iloc[0]

            # YoY data for company
            yoy_co = filtered_y[filtered_y["company_name"] == company].iloc[0] if not filtered_y.empty and "company_name" in filtered_y.columns and company in filtered_y["company_name"].values else None

            # --- KPI ---
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Хотят работать",  pct_metric(co.get("want_pct")),
                      delta=kpi_delta_color(yoy_co["want_pct_change"]) if yoy_co is not None and "want_pct_change" in yoy_co else None)
            k2.metric("Не хотят",        pct_metric(co.get("not_want_pct")),
                      delta=kpi_delta_color(yoy_co["not_want_pct_change"]) if yoy_co is not None and "not_want_pct_change" in yoy_co else None,
                      delta_color="inverse")
            k3.metric("Неуверены",       pct_metric(co.get("unsure_pct")))
            k4.metric("Не знают",        pct_metric(co.get("unknown_brand_pct")))
            k5.metric("Ранг Want",       f"#{int(co['rank_want'])}" if "rank_want" in co and pd.notna(co["rank_want"]) else "—",
                      delta=rank_delta(yoy_co["rank_want_change"]) if yoy_co is not None and "rank_want_change" in yoy_co else None,
                      delta_color=rank_delta_color(yoy_co["rank_want_change"]) if yoy_co is not None and "rank_want_change" in yoy_co else "normal")

            st.markdown("---")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Структура восприятия")
                labels = ["Хотят", "Не хотят", "Неуверены", "Не знают"]
                values = [
                    co.get("want_pct", 0),
                    co.get("not_want_pct", 0),
                    co.get("unsure_pct", 0),
                    co.get("unknown_brand_pct", 0)
                ]
                fig = donut_chart(
                    labels, values,
                    [COLOR_WANT, COLOR_NOT_WANT, COLOR_UNSURE, COLOR_UNKNOWN],
                    title=f"{company}: восприятие бренда",
                    height=428
                )
                fig.update_layout(margin=dict(l=50, r=90, t=36, b=80))
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                if yoy_co is not None:
                    st.markdown("### Год к году")
                    changes = {}
                    for col_name, label in [
                        ("want_pct_change", "Want %"),
                        ("not_want_pct_change", "Not Want %"),
                        ("unsure_pct_change", "Unsure %"),
                        ("unknown_brand_pct_change", "Unknown %"),
                    ]:
                        if col_name in yoy_co and pd.notna(yoy_co[col_name]):
                            changes[label] = yoy_co[col_name]
                    if changes:
                        yoy_df = pd.DataFrame({"Метрика": list(changes.keys()), "Изменение": list(changes.values())})
                        colors_yoy = [
                            yoy_metric_color(metric, value)
                            for metric, value in zip(yoy_df["Метрика"], yoy_df["Изменение"])
                        ]
                        fig = go.Figure(go.Bar(
                            x=yoy_df["Метрика"],
                            y=yoy_df["Изменение"],
                            marker_color=colors_yoy,
                            text=yoy_df["Изменение"].apply(lambda v: f"{v:+.1%}"),
                            textposition="outside",
                            textfont=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE)
                        ))
                        max_abs = yoy_df["Изменение"].abs().max()
                        y_range = [-0.01, 0.01] if max_abs == 0 else [-max_abs * 1.45, max_abs * 1.45]
                        update_layout_with_defaults(
                            fig,
                            height=378,
                            showlegend=False,
                            yaxis=dict(
                                tickformat=".0%",
                                gridcolor=COLOR_BORDER,
                                tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE),
                                range=y_range,
                            ),
                            xaxis=dict(gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
                            bargap=0.35,
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.markdown("### Относительно рынка")
                    comp_data = pd.DataFrame({
                        "Метрика": ["Want %", "Not Want %", "Unsure %", "Unknown %"],
                        "Компания": [co.get("want_pct",0), co.get("not_want_pct",0), co.get("unsure_pct",0), co.get("unknown_brand_pct",0)],
                        "Рынок (avg)": [
                            filtered_c26["want_pct"].mean(),
                            filtered_c26["not_want_pct"].mean(),
                            filtered_c26["unsure_pct"].mean() if "unsure_pct" in filtered_c26.columns else 0,
                            filtered_c26["unknown_brand_pct"].mean() if "unknown_brand_pct" in filtered_c26.columns else 0,
                        ]
                    })
                    fig = grouped_bar(comp_data, "Метрика", ["Компания", "Рынок (avg)"],
                                      [COLOR_ACCENT, COLOR_MUTED],
                                      title="Сравнение с рынком", height=318)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # ── ROW 2: Позиция на рынке  +  Три ранга ───────────────────
            col3, col4 = st.columns([3, 2])

            with col3:
                # Scatter: все компании серые, выбранная — яркая
                st.markdown("### Позиция на рынке")

                scatter_df = filtered_c26.copy()
                scatter_df["_is_selected"] = scatter_df["company_name"] == company
                others = scatter_df[~scatter_df["_is_selected"]]
                selected = scatter_df[scatter_df["_is_selected"]]

                want_med  = scatter_df["want_pct"].median()
                nwant_med = scatter_df["not_want_pct"].median()

                fig = go.Figure()
                # Background: все остальные компании
                fig.add_trace(go.Scatter(
                    x=others["want_pct"],
                    y=others["not_want_pct"],
                    mode="markers",
                    marker=dict(color=COLOR_MUTED, size=7, opacity=0.5),
                    text=others["company_name"],
                    hovertemplate="<b>%{text}</b><br>Want: %{x:.1%}<br>Not Want: %{y:.1%}<extra></extra>",
                    name="Другие компании",
                    showlegend=False,
                ))
                # Foreground: выбранная компания
                if not selected.empty:
                    fig.add_trace(go.Scatter(
                        x=selected["want_pct"],
                        y=selected["not_want_pct"],
                        mode="markers+text",
                        marker=dict(color=COLOR_ACCENT, size=23, line=dict(color=COLOR_TEXT, width=2)),
                        text=[company],
                        textposition="top center",
                        textfont=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE - 2),
                        hovertemplate=f"<b>{company}</b><br>Want: %{{x:.1%}}<br>Not Want: %{{y:.1%}}<extra></extra>",
                        name=company,
                        showlegend=False,
                    ))
                # Квадрантные линии
                fig.add_vline(x=want_med, line_dash="dot", line_color=COLOR_ACCENT, line_width=2)
                fig.add_hline(y=nwant_med, line_dash="dot", line_color=COLOR_ACCENT, line_width=2)
                # Подписи квадрантов
                x_max = scatter_df["want_pct"].max()
                y_max = scatter_df["not_want_pct"].max()
                for qtext, qx, qy, qcolor in [
                    ("Лидер", x_max * 0.97, nwant_med * 0.1, COLOR_WANT),
                    ("Анти-топ", want_med * 0.05, y_max * 0.95, COLOR_NOT_WANT),
                    ("Нейтральный", want_med * 0.05, nwant_med * 0.1, COLOR_MUTED),
                    ("Противоречивый", x_max * 0.97, y_max * 0.95, COLOR_UNSURE),
                ]:
                    fig.add_annotation(
                        x=qx, y=qy, text=qtext,
                        showarrow=False,
                        font=dict(color=qcolor, size=15, family="DM Sans"),
                        opacity=0.7,
                    )
                update_layout_with_defaults(
                    fig, height=418, showlegend=False,
                    xaxis=dict(title="Want %", tickformat=".0%", gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
                    yaxis=dict(title="Not Want %", tickformat=".0%", gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
                )
                st.plotly_chart(fig, use_container_width=True)

            with col4:
                # Три ранга: Want, Not Want, Unknown
                st.markdown("### Три ранга")

                total_cos = len(filtered_c26)
                rank_items = [
                    ("Ранг по Want",        "rank_want",         "want_pct_change",         COLOR_WANT,),
                    ("Ранг по Not Want",    "rank_not_want",     "not_want_pct_change",     COLOR_NOT_WANT,),
                    ("Ранг по Unknown",     "rank_unknown_brand","unknown_brand_pct_change", COLOR_UNKNOWN,),
                ]

                for rank_label, rank_col, change_col, rank_color in rank_items:
                    rank_val = co.get(rank_col)
                    change_val = yoy_co[change_col] if yoy_co is not None and change_col in yoy_co else None

                    if pd.notna(rank_val):
                        rank_int = int(rank_val)
                        pct_rank = rank_int / total_cos  # 0=лучший, 1=худший
                        bar_color = rank_color

                        # Arrow and delta text
                        if change_val is not None and not pd.isna(change_val):
                            delta_sign = "▲" if change_val > 0 else ("▼" if change_val < 0 else "—")
                            delta_text = f"{delta_sign} {abs(change_val):.1%}"
                        else:
                            delta_text = ""

                        st.markdown(
                            f"""
                            <div style="
                                background: #161920;
                                border: 1px solid #2A2F40;
                                border-left: 4px solid {bar_color};
                                border-radius: 6px;
                                padding: 12px 16px;
                                margin-bottom: 10px;
                            ">
                                <div style="font-size:0.6rem;color:#6B7280;text-transform:uppercase;letter-spacing:0.08em;font-family:'DM Sans',sans-serif;">
                                    {rank_label}
                                </div>
                                <div style="display:flex;align-items:baseline;gap:10px;margin-top:2px;">
                                    <span style="font-size:2.2rem;font-weight:800;font-family:DM Sans,sans-serif;color:{bar_color};">
                                        #{rank_int}
                                    </span>
                                    <span style="font-size:0.8rem;color:#6B7280;">из {total_cos}</span>
                                    {"<span style='font-size:0.7rem;color:#6B7280;margin-left:auto;'>" + delta_text + "</span>" if delta_text else ""}
                                </div>
                                <div style="margin-top:6px;background:#2A2F40;border-radius:2px;height:4px;overflow:hidden;">
                                    <div style="width:{pct_rank*100:.1f}%;background:{bar_color};height:100%;border-radius:2px;opacity:0.8;"></div>
                                </div>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(f"**{rank_label}:** —")

            st.markdown("---")
                    
    with tab_compare:
        st.markdown("### Сравнение двух или более компаний")
        company_options = sorted(filtered_c26["company_name"].unique())
        default_companies = company_options[:2] if len(company_options) >= 2 else company_options
        compare_companies = st.multiselect(
            "Выберите компании",
            company_options,
            default=default_companies,
            max_selections=6,
            key="compare_companies_tab"
        )

        if len(compare_companies) < 2:
            st.info("Выберите минимум две компании для сравнения")
        else:
            comp_df = filtered_c26[filtered_c26["company_name"].isin(compare_companies)].copy()
            metrics = [c for c in ["want_pct", "not_want_pct", "unsure_pct", "unknown_brand_pct"] if c in comp_df.columns]
            metric_labels = {"want_pct": "Want %", "not_want_pct": "Not Want %",
                             "unsure_pct": "Unsure %", "unknown_brand_pct": "Unknown %"}
            colors_comp = [COLOR_WANT, COLOR_NOT_WANT, COLOR_UNSURE, COLOR_UNKNOWN]
            
            fig = grouped_bar(
                comp_df, "company_name", metrics,
                colors_comp[:len(metrics)],
                title="Сравнение компаний",
                names=[metric_labels.get(m, m) for m in metrics],
                height=418,
                show_values_inside=True
            )
            st.plotly_chart(fig, use_container_width=True)

            if "want_pct" in comp_df.columns and "not_want_pct" in comp_df.columns:
                st.markdown("### Позиция на рынке")
                scatter_df = comp_df.copy()
                market_median_want = filtered_c26["want_pct"].median()
                market_median_not_want = filtered_c26["not_want_pct"].median()

                scatter_df["qcolor"] = scatter_df.apply(lambda row: (
                    COLOR_WANT if row["want_pct"] >= market_median_want and row["not_want_pct"] <= market_median_not_want else
                    COLOR_NOT_WANT if row["want_pct"] <= market_median_want and row["not_want_pct"] >= market_median_not_want else
                    COLOR_MUTED if row["want_pct"] <= market_median_want and row["not_want_pct"] <= market_median_not_want else
                    COLOR_UNSURE
                ), axis=1)

                fig = go.Figure()
                # Background: все остальные компании
                fig.add_trace(go.Scatter(
                    x=others["want_pct"],
                    y=others["not_want_pct"],
                    mode="markers",
                    marker=dict(color=COLOR_MUTED, size=7, opacity=0.5),
                    text=others["company_name"],
                    hovertemplate="<b>%{text}</b><br>Want: %{x:.1%}<br>Not Want: %{y:.1%}<extra></extra>",
                    name="Другие компании",
                    showlegend=False,
                ))
                fig.add_trace(go.Scatter(
                    x=scatter_df["want_pct"],
                    y=scatter_df["not_want_pct"],
                    mode="markers+text",
                    marker=dict(color=scatter_df["qcolor"].tolist(), size=23, line=dict(color=COLOR_TEXT, width=2)),
                    text=scatter_df["company_name"],
                    textposition="top center",
                    textfont=dict(color=COLOR_TEXT, size=PLOT_TEXT_SIZE - 2),
                    hovertemplate="<b>%{text}</b><br>Want: %{x:.1%}<br>Not Want: %{y:.1%}<extra></extra>",
                    showlegend=False,
                ))
                fig.add_vline(x=market_median_want, line_dash="dot", line_color=COLOR_ACCENT, line_width=2)
                fig.add_hline(y=market_median_not_want, line_dash="dot", line_color=COLOR_ACCENT, line_width=2)

                x_max = scatter_df["want_pct"].max()
                y_max = scatter_df["not_want_pct"].max()
                for qtext, qx, qy, qcolor in [
                    ("Лидер", x_max * 0.97, market_median_not_want * 0.1, COLOR_WANT),
                    ("Анти-топ", market_median_want * 0.05, y_max * 0.95, COLOR_NOT_WANT),
                    ("Нейтральный", market_median_want * 0.05, market_median_not_want * 0.1, COLOR_MUTED),
                    ("Противоречивый", x_max * 0.97, y_max * 0.95, COLOR_UNSURE),
                ]:
                    fig.add_annotation(
                        x=qx, y=qy, text=qtext,
                        showarrow=False,
                        font=dict(color=qcolor, size=23, family="DM Sans"),
                        opacity=0.7,
                    )
                update_layout_with_defaults(
                    fig, height=498, showlegend=False,
                    xaxis=dict(title="Want %", tickformat=".0%", gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
                    yaxis=dict(title="Not Want %", tickformat=".0%", gridcolor=COLOR_BORDER, tickfont=dict(color=COLOR_TEXT, size=PLOT_TICK_SIZE)),
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Нет данных для построения позиции на рынке")

            


# =========================================================
# PAGE: АНАЛИТИКА ОПРОСА
# =========================================================
elif page == "Аналитика опроса":

    st.markdown(
        f"<div class='page-title'><h1>Аналитика опроса</h1>"
        f"<div class='page-subtitle'>{filter_label}</div></div>",
        unsafe_allow_html=True
    )

    # UX Score KPI
    if "survey_score" in filtered_r.columns and len(filtered_r) > 0:
        if "ready_for_followup" in filtered_r.columns:
            followup_count = filtered_r["ready_for_followup"].astype(str).str.strip().eq("Да").sum()
            st.metric("Готовы к фидбэку", f"{followup_count:,}")
        else:
            st.metric("Готовы к фидбэку", "—")
        st.markdown("---")
    
    CATEGORY_RU = {
        "too_many_companies": "Сократить количество компаний в списке",
        "other": "Другие предложения",
        "too_long": "Сделать опрос короче",
        "answer_options": "Улучшить варианты ответов",
        "add_companies": "Добавить больше компаний",
        "scale_issues": "Улучшить шкалу оценок",
        "open_questions": "Сократить количество открытых вопросов",
        "ux_ui": "Улучшить интерфейс и удобство заполнения",
        "structure": "Упростить структуру и логику опроса",
        "add_info": "Добавить больше пояснений или информации",
    }
    
    scv["category_ru"] = (scv["category"].map(CATEGORY_RU).fillna(scv["category"]))
    stv["category_ru"] = (stv["category"].map(CATEGORY_RU).fillna(stv["category"]))
    
    st.markdown("### Категории по улучшению опроса по мнению респондентов")
    if not scv.empty and "category" in scv.columns and "count" in scv.columns:
        scv_sorted = scv.sort_values("count", ascending=True)
        scv_sorted["pct"] = (scv_sorted["count"] / scv_sorted["count"].sum() * 100).round(1)
        scv_sorted["text"] = scv_sorted["pct"].astype(str) + "%"
        fig = bar_chart_horizontal(scv_sorted, "count", "category_ru",
                                    color=COLOR_ACCENT, title="Количество упоминаний",
                                    height=max(498, len(scv_sorted)*28), text_col="text")
        st.plotly_chart(fig, use_container_width=True)

        # Per-category breakdown
        st.markdown("### Токены по категориям")
        if not stv.empty and "token" in stv.columns and "count" in stv.columns:
            cats_stv = stv["category_ru"].unique().tolist() if "category_ru" in stv.columns else []
            sel_cat = st.selectbox("Категория", ["Все"] + cats_stv, key="stv_cat")
            df_stv = stv if sel_cat == "Все" else stv[stv["category_ru"] == sel_cat]
            df_stv = df_stv.nlargest(30, "count").sort_values("count")
            fig = bar_chart_horizontal(df_stv, "count", "token", color="#9B59B6",
                                    title=f"Токены: {sel_cat}", height=max(358, len(df_stv)*24))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Нет данных STV")
    else:
        st.info("Нет данных SCV")
