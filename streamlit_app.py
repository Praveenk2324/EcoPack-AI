import streamlit as st
import requests

st.set_page_config(
    page_title="EcoPack-AI · Sustainable Packaging",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

/* ── Reset & base ─────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', system-ui, sans-serif;
}

.stApp {
    background-color: #F5F0E8;
}

/* ── Sidebar ──────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: #1A2E1A !important;
    border-right: none;
}

[data-testid="stSidebar"] * {
    color: #E8EFE0 !important;
}

[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stNumberInput label {
    color: #7BA05B !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase;
}

[data-testid="stSidebar"] .stSelectbox > div > div,
[data-testid="stSidebar"] .stNumberInput > div > div > input {
    background: #243824 !important;
    border: 1px solid #3a5c3a !important;
    border-radius: 8px !important;
    color: #F5F0E8 !important;
}

[data-testid="stSidebar"] hr {
    border-color: #3a5c3a !important;
    margin: 20px 0 !important;
}

/* Sidebar section headers */
.sidebar-section {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #7BA05B;
    margin: 24px 0 10px 0;
    padding-bottom: 6px;
    border-bottom: 1px solid #3a5c3a;
}

/* ── Hero header ──────────────────────────────────── */
.hero {
    background: linear-gradient(135deg, #1A2E1A 0%, #243824 60%, #2d4a2d 100%);
    border-radius: 16px;
    padding: 40px 48px 36px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}

.hero::before {
    content: '🌿';
    font-size: 160px;
    position: absolute;
    right: -10px;
    top: -30px;
    opacity: 0.08;
    transform: rotate(-15deg);
}

.hero-eyebrow {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #7BA05B;
    margin-bottom: 10px;
}

.hero-title {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 2.6rem;
    color: #F5F0E8;
    line-height: 1.15;
    margin: 0 0 12px 0;
    font-weight: 400;
}

.hero-title em {
    color: #7BA05B;
    font-style: italic;
}

.hero-sub {
    font-size: 0.95rem;
    color: #a8c49a;
    max-width: 560px;
    line-height: 1.65;
    margin: 0;
    font-weight: 300;
}

/* ── Status pill ──────────────────────────────────── */
.status-pill {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    padding: 6px 14px;
    border-radius: 99px;
    margin-top: 20px;
}

.status-ok {
    background: rgba(123, 160, 91, 0.18);
    color: #7BA05B;
    border: 1px solid rgba(123, 160, 91, 0.35);
}

.status-err {
    background: rgba(200, 92, 74, 0.12);
    color: #C85C4A;
    border: 1px solid rgba(200, 92, 74, 0.3);
}

/* ── Input panel ──────────────────────────────────── */
.input-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}

.input-tile {
    background: white;
    border: 1px solid #e2ddd4;
    border-radius: 12px;
    padding: 18px 20px;
}

.input-tile-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #7BA05B;
    margin-bottom: 4px;
}

.input-tile-value {
    font-size: 1.6rem;
    font-weight: 600;
    color: #1A2E1A;
    line-height: 1;
}

.input-tile-unit {
    font-size: 0.75rem;
    color: #999;
    font-weight: 400;
    margin-left: 4px;
}

/* ── Generate button ──────────────────────────────── */
.stButton > button {
    background: linear-gradient(135deg, #7BA05B, #5d8042) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    letter-spacing: 0.04em !important;
    padding: 14px 28px !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 14px rgba(123,160,91,0.3) !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(123,160,91,0.4) !important;
}

/* ── Results section ──────────────────────────────── */
.results-header {
    font-family: 'DM Serif Display', Georgia, serif;
    font-size: 1.5rem;
    color: #1A2E1A;
    margin: 28px 0 18px;
    font-weight: 400;
}

/* ── Recommendation card ──────────────────────────── */
.rec-card {
    background: white;
    border-radius: 14px;
    padding: 24px 28px;
    margin-bottom: 14px;
    border: 1px solid #e8e3da;
    box-shadow: 0 2px 8px rgba(26,46,26,0.04);
    position: relative;
    overflow: hidden;
    transition: box-shadow 0.2s;
}

.rec-card:hover {
    box-shadow: 0 6px 24px rgba(26,46,26,0.1);
}

.rec-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #7BA05B, #D4A843);
    border-radius: 4px 0 0 4px;
}

.rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 50%;
    font-size: 0.75rem;
    font-weight: 700;
    margin-right: 10px;
    flex-shrink: 0;
}

.rank-1 { background: #D4A843; color: white; }
.rank-2 { background: #9baab0; color: white; }
.rank-3 { background: #b08060; color: white; }
.rank-other { background: #E8EFE0; color: #1A2E1A; }

.mat-name {
    font-size: 1.05rem;
    font-weight: 600;
    color: #1A2E1A;
    display: inline;
}

.category-tag {
    display: inline-block;
    background: #E8EFE0;
    color: #4a7040;
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 99px;
    margin-left: 10px;
    vertical-align: middle;
}

.bio-tag {
    display: inline-block;
    background: rgba(123,160,91,0.12);
    color: #5d8042;
    border: 1px solid rgba(123,160,91,0.3);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 99px;
    margin-left: 6px;
    vertical-align: middle;
}

.no-bio-tag {
    background: rgba(200,92,74,0.08);
    color: #a84030;
    border: 1px solid rgba(200,92,74,0.2);
}

.metrics-row {
    display: flex;
    gap: 48px;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #f0ebe0;
    align-items: flex-end;
}

.metric-block { flex: 1; }

.metric-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #999;
    margin-bottom: 4px;
}

.metric-val {
    font-size: 1.4rem;
    font-weight: 700;
    line-height: 1;
}

.co2-val { color: #C85C4A; }
.cost-val { color: #5d8042; }

.score-bar-wrap {
    flex: 2;
}

.score-bar-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #bbb;
    margin-bottom: 6px;
    display: flex;
    justify-content: space-between;
}

.score-bar-track {
    height: 6px;
    background: #F0EBE0;
    border-radius: 99px;
    overflow: hidden;
}

.score-bar-fill {
    height: 100%;
    border-radius: 99px;
    background: linear-gradient(90deg, #7BA05B, #D4A843);
    transition: width 0.8s cubic-bezier(0.4,0,0.2,1);
}

/* ── Empty state ──────────────────────────────────── */
.empty-state {
    background: white;
    border: 2px dashed #d8d3ca;
    border-radius: 14px;
    padding: 60px 40px;
    text-align: center;
    color: #aaa;
}

.empty-icon { font-size: 3rem; margin-bottom: 12px; }
.empty-text { font-size: 0.95rem; color: #bbb; font-weight: 400; }

/* ── Streamlit overrides ──────────────────────────── */
.stSpinner > div { border-top-color: #7BA05B !important; }

[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] > div:first-child hr {
    border-color: #e2ddd4;
}

div[data-testid="column"] { gap: 0 !important; }
</style>
""", unsafe_allow_html=True)

API_URL = "http://localhost:8000"


def check_backend_health():
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            return response.json()
    except requests.exceptions.RequestException:
        pass
    return None


def get_recommendations_from_api(weight_kg, volume_m3, distance_km, shipping_mode, optimization):
    payload = {
        "weight_kg": weight_kg,
        "volume_m3": volume_m3,
        "distance_km": distance_km,
        "shipping_mode": shipping_mode,
        "optimization": optimization.lower()
    }
    try:
        response = requests.post(f"{API_URL}/recommend", json=payload)
        response.raise_for_status()
        return response.json().get("recommendations", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Cannot reach backend at {API_URL}. Make sure `uvicorn app:app` is running. ({e})")
        return []


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-section">Product</div>', unsafe_allow_html=True)
    weight_kg  = st.number_input("Weight (kg)",  min_value=0.1,   value=2.5,    step=0.1)
    volume_m3  = st.number_input("Volume (m³)",  min_value=0.001, value=0.005,  step=0.001, format="%.3f")

    st.markdown('<div class="sidebar-section">Shipping</div>', unsafe_allow_html=True)
    distance_km   = st.number_input("Distance (km)", min_value=1.0, value=1500.0, step=10.0)
    shipping_mode = st.selectbox("Mode", ["Road", "Air", "Sea", "Rail"])

    st.markdown('<div class="sidebar-section">Optimise for</div>', unsafe_allow_html=True)
    optimization = st.selectbox("Focus", ["Balanced", "Eco", "Cost"], index=0)

    st.markdown("---")
    health = check_backend_health()
    if health and health.get("status") == "healthy":
        st.markdown(
            f'<span class="status-pill status-ok">● API connected · v{health.get("model_version","—")}</span>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<span class="status-pill status-err">● API unreachable</span>',
            unsafe_allow_html=True
        )


# ── Hero ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-eyebrow">AI-Powered Sustainability</div>
  <div class="hero-title">Packaging that's<br><em>good for the planet</em> too.</div>
  <p class="hero-sub">Enter your product specs and let the model surface the most eco-friendly, cost-conscious packaging options — ranked and explained.</p>
</div>
""", unsafe_allow_html=True)


# ── Current parameters summary ─────────────────────────────────────────────
mode_icons = {"Road": "🚛", "Air": "✈️", "Sea": "🚢", "Rail": "🚂"}
opt_icons  = {"Balanced": "⚖️", "Eco": "🌿", "Cost": "💰"}

st.markdown(f"""
<div class="input-grid">
  <div class="input-tile">
    <div class="input-tile-label">Weight</div>
    <div class="input-tile-value">{weight_kg}<span class="input-tile-unit">kg</span></div>
  </div>
  <div class="input-tile">
    <div class="input-tile-label">Volume</div>
    <div class="input-tile-value">{volume_m3:.3f}<span class="input-tile-unit">m³</span></div>
  </div>
  <div class="input-tile">
    <div class="input-tile-label">Distance</div>
    <div class="input-tile-value">{int(distance_km):,}<span class="input-tile-unit">km</span></div>
  </div>
  <div class="input-tile">
    <div class="input-tile-label">Mode</div>
    <div class="input-tile-value" style="font-size:1.2rem;">{mode_icons.get(shipping_mode,'')} {shipping_mode}</div>
  </div>
  <div class="input-tile">
    <div class="input-tile-label">Optimise for</div>
    <div class="input-tile-value" style="font-size:1.2rem;">{opt_icons.get(optimization,'')} {optimization}</div>
  </div>
  <div class="input-tile" style="display:flex;align-items:center;justify-content:center;">
  </div>
</div>
""", unsafe_allow_html=True)

analyze_btn = st.button("🌿  Rank packaging options", type="primary")


# ── Results ────────────────────────────────────────────────────────────────
if analyze_btn:
    with st.spinner("Scoring materials…"):
        recs = get_recommendations_from_api(weight_kg, volume_m3, distance_km, shipping_mode, optimization)

    if recs:
        st.markdown('<div class="results-header">Top recommendations</div>', unsafe_allow_html=True)

        # Normalise for score bar (lower CO2 = better)
        co2_vals = [r["predicted_co2_kg"] for r in recs]
        co2_max  = max(co2_vals) if co2_vals else 1

        for rec in recs:
            rank   = rec["rank"]
            rclass = f"rank-{rank}" if rank <= 3 else "rank-other"
            bio_cls = "bio-tag" if rec["biodegradable"] else "bio-tag no-bio-tag"
            bio_txt = "Biodegradable" if rec["biodegradable"] else "Not biodegradable"

            # Eco score bar: invert CO2 so rank-1 fills more
            eco_pct  = max(5, round((1 - rec["predicted_co2_kg"] / co2_max) * 100))

            st.markdown(f"""
            <div class="rec-card">
              <div style="display:flex;align-items:center;flex-wrap:wrap;gap:4px;">
                <span class="rank-badge {rclass}">{rank}</span>
                <span class="mat-name">{rec['material_name']}</span>
                <span class="category-tag">{rec['category']}</span>
                <span class="{bio_cls}">{bio_txt}</span>
              </div>
              <div class="metrics-row">
                <div class="metric-block">
                  <div class="metric-label">CO₂ Emissions</div>
                  <div class="metric-val co2-val">{rec['predicted_co2_kg']} <span style="font-size:0.75rem;font-weight:400;color:#aaa">kg</span></div>
                </div>
                <div class="metric-block">
                  <div class="metric-label">Estimated Cost</div>
                  <div class="metric-val cost-val">${rec['predicted_cost_usd']}</div>
                </div>
                <div class="score-bar-wrap">
                  <div class="score-bar-label">
                    <span>Eco score</span>
                    <span>{eco_pct}%</span>
                  </div>
                  <div class="score-bar-track">
                    <div class="score-bar-fill" style="width:{eco_pct}%"></div>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        if health is None:
            st.markdown("""
            <div class="empty-state">
              <div class="empty-icon">🔌</div>
              <div class="empty-text">Backend unreachable — run <code>uvicorn app:app</code> and refresh.</div>
            </div>
            """, unsafe_allow_html=True)

else:
    st.markdown("""
    <div class="empty-state">
      <div class="empty-icon">🌿</div>
      <div class="empty-text">Adjust your specs in the sidebar, then click <strong>Rank packaging options</strong>.</div>
    </div>
    """, unsafe_allow_html=True)