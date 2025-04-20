import streamlit as st
import folium
from streamlit_folium import folium_static
from xhtml2pdf import pisa
import tempfile
import json

# --- Set Page Config ---
st.set_page_config(
    page_title="Perfect Destination Finder",
    page_icon="🌍",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
<style>
.small-font { font-size:14px !important; }
.travel-card {
    border-radius: 15px;
    padding: 20px;
    margin: 15px 0;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.warning-card {
    border-left: 5px solid #ff5252;
    background-color: #fff5f5;
    padding: 15px;
    border-radius: 8px;
}
</style>
""", unsafe_allow_html=True)

# --- Mock Groq API (Replace this with real API in production) ---
class MockGroqClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def chat(self, prompt):
        # Mock response for testing, replace this with actual call to Groq API
        return {
            "destination": "Paris, France",
            "match_score": "9/10",
            "why_perfect": ["Rich in history", "Romantic atmosphere", "Great food and culture"],
            "coordinates": [48.8566, 2.3522],
            "itinerary_highlights": ["Day 1: Visit the Eiffel Tower", "Day 2: Explore Louvre Museum"],
            "local_secret": "Visit the hidden garden behind Notre-Dame",
            "warning": "Pickpockets are common in tourist areas."
        }

# --- Recommendation Function ---
def get_perfect_destination(user_inputs):
    try:
        # Replace the MockGroqClient with actual Groq client in production
        groq_api_key = st.secrets["groq_api_key"]
        client = MockGroqClient(api_key=groq_api_key)  # Use Mock client here for testing
        response = client.chat(prompt="Generate travel recommendation based on user inputs")
        return response
    except Exception as e:
        st.error(f"⚠️ Error generating destination. {e}")
        return None

# --- Traveler Profile Section ---
def traveler_profile_section():
    with st.container():
        st.header("🧳 Traveler Profile")
        cols = st.columns([1, 1, 1])

        with cols[0]:
            traveler_type = st.radio(
                "Who's traveling?",
                ["Solo", "Couple", "Family", "Business", "Friends Group"],
                index=0
            )

        with cols[1]:
            duration = st.slider(
                "Trip duration (days)",
                min_value=1, max_value=21, value=7
            )

        with cols[2]:
            budget = st.select_slider(
                "Budget level",
                ["💰 Budget", "💵 Comfort", "💎 Luxury"],
                value="💵 Comfort"
            )

    return {
        "traveler_type": traveler_type,
        "duration": duration,
        "budget": budget
    }

# --- Destination Preferences Section ---
def destination_preferences_section():
    with st.container():
        st.header("🌎 Destination Preferences")
        cols = st.columns([1, 1])

        with cols[0]:
            continent = st.selectbox(
                "Preferred continent",
                ["Any", "Europe", "Asia", "Africa", "Americas", "Oceania"]
            )
            season = st.selectbox(
                "Travel season",
                ["Summer", "Winter", "Spring", "Fall", "Any"]
            )

        with cols[1]:
            destination_type = st.selectbox(
                "Landscape type",
                [
                    "Mountains", "Beaches", "Deserts", "Forests", "Islands",
                    "Lakes & Rivers", "Volcanoes", "Tundra", "Countryside",
                    "Canyons", "Cliffs", "Sand Dunes", "Waterfalls"
                ]
            )
            interests = st.multiselect(
                "Your interests",
                [
                    "History", "Food & Street Eats", "Nature Trails", "Art & Museums",
                    "Shopping", "Nightlife & Clubs", "Photography", "Adventure Sports",
                    "Local Culture", "Relaxation", "Festivals & Events", "Spiritual Retreats",
                    "Tech & Innovation", "Sustainable Travel", "Music & Concerts", "Gaming Cafes",
                    "Wellness & Spas", "Social Media Hotspots", "Extreme Sports", "Eco-Lodging",
                    "Unique Stays (e.g., Treehouses)", "Road Trips", "Digital Detox"
                ],
                default=["Food & Street Eats", "Local Culture"]
            )

    return {
        "continent": continent,
        "season": season,
        "destination_type": destination_type,
        "interests": interests
    }

# --- Create PDF ---
def create_pdf(recommendation):
    html = f"""
    <h1>{recommendation['destination']}</h1>
    <p><strong>Match Score:</strong> {recommendation['match_score']}</p>
    <h2>Why It's Perfect:</h2>
    <ul>{''.join(f'<li>{pt.strip()}</li>' for pt in recommendation['why_perfect'])}</ul>
    <h2>Itinerary Highlights:</h2>
    <ul>{''.join(f'<li>{item}</li>' for item in recommendation['itinerary_highlights'])}</ul>
    <p><strong>Insider Tip:</strong> {recommendation['local_secret']}</p>
    <p><strong>Warning:</strong> {recommendation['warning']}</p>
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf_path = tmp_file.name
        with open(pdf_path, "w+b") as pdf:
            pisa.CreatePDF(html, dest=pdf)
    return pdf_path

# --- Main ---
def main():
    st.title("✈️ Perfect Destination Finder")
    st.caption("Discover your ideal travel spot in seconds")

    profile = traveler_profile_section()
    prefs = destination_preferences_section()
    user_inputs = {**profile, **prefs}

    if st.button("✨ Find My Perfect Destination", type="primary", use_container_width=True):
        with st.spinner("Analyzing 1,000+ destinations..."):
            rec = get_perfect_destination(user_inputs)

        if rec:
            st.success(f"## 🏆 Your Perfect Match: {rec['destination']}")
            st.markdown(f"**{rec['match_score']} match** | {user_inputs['duration']} day trip")

            m = folium.Map(location=rec["coordinates"], zoom_start=12)
            folium.Marker(
                rec["coordinates"],
                tooltip=f"Explore {rec['destination']}",
                icon=folium.Icon(color="red", icon="heart")
            ).add_to(m)
            folium_static(m, height=300)

            st.markdown("### ❤️ Why This Fits You")
            for point in rec["why_perfect"]:
                st.markdown(f"- {point.strip()}")

            st.markdown("### 📅 Sample Itinerary")
            for day in rec["itinerary_highlights"]:
                st.markdown(f"- {day}")

            with st.expander("🔍 Local Insider Secret"):
                st.markdown(f"*{rec['local_secret']}*")

            st.markdown("### ⚠️ Heads Up")
            st.warning(rec["warning"])

            pdf_path = create_pdf(rec)
            with open(pdf_path, "rb") as f:
                st.download_button("📄 Download Itinerary as PDF", f, file_name="travel_plan.pdf")

if __name__ == "__main__":
    main()
