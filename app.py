import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        return "Happy 😊", "#F9CB42"
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
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=False,
        margin=dict(t=20, b=20, l=20, r=20),
        height=300
    )
    return fig

st.title("Vibometer")
st.caption("Analyze the mood of any song")
df = load_data()

song_input = st.text_input("Enter a song name", placeholder="e.g. Blinding Lights, Talking to the moon")
st.caption("Can't find your song? Try searching by artist name or a keyword from the title.")

if song_input:
    results = df[df["track_name"].str.contains(song_input, case=False, na=False)]
    
    if results.empty:
        st.error("Song not found. Try a different spelling or another song.")
    else:
        # Drop duplicates by name + artist so same song doesn't appear twice
        results_clean = results.drop_duplicates(subset=["track_name", "artists"]).head(10)
        
        # Let user pick from results
        options = [
            f"{r['track_name']} — {r['artists']}" 
            for _, r in results_clean.iterrows()
        ]
        selected = st.selectbox("Select the song you meant:", options)
        
        # Get the selected song's row
        selected_index = options.index(selected)
        row = results_clean.iloc[selected_index]
        
        mood, color = classify_mood(row)
        
        st.markdown("---")
        
        col1, col2 = st.columns([1, 2])
        with col1:
            st.markdown(f"### {row['track_name']}")
            st.write(f"**Artist:** {row['artists']}")
            st.write(f"**Genre:** {row['track_genre']}")
            st.markdown(f"## {mood}")
        with col2:
            st.plotly_chart(make_radar(row), use_container_width=True)
        
        st.subheader("Audio features")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Valence", f"{row['valence']:.2f}")
        c2.metric("Energy", f"{row['energy']:.2f}")
        c3.metric("Tempo", f"{row['tempo']:.0f} BPM")
        c4.metric("Danceability", f"{row['danceability']:.2f}")
        
        st.markdown("---")
        
        # Similar songs
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
                st.write(f"**{s['track_name']}** — {s['artists']} ({s['track_genre']})")