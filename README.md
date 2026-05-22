# 🎬 Movie Recommendation System

A terminal-based interactive movie recommendation system built with Python using Object-Oriented Programming and Jaccard Similarity to suggest movies based on user preferences.

---

## 👥 Team

| Person | File | Responsible For |
|--------|------|----------------|
| Ketan | `models.py` | `Movie` class, `User` class |
| Lakshay | `data_manager.py` | `DataManager` class |
| Parth | `recommender.py`, `main.py` | `RecommendationSystem` class, entry point |

---

## 📁 Project Structure

```
recommendation_system/
│
├── main.py              ← Run this to start the app
├── models.py            ← Movie and User classes (Person 1)
├── data_manager.py      ← File read/write logic (Person 2)
├── recommender.py       ← Recommendation engine + menu (Person 3)
│
├── users.json           ← Stores all user data and preferences
└── items.json           ← Stores the movie catalog
```

---

## ▶️ How to Run

**Requirements:** Python 3 only — no external libraries needed.

```bash
python main.py
```

Make sure all 4 `.py` files and both `.json` files are in the same folder.

---

## 🧭 Features (Menu Options)

```
1. Get Recommendations       — Enter User ID, genre filter, and count
2. View All Users            — See all users and the movies they liked
3. Add New User              — Add name, liked movies, genre preferences
4. Add a Liked Movie to User — Update a user's liked list anytime
5. Browse Movies by Genre    — Filter the full catalog by genre
6. Add New Movie to Catalog  — Add title, genre, year, IMDb rating
7. Compare Two Users         — See the Jaccard similarity score between two users
0. Exit
```

---

## 🧠 How the Algorithm Works

The system uses **Jaccard Similarity** to find users with similar taste:

```
Similarity(A, B) = |A ∩ B| / |A ∪ B|
```

- `A ∩ B` = movies both users liked (intersection)
- `A ∪ B` = all movies between them (union)
- Score ranges from `0.0` (nothing in common) to `1.0` (identical taste)

### Example

| User | Liked Movies |
|------|-------------|
| Alice | The Dark Knight, Superbad, Avengers |
| Bob | Superbad, The Godfather, Avengers |

```
Intersection = {Superbad, Avengers} = 2
Union        = {Dark Knight, Superbad, Avengers, Godfather} = 4
Score        = 2 / 4 = 0.50
```

Alice and Bob are 50% similar — so Bob's unseen movies get recommended to Alice.

### Fallback Logic

If a genre filter is applied but no similar user has liked a movie in that genre, the system **falls back** to the highest-rated unseen movies in that genre from the catalog.

---

## 📂 Input File Format

**users.json**
```json
[
  {
    "user_id": 1,
    "name": "Alice",
    "liked_items": ["movie1", "movie2"],
    "preferred_genres": ["action", "comedy"]
  }
]
```

**items.json**
```json
[
  {
    "id": "movie1",
    "title": "The Dark Knight",
    "genre": "action",
    "year": 2008,
    "rating": 9.0
  }
]
```

> ⚠️ At least **2 users** must exist in `users.json` for the system to start.

---

## 🏗️ OOP Design

### `Movie` — `models.py`
Represents a single movie in the catalog.
- `__init__()` — stores id, title, genre, year, rating
- `display()` — prints a formatted movie card
- `to_dict()` — converts object to dict for JSON saving

### `User` — `models.py`
Represents a user and their preferences.
- `add_liked_item(movie_id)` — adds a movie to liked list
- `has_seen(movie_id)` — checks if user already liked a movie
- `display(movies_dict)` — prints user card with movie titles (not IDs)
- `to_dict()` — converts object to dict for JSON saving

### `DataManager` — `data_manager.py`
Handles all file reading and writing.
- `load_users()` — reads `users.json` → returns list of `User` objects
- `load_movies()` — reads `items.json` → returns list of `Movie` objects
- `save_users(users)` — writes `User` objects back to `users.json`
- `save_movies(movies)` — writes `Movie` objects back to `items.json`
- `get_next_user_id()` / `get_next_movie_id()` — auto-generates new IDs

### `RecommendationSystem` — `recommender.py`
The main engine that runs everything.
- `jaccard_similarity(user_a, user_b)` — computes similarity score
- `get_recommendations(...)` — finds and returns top-N recommendations
- `run()` — starts the interactive menu loop
- `feature_*()` — one method per menu feature

---

## 📤 Sample Output

```
══════════════════════════════════════════════════════
  Recommendations for Alice
══════════════════════════════════════════════════════
  Movies already liked: The Dark Knight, Superbad, Avengers
  Genre filter applied: drama

  #1  The Godfather  (1972)
       Genre      : drama
       IMDb Rating: 9.2
       Why        : Bob liked it  [similarity: 0.5]

  #2  Schindler's List  (1993)
       Genre      : drama
       IMDb Rating: 8.9
       Why        : Carol liked it  [similarity: 0.2]
```

---

## 🔗 Import Chain

```
main.py
  └── RecommendationSystem  (recommender.py)
        └── DataManager     (data_manager.py)
              └── Movie, User  (models.py)
```

Each file only depends on the one below it — no circular imports.
