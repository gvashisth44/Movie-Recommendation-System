
from flask import Blueprint, render_template, request
import pickle
import pandas as pd
import requests
from models import get_last_search, set_last_search
from database import init_db
from datetime import datetime
from flask import Flask

app = Flask(__name__)


API_KEY = "690ec379879b06618fc1a6e008838ec4&language=en-US"

# main = Blueprint('main', __name__)

init_db()

with open('movies.pkl', 'rb') as file:
    movies_list = pickle.load(file)

with open('similarity.pkl', 'rb') as file:
    similarity = pickle.load(file)

movies_list = pd.DataFrame(movies_list)

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    data = requests.get(url).json()
    return f"https://image.tmdb.org/t/p/w500/{data['poster_path']}"

def recommend(movie):
    movie = movie.lower()
    movie_index = movies_list[movies_list['title'].str.lower() == movie].index[0]
    distances = similarity[movie_index]
    sorted_movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

    recommended_movies_lst = []
    recommended_movies_posters = []
    for i in sorted_movies_list:
        movie_id = movies_list.iloc[i[0]].movie_id
        recommended_movies_lst.append(movies_list.iloc[i[0]].title)
        recommended_movies_posters.append(movie_id)  # Just storing movie_id for now
    return recommended_movies_lst, recommended_movies_posters

def fetch_posters(movie_ids):
    return [fetch_poster(movie_id) for movie_id in movie_ids]

def fetch_movie_details(movie_id):
    movie_url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"
    return requests.get(movie_url).json()

def fetch_cast_member_details(cast_id):
    url = f'https://api.themoviedb.org/3/person/{cast_id}?api_key={API_KEY}'
    response = requests.get(url)
    return response.json()

def process_movie_selection(movie):
    movie_index = movies_list[movies_list['title'].str.lower() == movie.lower()].index[0]
    selected_movie_id = movies_list.iloc[movie_index].movie_id
    selected_movie_details = fetch_movie_details(selected_movie_id)
    recommended_movies, movie_ids = recommend(movie)
    if recommended_movies:
        posters = fetch_posters(movie_ids)
    else:
        posters = []

    # Fetch cast details for the selected movie
    credits_url = f'https://api.themoviedb.org/3/movie/{selected_movie_id}/credits?api_key={API_KEY}'
    credits_response = requests.get(credits_url).json()
    cast = credits_response.get('cast', [])

    return selected_movie_details, recommended_movies, posters, cast

@app.route('/', methods=['GET', 'POST'])
def home():
    current_year = datetime.now().year
    recommended_movies = []
    posters = []
    selected_movie_details = None
    selected_movie = None
    cast = []

    if request.method == 'POST':
        selected_movie = request.form['movie']
        if selected_movie:
            set_last_search(selected_movie)
            try:
                selected_movie_details, recommended_movies, posters, cast = process_movie_selection(selected_movie)
            except IndexError:
                return render_template('home.html', movies=movies_list['title'].values, recommended_movies=[], selected_movie_details=None, error_message="Movie not found")
        else:
            return render_template('home.html', movies=movies_list['title'].values, recommended_movies=[], selected_movie_details=None, error_message="Please enter a movie name")
    else:
        last_searched_movie = get_last_search()
        if last_searched_movie:
            try:
                selected_movie_details, recommended_movies, posters, cast = process_movie_selection(last_searched_movie)
            except IndexError:
                pass

    recommended_movies_links = [(movie, poster, movies_list[movies_list['title'] == movie].iloc[0].movie_id) for movie, poster in zip(recommended_movies, posters)]
    return render_template('home.html', movies=movies_list['title'].values, recommended_movies=recommended_movies_links, selected_movie_details=selected_movie_details, selected_movie=selected_movie, cast=cast,current_year=current_year)

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    movie = fetch_movie_details(movie_id)
    credits_url = f'https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}'
    credits_response = requests.get(credits_url).json()
    cast = credits_response.get('cast', [])
    return render_template('movie_detail.html', movie=movie, cast=cast)

@app.route('/cast/<int:cast_id>')
def cast_detail(cast_id):
    cast_member = fetch_cast_member_details(cast_id)
    return render_template('cast_detail.html', cast_member=cast_member)


if __name__ == '__main__':
    app.run(debug=True)
