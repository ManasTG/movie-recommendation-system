import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load datasets
movies = pd.read_csv("dataset/movie.csv")
tags = pd.read_csv("dataset/tag.csv")
links = pd.read_csv("dataset/link.csv")
genome_scores = pd.read_csv("dataset/genome_scores.csv")
genome_tags = pd.read_csv("dataset/genome_tags.csv")

print(movies.head())
# Dataset Information
print("\n===== Movies Dataset Information =====")
print(movies.info())

# Shape
print("\nDataset Shape:")
print(movies.shape)

# Columns
print("\nColumns:")
print(movies.columns)

# Missing Values
print("\nMissing Values:")
print(movies.isnull().sum())

# Duplicate Rows
print("\nDuplicate Rows:")
print(movies.duplicated().sum())

# ==========================================
# TAGS DATASET INFORMATION
# ==========================================

print("\n========== TAGS DATASET ==========")

print(tags.head())

print("\nShape:")
print(tags.shape)

print("\nColumns:")
print(tags.columns)

print("\nMissing Values:")
print(tags.isnull().sum())

print("\nDuplicate Rows:")
print(tags.duplicated().sum())

# ==========================================
# DATA CLEANING
# ==========================================

# Remove duplicate rows
movies.drop_duplicates(inplace=True)
tags.drop_duplicates(inplace=True)

# Fill missing values in tag column
tags["tag"] = tags["tag"].fillna("")

print("\n===== AFTER CLEANING =====")
print("Movies Shape :", movies.shape)
print("Tags Shape   :", tags.shape)

# ==========================================
# GROUP TAGS BY MOVIE
# ==========================================

tags_grouped = (
    tags.groupby("movieId")["tag"]
    .apply(lambda x: " ".join(x.astype(str)))
    .reset_index()
)

print("\n===== GROUPED TAGS =====")
print(tags_grouped.head())


# ==========================================
# MERGE MOVIES WITH GROUPED TAGS
# ==========================================

movie_data = pd.merge(
    movies,
    tags_grouped,
    on="movieId",
    how="left"
)

# Fill missing tags
movie_data["tag"] = movie_data["tag"].fillna("")

print("\n===== MERGED DATASET =====")
print(movie_data.head())

print("\nShape:")
print(movie_data.shape)


# ==========================================
# CREATE CONTENT COLUMN
# ==========================================

# Combine genres and tags
movie_data["content"] = movie_data["genres"] + " " + movie_data["tag"]

print("\n===== CONTENT COLUMN =====")
print(movie_data[["title", "content"]].head())

# ==========================================
# TF-IDF VECTORIZATION
# ==========================================

# ==========================================
# TF-IDF VECTORIZATION
# ==========================================

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

tfidf = TfidfVectorizer(
    stop_words="english",
    max_features=5000
)

tfidf_matrix = tfidf.fit_transform(movie_data["content"])

print("\n===== TF-IDF MATRIX =====")
print(tfidf_matrix.shape)

# ==========================================
# CREATE MOVIE INDEX
# ==========================================

indices = pd.Series(
    movie_data.index,
    index=movie_data["title"]
).drop_duplicates()

print("\n===== MOVIE INDEX =====")
print("Total Movies:", len(indices))

# ==========================================
# MOVIE RECOMMENDATION FUNCTION
# ==========================================

def recommend(movie_title, top_n=10):

    if movie_title not in indices:
        return []

    idx = indices[movie_title]

    cosine_scores = linear_kernel(
        tfidf_matrix[idx:idx+1],
        tfidf_matrix
    ).flatten()

    similar_indices = cosine_scores.argsort()[::-1][1:top_n+1]

    recommendations = []

    for i in similar_indices:
        recommendations.append({
            "title": movie_data.iloc[i]["title"],
            "genres": movie_data.iloc[i]["genres"],
            "score": round(float(cosine_scores[i]), 3)
        })

    return recommendations


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    movies = recommend("Toy Story (1995)")

    if not movies:
        print("Movie not found!")

    else:
        print("\nTop Recommendations:\n")

        for i, movie in enumerate(movies, start=1):
            print(f"{i}. {movie['title']}")
            print(f"   Genre : {movie['genres']}")
            print(f"   Score : {movie['score']}")
            print()