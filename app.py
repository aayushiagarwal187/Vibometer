import streamlit as st
import pandas as pd
import plotly.graph_objects as go

@st.cache_data
def load_data():
    df = pd.read_csv("dataset.csv")
    df.columns = df.columns.str.strip().str.lower()
    return df

def classify_mood(row):
    valence = row["valence"]
    energy = row["energy"]
    tempo = row["tempo"]
    if valence > 0.6 and energy > 0.5:
        return "Happy"
    elif valence < 0.4 and energy < 0.5:
        return "Melancholic"
    elif energy > 0.8 and tempo > 130:
        return "Hype"
    elif energy < 0.4 and valence > 0.4:
        return "Chill"
    elif energy > 0.7 and valence < 0.4:
        return "Angry / intense"
    else:
        return "Neutral"

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
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=300
    )
    return fig

st.title("Music mood analyzer")
st.caption("Powered by Spotify audio features")

df = load_data()

song_input = st.text_input("Enter a song name", placeholder="e.g. Style")

if song_input:
    results = df[df["track_name"].str.contains(song_input, case=False, na=False)]
    if results.empty:
        st.error("Song not found. Try a different name.")
    else:
        row = results.iloc[0]
        mood = classify_mood(row)

        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"### {row['track_name']}")
            st.write(row["artists"])
            st.write(row["track_genre"])
        with col2:
            st.markdown(f"### Mood: {mood}")
            st.plotly_chart(make_radar(row), use_container_width=True)

        st.subheader("Audio features breakdown")
        c1, c2, c3 = st.columns(3)
        c1.metric("Valence", f"{row['valence']:.2f}")
        c2.metric("Energy", f"{row['energy']:.2f}")
        c3.metric("Tempo", f"{row['tempo']:.0f} BPM")

        st.subheader("Other matches")
        st.dataframe(results[["track_name", "artists", "track_genre"]].head(5))