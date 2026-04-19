import streamlit as st
import pandas as pd
import requests
import pickle

# ------------------ STYLE ------------------
st.markdown("""
<style>
body {
    background-color: #0e1117;
}

h1 {
    color: #E50914;
    text-align: center;
}

.movie-card {
    background-color: #1c1f26;
    padding: 10px;
    border-radius: 12px;
    text-align: center;
    transition: 0.3s;
}

.movie-card:hover {
    transform: scale(1.05);
}

.banner {
    background-color: #1c1f26;
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Load data
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

movies = pd.read_csv("movies.csv")

# simple example (adjust based on your project)
movies['tags'] = movies['overview'].fillna('')

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['tags'])

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
#8c456926fa1178ea06085085e59ba0f2
# Recommendation function
def get_recommendations(title):
    idx = movies[movies['title'] == title].index[0]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Take more movies (so we can filter later)
    sim_scores = sim_scores[1:20]

    movie_indices = [i[0] for i in sim_scores]
    return movies.iloc[movie_indices]

# Fetch poster using TITLE (better accuracy)
def fetch_movie_data(movie_title):
    try:
        api_key = '8c456926fa1178ea06085085e59ba0f2'  # 👈 your key

        url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
        
        response = requests.get(url, timeout=5)
        data = response.json()

        if data['results']:
            movie = data['results'][0]

            poster_path = movie.get('poster_path')
            rating = movie.get('vote_average')
            overview = movie.get('overview')

            poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

            return poster_url, rating, overview

        return None, None, None

    except:
        return None, None, None
    
def fetch_trailer(movie_title):
    try:
        api_key = '8c456926fa1178ea06085085e59ba0f2'

        # Step 1: Search movie
        search_url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}"
        search_data = requests.get(search_url).json()

        if not search_data['results']:
            return None

        movie_id = search_data['results'][0]['id']

        # Step 2: Get videos
        video_url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={api_key}"
        video_data = requests.get(video_url).json()

        for video in video_data['results']:
            if video['type'] == 'Trailer' and video['site'] == 'YouTube':
                return f"https://www.youtube.com/watch?v={video['key']}"

        return None

    except:
        return None 

# UI
st.set_page_config(page_title="Movie Recommender", layout="wide")

st.title("🎬 Movie Recommendation System")

selected_movie = st.selectbox(
    "Select a movie:",
    movies['title'].values  )

# 🎬 Banner
poster, rating, overview = fetch_movie_data(selected_movie)

if poster:
    st.markdown(f"""
    <div class="banner">
        <h2>{selected_movie}</h2>
        <p>⭐ Rating: {rating}</p>
        <p>{overview}</p>
    </div>
    """, unsafe_allow_html=True)

# Button
if st.button('Recommend'):

    # ✅ create recommendations FIRST
    recommendations = get_recommendations(selected_movie)

    valid_movies = []

    # ✅ now safe to use
    for i in range(len(recommendations)):
        movie_title = recommendations.iloc[i]['title']
        poster, rating, overview = fetch_movie_data(movie_title)

        if poster:
            valid_movies.append((movie_title, poster, rating, overview))

        if len(valid_movies) == 10:
            break

    # ✅ display
    st.subheader("🔥 Top Recommendations")

    if len(valid_movies) == 0:
        st.write("No movies found ❌")
    else:
       for i in range(0, len(valid_movies), 5):
         row_movies = valid_movies[i:i+5]
         cols = st.columns(len(row_movies))

         for col, item in zip(cols, row_movies):
           title, poster, rating, overview = item

           with col:
              # ✅ define trailer INSIDE block
               trailer = fetch_trailer(title)

               st.markdown(f"""
               <div class="movie-card">
                   <img src="{poster}" width="100%">
                   <h4>{title}</h4>
                   <p>⭐ {rating}</p>
                   <p style="font-size:12px;">{overview[:80]}...</p>
               </div>
               """, unsafe_allow_html=True)

            # ✅ use trailer here (same scope)
               if trailer:
                   st.markdown(f"[▶ Watch Trailer]({trailer})")
