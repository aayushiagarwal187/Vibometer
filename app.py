import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Vibometer", page_icon="🎵", layout="centered")

st.markdown("""
<style>
.stApp { background-color: #0e0e14; }
.stTextInput input { background-color: #1a1a2e !important; border: 0.5px solid #534AB7 !important; color: #EEEDFE !important; border-radius: 10px !important; }
div[data-baseweb="select"] { background-color: #1a1a2e !important; border: 0.5px solid #534AB7 !important; border-radius: 10px !important; }
div[data-testid="metric-container"] { background-color: #1a1a2e; border-radius: 10px; padding: 12px; border: 0.5px solid #3C3489; }
div[data-testid="metric-container"] label { color: #534AB7 !important; font-size: 11px !important; }
div[data-testid="stMetricValue"] { color: #AFA9EC !important; }
h1 { color: #AFA9EC !important; }
h2, h3 { color: #AFA9EC !important; }
p, label { color: #CECBF6 !important; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/aayushiagarwal187/Vibometer/main/dataset.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.lower()
    return df

def classify_mood(row):
    valence = row["valence"]
    energy = row["energy"]
    tempo = row["tempo"]
    if valence > 0.6 and energy > 0.5:
        return "Happy 😊", "#97C459"
    elif valence < 0.4 and energy < 0.5:
        return "Melancholic 😔", "#85B7EB"
    elif energy > 0.8 and tempo > 130:
        return "Hype 🔥", "#F0997B"
    elif energy < 0.4 and valence > 0.4:
        return "Chill 😌", "#5DCAA5"
    elif energy > 0.7 and valence < 0.4:
        return "Angry / Intense 😤", "#ED93B1"
    else:
        return "Neutral 😐", "#B4B2A9"

def make_radar(row):
    categories = ["Valence", "Energy", "Danceability", "Acousticness", "Instrumentalness"]
    values = [row[c.lower()] for c in categories]
    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        line_color="#7F77DD"
    ))
    fig.update_layout(
        polar=dict(
            bgcolor="#1a1a2e",
            radialaxis=dict(visible=True, range=[0, 1], color="#534AB7"),
            angularaxis=dict(color="#534AB7")
        ),
        paper_bgcolor="#0e0e14",
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=300
    )
    return fig

mood_styles = {
    "Happy 😊":           ("border: 0.5px solid #639922; background: #1a2a1a;", "#97C459"),
    "Melancholic 😔":     ("border: 0.5px solid #185FA5; background: #0a101f;", "#85B7EB"),
    "Hype 🔥":            ("border: 0.5px solid #993C1D; background: #2a1a0a;", "#F0997B"),
    "Chill 😌":           ("border: 0.5px solid #0F6E56; background: #0a1f1f;", "#5DCAA5"),
    "Angry / Intense 😤": ("border: 0.5px solid #993556; background: #1f0a14;", "#ED93B1"),
    "Neutral 😐":         ("border: 0.5px solid #5F5E5A; background: #1a1a1a;", "#B4B2A9"),
}

mood_descriptions = {
    "Happy 😊":           "Bright and uplifting — put this on repeat",
    "Melancholic 😔":     "Soft and emotional — for those quiet moments",
    "Hype 🔥":            "High energy, fast tempo — made for the main stage",
    "Chill 😌":           "Laid back and easy — perfect background music",
    "Angry / Intense 😤": "Raw and intense — feels like a final boss track",
    "Neutral 😐":         "Balanced vibes — fits almost any mood",
}

# --- UI ---
st.title("Vibometer 🎵")
st.caption("Analyze the mood of any song")

df = load_data()

song_input = st.text_input("Enter a song name", placeholder="e.g. Blinding Lights, Levitating")
st.caption("Can't find your song? Try searching by artist name or a keyword from the title.")

if song_input:
    results = df[df["track_name"].str.contains(song_input, case=False, na=False)]

    if results.empty:
        st.error("Song not found. Try a different spelling or another song.")
    else:
        results_clean = results.drop_duplicates(subset=["track_name", "artists"]).head(10)
        options = [f"{r['track_name']} — {r['artists']}" for _, r in results_clean.iterrows()]
        selected = st.selectbox("Select the song you meant:", options)
        selected_index = options.index(selected)
        row = results_clean.iloc[selected_index]

        mood, color = classify_mood(row)
        card_style, text_color = mood_styles.get(mood, mood_styles["Neutral 😐"])
        desc = mood_descriptions.get(mood, "")

        st.markdown("---")

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"### {row['track_name']}")
            st.write(f"**Artist:** {row['artists']}")
            st.write(f"**Genre:** {row['track_genre']}")
            st.markdown(f"""
<div style="border-radius: 12px; padding: 1.25rem 1.5rem; margin: 1rem 0; {card_style}">
    <div style="font-size: 22px; font-weight: 500; color: {text_color};">{mood}</div>
    <div style="font-size: 13px; color: {text_color}; opacity: 0.7; margin-top: 4px;">{desc}</div>
</div>
""", unsafe_allow_html=True)

        with col2:
            st.plotly_chart(make_radar(row), use_container_width=True)

        st.subheader("Audio features")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Valence", f"{row['valence']:.2f}")
        c2.metric("Energy", f"{row['energy']:.2f}")
        c3.metric("Tempo", f"{row['tempo']:.0f} BPM")
        c4.metric("Danceability", f"{row['danceability']:.2f}")

        st.markdown("---")

        st.subheader("Songs with a similar vibe")
        similar = df[
            (df["track_genre"] == row["track_genre"]) &
            (abs(df["valence"] - row["valence"]) < 0.15) &
            (abs(df["energy"] - row["energy"]) < 0.15) &
            (df["track_name"] != row["track_name"])
        ].drop_duplicates(subset=["track_name", "artists"]).head(5)

        if similar.empty:
            st.write("No similar songs found in this genre.")
        else:
            for _, s in similar.iterrows():
                st.markdown(f"""
<div style="background: #1a1a2e; border-radius: 8px; padding: 10px 14px; margin-bottom: 6px; display: flex; justify-content: space-between;">
    <div>
        <div style="font-size: 14px; color: #CECBF6;">{s['track_name']}</div>
        <div style="font-size: 12px; color: #534AB7;">{s['artists']}</div>
    </div>
    <div style="font-size: 11px; color: #AFA9EC; background: #26215C; padding: 2px 10px; border-radius: 20px; height: fit-content;">{s['track_genre']}</div>
</div>
""", unsafe_allow_html=True)