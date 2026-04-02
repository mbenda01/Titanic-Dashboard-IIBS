# app.py
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import json
import logging
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))
from data.loader import load_titanic, get_age_group  # noqa: E402

st.set_page_config(
    page_title="RMS Titanic · Dashboard",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Palette ────────────────────────────────────────────────────────────────────
C = {
    "bg": "#F0F4F8",
    "surface": "#FFFFFF",
    "navy": "#1A2332",
    "navy2": "#243044",
    "mint": "#4ECBA0",
    "mint_l": "#7EDCB8",
    "coral": "#F07A65",
    "sky": "#5BA8F5",
    "amber": "#F5B942",
    "text": "#1A2332",
    "muted": "#8A9BB0",
    "border": "#E1E8F0",
    "card_dark": "#1A2332",
}

SURVIVED_COLORS = [C["coral"], C["mint"]]
CLASS_COLORS = [C["navy"], C["mint"], C["coral"]]
SEX_COLORS = [C["sky"], C["mint"]]


def rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"


PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color=C["text"], family="'Inter', sans-serif", size=12),
    margin=dict(t=40, b=30, l=10, r=10),
    legend=dict(
        bgcolor=rgba(C["surface"], 0.95),
        bordercolor=rgba(C["border"], 1.0),
        borderwidth=1,
    ),
)


# ── Logger ─────────────────────────────────────────────────────────────────────
def _get_logger():
    log = logging.getLogger("titanic_app")
    if not log.handlers:
        os.makedirs("logs", exist_ok=True)
        h = logging.FileHandler("logs/app.log", encoding="utf-8")
        h.setFormatter(logging.Formatter("%(message)s"))
        log.addHandler(h)
        log.setLevel(logging.INFO)
    return log


def _json_safe(obj):
    import numpy as np
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(i) for i in obj]
    return obj


def log_event(event_type: str, details: dict):
    _get_logger().info(json.dumps({
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "event_type": event_type,
        "details": _json_safe(details),
    }, ensure_ascii=False))


@st.cache_data(show_spinner="Chargement 🚢")
def get_data():
    return get_age_group(load_titanic())


CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800\
&family=Space+Grotesk:wght@500;600;700&display=swap');
html, body, .stApp {
    background-color:#F0F4F8 !important;
    color:#1A2332; font-family:'Inter',sans-serif;
}
.block-container {
    padding-top:0 !important; padding-bottom:1rem !important;
    padding-left:1.5rem !important; padding-right:1.5rem !important;
}
#MainMenu, header, footer { visibility:hidden; height:0; }
[data-testid="stToolbar"] { display:none; }
section[data-testid="stSidebar"] {
    background:#1A2332 !important;
    border-right:none !important; width:260px !important;
}
section[data-testid="stSidebar"] > div { padding:0 !important; }
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div,
section[data-testid="stSidebar"] label { color:#FFFFFF !important; }
section[data-testid="stSidebar"] .stMultiSelect label {
    font-size:.65rem !important; font-weight:700 !important;
    letter-spacing:.12em !important; text-transform:uppercase !important;
    color:rgba(255,255,255,0.5) !important; margin-bottom:.3rem !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child {
    background:rgba(255,255,255,0.07) !important;
    border:1px solid rgba(255,255,255,0.12) !important;
    border-radius:10px !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div:first-child:focus-within {
    border-color:#4ECBA0 !important;
    box-shadow:0 0 0 3px rgba(78,203,160,0.15) !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] {
    background:rgba(78,203,160,0.2) !important;
    border:1px solid rgba(78,203,160,0.4) !important;
    border-radius:6px !important; color:#7EDCB8 !important;
    font-size:.7rem !important; font-weight:600 !important;
}
section[data-testid="stSidebar"] [data-baseweb="tag"] span[role="presentation"] {
    color:rgba(78,203,160,0.7) !important;
}
[data-baseweb="popover"] { background:#243044 !important; }
[data-baseweb="menu"] li { color:#fff !important; background:transparent !important; }
[data-baseweb="menu"] li:hover { background:rgba(78,203,160,0.15) !important; }
section[data-testid="stSidebar"] [data-baseweb="select"] input { color:#fff !important; }
.kpi-grid {
    display:grid; grid-template-columns:repeat(4,1fr);
    gap:1rem; margin-bottom:1.4rem;
}
.kpi-card {
    background:#FFFFFF; border-radius:14px; overflow:hidden;
    box-shadow:0 2px 8px rgba(0,0,0,0.06); border:1px solid #E1E8F0;
    display:flex; flex-direction:column; transition:transform .2s, box-shadow .2s;
}
.kpi-card:hover { transform:translateY(-2px); box-shadow:0 8px 20px rgba(0,0,0,0.1); }
.kpi-header {
    background:#1A2332; padding:.6rem 1rem;
    display:flex; align-items:center; justify-content:space-between;
}
.kpi-title {
    font-size:.62rem; font-weight:700; letter-spacing:.12em;
    text-transform:uppercase; color:rgba(255,255,255,0.6);
}
.kpi-icon {
    width:28px; height:28px; border-radius:8px;
    display:flex; align-items:center; justify-content:center; font-size:.85rem;
}
.kpi-body { padding:.9rem 1rem 1rem; flex:1; }
.kpi-value {
    font-family:'Space Grotesk',sans-serif; font-size:2rem; font-weight:700;
    color:#1A2332; line-height:1; letter-spacing:-.03em;
}
.kpi-delta {
    font-size:.72rem; font-weight:500; margin-top:.4rem;
    display:flex; align-items:center; gap:.3rem;
}
[data-testid="stTabs"] {
    background:#FFFFFF; border-radius:12px 12px 0 0;
    border:1px solid #E1E8F0; border-bottom:none; padding:.2rem .5rem 0;
}
[data-testid="stTabs"] button {
    font-family:'Inter',sans-serif !important; font-size:.75rem !important;
    font-weight:600 !important; letter-spacing:.05em !important;
    text-transform:uppercase; color:#8A9BB0 !important;
    padding:.65rem 1.1rem !important; border-radius:0 !important;
    border-bottom:2px solid transparent !important; transition:all .2s;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color:#1A2332 !important;
    border-bottom:2px solid #4ECBA0 !important;
    background:rgba(78,203,160,0.06) !important;
}
[data-testid="stTabs"] button:hover {
    color:#1A2332 !important; background:#F0F4F8 !important;
}
.section-title {
    font-size:.72rem; font-weight:700; letter-spacing:.1em;
    text-transform:uppercase; color:#8A9BB0; margin:1rem 0 .6rem;
    display:flex; align-items:center; gap:.6rem;
}
.section-title::after { content:''; flex:1; height:1px; background:#E1E8F0; }
.page-header {
    background:#FFFFFF; border:1px solid #E1E8F0; border-radius:14px;
    padding:1rem 1.4rem; margin-bottom:1.2rem;
    display:flex; align-items:center; gap:1rem;
    box-shadow:0 1px 4px rgba(0,0,0,0.04);
}
.page-header-bar {
    width:4px; height:40px; border-radius:4px;
    background:linear-gradient(180deg,#4ECBA0,#5BA8F5); flex-shrink:0;
}
.page-header-title {
    font-family:'Space Grotesk',sans-serif; font-size:1.1rem; font-weight:700;
    color:#1A2332; margin:0; letter-spacing:-.02em;
}
.page-header-sub { font-size:.72rem; color:#8A9BB0; margin-top:.15rem; }
.deco-divider { display:flex; align-items:center; gap:1rem; margin:1.2rem 0; }
.deco-divider::before, .deco-divider::after {
    content:''; flex:1; height:1px; background:#E1E8F0;
}
.deco-divider span {
    color:#8A9BB0; font-size:.6rem; letter-spacing:.18em;
    text-transform:uppercase; white-space:nowrap; font-weight:700;
}
.filter-summary {
    background:#FFFFFF; border:1px solid #E1E8F0; border-radius:12px;
    padding:.9rem 1.2rem; margin-bottom:1.2rem;
    box-shadow:0 1px 4px rgba(0,0,0,0.04);
}
.filter-row { display:flex; flex-wrap:wrap; gap:.45rem; margin-bottom:.45rem; }
.filter-chip {
    display:inline-flex; align-items:center; gap:.3rem;
    padding:.25rem .65rem; border-radius:20px; font-size:.68rem; font-weight:600;
}
.chip-navy {
    background:rgba(26,35,50,0.08); color:#1A2332;
    border:1px solid rgba(26,35,50,0.18);
}
.chip-mint {
    background:rgba(78,203,160,0.1); color:#2D9E77;
    border:1px solid rgba(78,203,160,0.3);
}
.chip-sky {
    background:rgba(91,168,245,0.1); color:#5BA8F5;
    border:1px solid rgba(91,168,245,0.3);
}
.chip-coral {
    background:rgba(240,122,101,0.1); color:#F07A65;
    border:1px solid rgba(240,122,101,0.3);
}
.filter-count {
    font-family:'Space Grotesk',sans-serif; font-size:1.6rem;
    font-weight:700; color:#1A2332;
}
.filter-pct { font-size:.7rem; color:#8A9BB0; margin-left:.3rem; }
.stDownloadButton > button {
    background:#1A2332 !important; color:#fff !important;
    border:none !important; border-radius:10px !important;
    font-family:'Inter',sans-serif !important; font-size:.75rem !important;
    font-weight:600 !important; letter-spacing:.06em !important;
    text-transform:uppercase !important; padding:.5rem 1.4rem !important;
    transition:all .2s !important;
}
.stDownloadButton > button:hover {
    background:#243044 !important;
    box-shadow:0 4px 14px rgba(26,35,50,0.25) !important;
    transform:translateY(-1px) !important;
}
::-webkit-scrollbar { width:5px; height:5px; }
::-webkit-scrollbar-track { background:#F0F4F8; }
::-webkit-scrollbar-thumb { background:rgba(78,203,160,0.3); border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#4ECBA0; }
[data-testid="stDataFrame"] { border:1px solid #E1E8F0; border-radius:10px; }
.sb-logo {
    background:#243044; padding:1.4rem 1.2rem 1rem;
    border-bottom:1px solid rgba(255,255,255,0.07); margin-bottom:.5rem;
}
.sb-logo-row { display:flex; align-items:center; gap:.8rem; }
.sb-logo-icon {
    width:42px; height:42px; border-radius:12px;
    background:rgba(78,203,160,0.2); border:1px solid rgba(78,203,160,0.3);
    display:flex; align-items:center; justify-content:center; font-size:1.4rem;
}
.sb-logo-name {
    font-family:'Space Grotesk',sans-serif; font-size:.95rem;
    font-weight:700; color:#fff; letter-spacing:.04em;
}
.sb-logo-sub {
    font-size:.6rem; color:rgba(255,255,255,0.4);
    letter-spacing:.12em; text-transform:uppercase; margin-top:.15rem;
}
.sb-section {
    padding:.6rem 1.2rem .2rem; font-size:.6rem; font-weight:700;
    letter-spacing:.14em; text-transform:uppercase;
    color:rgba(255,255,255,0.35); display:flex; align-items:center; gap:.5rem;
}
.sb-dot { width:5px; height:5px; border-radius:50%; display:inline-block; flex-shrink:0; }
.sb-footer {
    padding:.8rem 1.2rem; font-size:.58rem; color:rgba(255,255,255,0.25);
    letter-spacing:.1em; text-transform:uppercase;
    border-top:1px solid rgba(255,255,255,0.06); margin-top:auto;
}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)


def section(title):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def divider(label):
    st.markdown(
        f'<div class="deco-divider"><span>{label}</span></div>',
        unsafe_allow_html=True,
    )


def page_header(emoji, title, subtitle, page_key):
    st.markdown(f"""
    <div class="page-header">
      <div class="page-header-bar"></div>
      <div>
        <div class="page-header-title">{emoji} {title}</div>
        <div class="page-header-sub">{subtitle}</div>
      </div>
    </div>""", unsafe_allow_html=True)
    log_event("page_visit", {"page": page_key})


def kpi_card(title, value, delta_text, delta_color, icon_emoji, icon_bg):
    return (
        '<div class="kpi-card"><div class="kpi-header">'
        f'<span class="kpi-title">{title}</span>'
        f'<span class="kpi-icon" style="background:{icon_bg}">{icon_emoji}</span>'
        '</div><div class="kpi-body">'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-delta" style="color:{delta_color}">{delta_text}</div>'
        '</div></div>'
    )


def styled_fig(fig, light=True):
    fig.update_layout(**PLOTLY_BASE)
    fig.update_xaxes(
        gridcolor=rgba(C["border"], 1.0),
        zerolinecolor=rgba(C["border"], 1.0),
        linecolor=rgba(C["border"], 1.0),
    )
    fig.update_yaxes(
        gridcolor=rgba(C["border"], 1.0),
        zerolinecolor=rgba(C["border"], 1.0),
        linecolor=rgba(C["border"], 1.0),
    )
    return fig


def render_sidebar(df):
    st.sidebar.markdown("""
    <div class="sb-logo">
      <div class="sb-logo-row">
        <div class="sb-logo-icon">🚢</div>
        <div>
          <div class="sb-logo-name">TITANIC</div>
          <div class="sb-logo-sub">1912 · 891 passagers</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.sidebar.markdown(
        '<div class="sb-section">'
        '<span class="sb-dot" style="background:#5BA8F5"></span>Classe de cabine'
        '</div>',
        unsafe_allow_html=True,
    )
    classes = sorted(df["pclass"].unique())
    sel_classes = st.sidebar.multiselect(
        "Classe de cabine",
        options=classes, default=classes,
        format_func=lambda x: f"Classe {x}",
        label_visibility="hidden", key="filter_class",
    )

    st.sidebar.markdown(
        '<div class="sb-section">'
        '<span class="sb-dot" style="background:#4ECBA0"></span>Genre'
        '</div>',
        unsafe_allow_html=True,
    )
    sexes = df["sex"].unique().tolist()
    sel_sexes = st.sidebar.multiselect(
        "Genre",
        options=sexes, default=sexes,
        format_func=lambda x: "Homme" if x == "male" else "Femme",
        label_visibility="hidden", key="filter_sex",
    )

    st.sidebar.markdown(
        '<div class="sb-section">'
        '<span class="sb-dot" style="background:#F07A65"></span>Tranche age'
        '</div>',
        unsafe_allow_html=True,
    )
    age_groups = df["age_group"].cat.categories.tolist()
    sel_ages = st.sidebar.multiselect(
        "Tranche age",
        options=age_groups, default=age_groups,
        label_visibility="hidden", key="filter_age",
    )

    st.sidebar.markdown(
        '<div class="sb-footer">Projet DevOps · Data/IA 2024-2025</div>',
        unsafe_allow_html=True,
    )
    return sel_classes, sel_sexes, sel_ages


def apply_filters(df, cls, sex, ages):
    if not cls or not sex or not ages:
        return df.iloc[0:0]
    return df[df["pclass"].isin(cls) & df["sex"].isin(sex) & df["age_group"].isin(ages)]


def page_vue_generale(df, dff):
    page_header("🌊", "Vue Generale", "Synthese · profil des passagers filtres", "vue_generale")

    total = len(dff)
    survivors = int(dff["survived"].sum()) if total else 0
    rate = survivors / total * 100 if total else 0
    avg_age = int(round(dff["age"].mean())) if total else 0
    avg_fare = dff["fare"].mean() if total else 0

    kpis_html = (
        kpi_card("Passagers", f"{total:,}",
                 "+0 vs total", C["muted"], "👥", "rgba(91,168,245,0.2)") +
        kpi_card("Survivants", f"{survivors:,}",
                 f"sur {total:,} selectionnes", C["mint"], "💚", "rgba(78,203,160,0.2)") +
        kpi_card("Taux de survie", f"{rate:.1f}%",
                 f"{rate:.1f}% historique", C["coral"], "📈", "rgba(240,122,101,0.2)") +
        kpi_card("Age moyen", f"{avg_age} ans",
                 f"Tarif moy. £{avg_fare:.0f}", C["muted"], "🎂", "rgba(245,185,66,0.2)")
    )
    st.markdown(f'<div class="kpi-grid">{kpis_html}</div>', unsafe_allow_html=True)

    divider("PROFIL")
    col1, col2 = st.columns(2)
    with col1:
        section("Survie par sexe")
        grp = dff.groupby(["sex", "survived"]).size().reset_index(name="n")
        grp["Sexe"] = grp["sex"].map({"male": "Homme", "female": "Femme"})
        grp["Statut"] = grp["survived"].map({0: "Non survivant", 1: "Survivant"})
        fig = px.bar(grp, x="Sexe", y="n", color="Statut",
                     color_discrete_sequence=SURVIVED_COLORS,
                     barmode="group", template="plotly_white")
        fig.update_traces(marker_line_width=0, opacity=.9, marker_cornerradius=4)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col2:
        section("Repartition par classe")
        fig2 = px.pie(dff, names="pclass", color_discrete_sequence=CLASS_COLORS,
                      hole=.55, template="plotly_white", labels={"pclass": "Classe"})
        fig2.update_traces(
            textinfo="percent+label",
            marker=dict(line=dict(color="#fff", width=2)),
            pull=[.04, 0, 0],
        )
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    divider("EMBARQUEMENT & TARIFS")
    col3, col4 = st.columns(2)
    with col3:
        section("Port d'embarquement")
        port_df = dff["embark_town"].value_counts().reset_index()
        port_df.columns = ["Port", "Passagers"]
        fig3 = px.bar(port_df, x="Port", y="Passagers", color="Port",
                      color_discrete_sequence=[C["mint"], C["sky"], C["coral"]],
                      template="plotly_white")
        fig3.update_traces(marker_line_width=0, opacity=.9, marker_cornerradius=4)
        fig3.update_layout(showlegend=False)
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    with col4:
        section("Tarif moyen par classe (£)")
        fare_df = dff.groupby("pclass")["fare"].mean().reset_index()
        fare_df["Classe"] = fare_df["pclass"].map({1: "1ere", 2: "2eme", 3: "3eme"})
        fig4 = px.bar(fare_df, x="Classe", y="fare", color="Classe",
                      color_discrete_sequence=CLASS_COLORS,
                      text=fare_df["fare"].apply(lambda x: f"£{x:.0f}"),
                      template="plotly_white")
        fig4.update_traces(textposition="outside", marker_line_width=0,
                           opacity=.9, marker_cornerradius=4)
        fig4.update_layout(showlegend=False, yaxis_title="Tarif moyen (£)")
        st.plotly_chart(styled_fig(fig4), use_container_width=True)


def page_analyse_survie(df, dff):
    page_header("🏅", "Analyse de Survie", "Taux · distributions · correlations", "analyse_survie")

    section("Taux de survie par sexe")
    surv_sex = dff.groupby("sex")["survived"].mean().reset_index()
    surv_sex["taux"] = surv_sex["survived"] * 100
    surv_sex["label"] = surv_sex["sex"].map({"male": "Homme", "female": "Femme"})
    fig1 = px.bar(surv_sex, x="label", y="taux", color="label",
                  color_discrete_sequence=SEX_COLORS,
                  text=surv_sex["taux"].apply(lambda x: f"{x:.1f}%"),
                  template="plotly_white",
                  labels={"taux": "Taux (%)", "label": "Genre"})
    fig1.update_traces(textposition="outside", marker_line_width=0,
                       opacity=.9, marker_cornerradius=4)
    fig1.update_layout(showlegend=False, yaxis_range=[0, 115])
    st.plotly_chart(styled_fig(fig1), use_container_width=True)

    divider("PAR CLASSE ET AGE")
    col1, col2 = st.columns(2)
    with col1:
        section("Survie par classe")
        sc = dff.groupby("pclass")["survived"].mean().reset_index()
        sc["taux"] = sc["survived"] * 100
        sc["Classe"] = sc["pclass"].map({1: "1ere", 2: "2eme", 3: "3eme"})
        fig2 = px.pie(sc, names="Classe", values="taux",
                      color_discrete_sequence=CLASS_COLORS,
                      hole=.45, template="plotly_white")
        fig2.update_traces(
            textinfo="percent+label",
            marker=dict(line=dict(color="#fff", width=2)),
        )
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    with col2:
        section("Distribution des ages")
        fig3 = px.histogram(
            dff, x="age", color="survived", nbins=30,
            barmode="overlay", opacity=.75,
            color_discrete_sequence=SURVIVED_COLORS,
            template="plotly_white",
            labels={"age": "Age", "count": "Passagers", "survived": "Survie"},
        )
        fig3.update_layout(bargap=.02)
        st.plotly_chart(styled_fig(fig3), use_container_width=True)

    divider("HEATMAP")
    section("Taux de survie — Classe x Sexe")
    pivot = dff.groupby(["pclass", "sex"])["survived"].mean().unstack() * 100
    pivot.index = pivot.index.map({1: "1ere", 2: "2eme", 3: "3eme"})
    pivot.columns = pivot.columns.map({"male": "Homme", "female": "Femme"})
    fig4 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=pivot.columns.tolist(),
        y=pivot.index.tolist(),
        colorscale=[[0, C["coral"]], [0.5, C["amber"]], [1, C["mint"]]],
        text=[[f"{v:.1f}%" for v in row] for row in pivot.values],
        texttemplate="%{text}", showscale=True,
        colorbar=dict(title="% survie", tickfont=dict(color=C["text"])),
    ))
    fig4.update_layout(height=260)
    st.plotly_chart(styled_fig(fig4), use_container_width=True)

    divider("CORRELATION AGE · TARIF")
    section("Age vs Tarif — colore par survie")
    fig5 = px.scatter(
        dff, x="age", y="fare", color="survived",
        color_discrete_sequence=SURVIVED_COLORS, opacity=.6,
        template="plotly_white",
        labels={"age": "Age", "fare": "Tarif (£)", "survived": "Survie"},
        hover_data=["sex", "pclass"],
    )
    st.plotly_chart(styled_fig(fig5), use_container_width=True)


def page_filtres(df, dff, sel_cls, sel_sex, sel_ages):
    page_header("🎛️", "Filtres Interactifs", "Explorez la selection active", "filtres")
    log_event("filter_apply", {"classes": sel_cls, "sexes": sel_sex, "n_result": len(dff)})

    pct = len(dff) / len(df) * 100 if len(df) else 0
    cls_chips = "".join(
        f'<span class="filter-chip chip-sky">Classe {c}</span>' for c in sel_cls
    )
    sex_chips = "".join(
        '<span class="filter-chip chip-mint">'
        + ("Homme" if s == "male" else "Femme") + '</span>'
        for s in sel_sex
    )
    age_chips = "".join(
        f'<span class="filter-chip chip-coral">{a}</span>' for a in sel_ages
    )
    no_class = '<span style="color:#ccc;font-size:.72rem">Aucune classe</span>'
    no_sex = '<span style="color:#ccc;font-size:.72rem">Aucun genre</span>'
    no_age = '<span style="color:#ccc;font-size:.72rem">Aucun age</span>'

    st.markdown(f"""
    <div class="filter-summary">
      <div style="font-size:.6rem;font-weight:700;letter-spacing:.14em;
                  text-transform:uppercase;color:#8A9BB0;margin-bottom:.7rem">
        Filtres actifs
      </div>
      <div class="filter-row">{cls_chips or no_class}</div>
      <div class="filter-row">{sex_chips or no_sex}</div>
      <div class="filter-row" style="margin-bottom:.8rem">{age_chips or no_age}</div>
      <div style="border-top:1px solid #E1E8F0;padding-top:.7rem;
                  display:flex;align-items:baseline;gap:.4rem">
        <span class="filter-count">{len(dff)}</span>
        <span class="filter-pct">passagers selectionnes — {pct:.1f}% du total</span>
      </div>
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        section("Survie dans la selection")
        sc = dff["survived"].value_counts().reset_index()
        sc.columns = ["survived", "n"]
        sc["Statut"] = sc["survived"].map({0: "Non survivant", 1: "Survivant"})
        fig1 = px.bar(sc, x="Statut", y="n", color="Statut",
                      color_discrete_sequence=SURVIVED_COLORS,
                      text="n", template="plotly_white")
        fig1.update_traces(textposition="outside", marker_line_width=0,
                           opacity=.9, marker_cornerradius=4)
        fig1.update_layout(showlegend=False)
        st.plotly_chart(styled_fig(fig1), use_container_width=True)

    with col2:
        section("Repartition par tranche age")
        ag = dff["age_group"].value_counts().reset_index()
        ag.columns = ["Tranche", "n"]
        fig2 = px.bar(ag, x="Tranche", y="n", color="Tranche",
                      color_discrete_sequence=[
                          C["mint"], C["sky"], C["navy"], C["amber"], C["coral"]
                      ],
                      text="n", template="plotly_white")
        fig2.update_traces(textposition="outside", marker_line_width=0,
                           opacity=.9, marker_cornerradius=4)
        fig2.update_layout(showlegend=False)
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    divider("TARIFS")
    section("Tarif moyen par classe · selection active")
    fare = dff.groupby("pclass")["fare"].mean().reset_index()
    fare["Classe"] = fare["pclass"].map(
        {1: "1ere classe", 2: "2eme classe", 3: "3eme classe"}
    )
    fig3 = px.bar(fare, x="Classe", y="fare", color="Classe",
                  color_discrete_sequence=CLASS_COLORS,
                  text=fare["fare"].apply(lambda x: f"£{x:.2f}"),
                  template="plotly_white")
    fig3.update_traces(textposition="outside", marker_line_width=0,
                       opacity=.9, marker_cornerradius=4)
    fig3.update_layout(showlegend=False, yaxis_title="Tarif moyen (£)")
    st.plotly_chart(styled_fig(fig3), use_container_width=True)


def page_donnees(df, dff):
    n = len(dff)
    page_header("📋", "Donnees Brutes", f"{n} passagers filtres · export CSV", "donnees_brutes")

    all_cols = dff.columns.tolist()
    default = [
        c for c in [
            "survived", "pclass", "sex", "age", "fare", "embarked", "who", "age_group"
        ]
        if c in all_cols
    ]
    sel_cols = st.multiselect("Colonnes a afficher", options=all_cols, default=default)
    if not sel_cols:
        st.warning("Selectionnez au moins une colonne.")
        return

    display = dff[sel_cols].copy()
    page_size = st.slider("Lignes par page", 10, 100, 25, 5)
    total_pages = max(1, (len(display) - 1) // page_size + 1)
    page_num = st.number_input(f"Page (1 -> {total_pages})", 1, total_pages, 1)
    start = (page_num - 1) * page_size

    st.dataframe(display.iloc[start:start + page_size], use_container_width=True, height=420)

    csv = dff[sel_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Telecharger en CSV",
        data=csv,
        file_name=f"titanic_{len(dff)}_passagers.csv",
        mime="text/csv",
    )
    log_event("export_csv", {"rows": len(dff)})


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    df = get_data()
    cls, sex, ages = render_sidebar(df)
    dff = apply_filters(df, cls, sex, ages)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🌊  Vue Generale",
        "🏅  Analyse de Survie",
        "🎛️  Filtres Interactifs",
        "📋  Donnees Brutes",
    ])
    with tab1:
        page_vue_generale(df, dff)
    with tab2:
        page_analyse_survie(df, dff)
    with tab3:
        page_filtres(df, dff, cls, sex, ages)
    with tab4:
        page_donnees(df, dff)


if __name__ == "__main__":
    main()