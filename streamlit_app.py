import streamlit as st
import requests

# Set up page configuration
st.set_page_config(
    page_title="EcoPack-AI Recommender",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetics
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #4CAF50;
    }
    .rank-circle {
        display: inline-block;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        background-color: #4CAF50;
        color: white;
        text-align: center;
        line-height: 32px;
        font-weight: bold;
        margin-right: 10px;
        font-size: 16px;
    }
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
        st.error(f"API Connection Error. Is the FastAPI server running on {API_URL}? ({e})")
        return []

# Main UI
st.title("🌱 EcoPack-AI Packaging Recommender")
st.markdown("Discover the most **eco-friendly** and **cost-effective** packaging materials for your products using our trained AI models.")

with st.sidebar:
    st.header("📦 Product Specifications")
    weight_kg = st.number_input("Product Weight (kg)", min_value=0.1, value=2.5, step=0.1)
    volume_m3 = st.number_input("Product Volume (m³)", min_value=0.001, value=0.005, step=0.001, format="%.3f")
    
    st.header("🚚 Shipping Details")
    distance_km = st.number_input("Shipping Distance (km)", min_value=1.0, value=1500.0, step=10.0)
    shipping_mode = st.selectbox("Shipping Mode", ["Road", "Air", "Sea", "Rail"])
    
    st.header("⚙️ Preferences")
    optimization = st.selectbox("Optimization Focus", ["Balanced", "Eco", "Cost"], index=0)

    st.markdown("---")
    
    health = check_backend_health()
    if health and health.get("status") == "healthy":
        st.success(f"✅ Connected to FastAPI Backend.\nModel Version: {health.get('model_version', 'Unknown')}")
    else:
        st.error(f"❌ Cannot connect to API Backend at {API_URL}. Please run `uvicorn app:app`.")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("### Generate Options")
    st.markdown("Click below to fetch recommendations from the FastAPI backend.")
    analyze_btn = st.button("Generate Recommendations", type="primary", use_container_width=True)

with col2:
    if analyze_btn:
        with st.spinner("Fetching recommendations from the backend..."):
            recs = get_recommendations_from_api(weight_kg, volume_m3, distance_km, shipping_mode, optimization)
            
            if recs:
                st.success("Top 5 Recommendations Generated Successfully!")
                
                for rec in recs:
                    st.markdown(f"""
                    <div class="metric-card" style="margin-bottom: 1rem;">
                        <h3 style="margin-top: 0;"><span class="rank-circle">{rec['rank']}</span> {rec['material_name']}</h3>
                        <p style="color: #666; margin-bottom: 15px;"><b>Category:</b> {rec['category']} &nbsp;|&nbsp; <b>Biodegradable:</b> {"✅ Yes" if rec['biodegradable'] else "❌ No"}</p>
                        <div style="display: flex; gap: 40px;">
                            <div>
                                <p style="margin: 0; color: #888; font-size: 14px;">Est. CO₂ Emissions</p>
                                <h4 style="margin: 0; color: #E53935;">{rec['predicted_co2_kg']} kg</h4>
                            </div>
                            <div>
                                <p style="margin: 0; color: #888; font-size: 14px;">Est. Cost</p>
                                <h4 style="margin: 0; color: #43A047;">${rec['predicted_cost_usd']}</h4>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
            elif health is None:
                st.warning("Cannot generate recommendations. Backend server is unreachable.")
    else:
        st.info("Enter your product specifications in the sidebar and click Generate Recommendations.")
