import requests

API_KEY = "bf365c6ed5c1c930c78b25c1315e9094"

def get_movie_details(movie_name):

    url = "https://api.themoviedb.org/3/search/movie"

    params = {
        "api_key": API_KEY,
        "query": movie_name
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    data = response.json()

    if data["results"]:

        movie = data["results"][0]

        poster = ""
        if movie.get("poster_path"):
            poster = "https://image.tmdb.org/t/p/w500" + movie["poster_path"]

        return {
            "rating": movie.get("vote_average"),
            "overview": movie.get("overview"),
            "release_date": movie.get("release_date"),
            "poster": poster
        }

    return None