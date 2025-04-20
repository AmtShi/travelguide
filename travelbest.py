import streamlit as st
import os
from groq import Groq
import folium
from streamlit_folium import folium_static
import tempfile
import json

# --- Set Page Config ---
st.set_page_config(
    page_title="Perfect Destination Finder",
    page_icon="🌍",
    layout="centered"
)

# --- Load API Key from Secrets ---
groq_api_key = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=groq_api_key)

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

# --- Recommendation Function ---
def get_perfect_destination(user_inputs):
    prompt = f"""
    You are an elite travel curator with 20+ years of experience. Suggest the best matching destination based on the following profile:
    - Traveler: {user_inputs['traveler_type']}
    - Duration: {user_inputs['duration']} days
    - Continent: {user_inputs['continent']}
    - Interests: {', '.join(user_inputs['interests'])}
    - Destination Type: {user_inputs['destination_type']}
    - Budget: {user_inputs['budget']}
    - Season: {user_inputs['season']}
    - Age Group: {user_inputs['age_group']}
    - Preferred Climate: {user_inputs['climate_preference']}

    Provide the best match, even if partial matches are found. Return ONLY this JSON structure:
    {{
        "destination": "City, Country",
        "match_score": "X/10 match score",
        "why_perfect": ["3 bullet points max"],
        "coordinates": [lat, lng],
        "itinerary_highlights": ["Day 1: Morning/Afternoon/Evening", "Day 2:..."],
        "local_secret": "One special insider tip",
        "warning": "Main safety concern to note"
    }}
    """
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are an elite travel curator. Be extremely selective."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error("⚠️ Sorry, we couldn't generate your perfect destination. Please review your selections and try again.")
        st.stop()

# --- Traveler Profile ---
def traveler_profile_section():
    with st.container(border=True):
        st.header("🧳 Traveler Profile")
        cols = st.columns([1,1,1])

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

        extra_cols = st.columns([1, 1])
        with extra_cols[0]:
            age_group = st.selectbox("Age group", ["18-25", "26-40", "41-60", "60+"])
        with extra_cols[1]:
            climate_preference = st.selectbox("Preferred Climate", ["Warm", "Cold", "Tropical", "Dry", "Any"])

    return {
        "traveler_type": traveler_type,
        "duration": duration,
        "budget": budget,
        "age_group": age_group,
        "climate_preference": climate_preference
    }

# --- Destination Preferences ---
def destination_preferences_section():
    with st.container(border=True):
        st.header("🌎 Destination Preferences")
        cols = st.columns([1,1])

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

# --- Save to JSON File ---
def save_recommendation_to_file(rec):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as tmp:
        json.dump(rec, tmp, indent=4)
        return tmp.name

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
            with st.container(border=True):
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

                json_path = save_recommendation_to_file(rec)
                with open(json_path, "rb") as jf:
                    st.download_button("💾 Save Recommendation as File", jf, file_name="travel_recommendation.json")

    st.markdown("""
    <div class="small-font" style="margin-top: 50px;">
        <hr>
        <p>🔎 <strong>Note:</strong> These destination suggestions are generated by an AI model based on patterns and probabilities from your inputs. They are not influenced by any particular country, region, or commercial interest. No personally identifiable information (PII) is collected or stored.</p>
        <p>⚠️ <strong>Disclaimer:</strong> This app is for informational and educational purposes only as part of a study project. It does not offer professional travel advice or services. The developer holds no liability for any travel-related outcomes from using this app.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
