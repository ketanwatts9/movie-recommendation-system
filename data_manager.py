"""
data_manager.py
═════════════════════════════════════════════════
  TEAM MEMBER 2 — Data Manager
  Contains: DataManager class
  Handles ALL file reading and writing.
  Loads JSON → creates Movie/User objects
  Saves Movie/User objects → back to JSON
═════════════════════════════════════════════════
"""

import json
from models import Movie, User   # import our data model classes


# ══════════════════════════════════════════════════
#  CLASS: DataManager
#  Single responsibility: only reads and writes files
#  All other classes use this to get/save data
# ══════════════════════════════════════════════════

class DataManager:

    def __init__(self, users_file="users.json", items_file="items.json"):
        self.users_file = users_file
        self.items_file = items_file

    # ── Load Methods ──────────────────────────────

    def load_users(self):
        """Read users.json → return list of User objects"""
        with open(self.users_file) as f:
            raw_list = json.load(f)

        users = []
        for data in raw_list:
            user = User(
                user_id          = data["user_id"],
                name             = data["name"],
                liked_items      = data.get("liked_items", []),
                preferred_genres = data.get("preferred_genres", [])
            )
            users.append(user)
        return users

    def load_movies(self):
        """Read items.json → return list of Movie objects"""
        with open(self.items_file) as f:
            raw_list = json.load(f)

        movies = []
        for data in raw_list:
            movie = Movie(
                id     = data["id"],
                title  = data["title"],
                genre  = data["genre"],
                year   = data.get("year", 2024),
                rating = data.get("rating", 0.0)
            )
            movies.append(movie)
        return movies

    # ── Save Methods ──────────────────────────────

    def save_users(self, users):
        """Save list of User objects → users.json"""
        with open(self.users_file, "w") as f:
            json.dump([u.to_dict() for u in users], f, indent=2)

    def save_movies(self, movies):
        """Save list of Movie objects → items.json"""
        with open(self.items_file, "w") as f:
            json.dump([m.to_dict() for m in movies], f, indent=2)

    # ── ID Generator Helpers ──────────────────────

    def get_next_user_id(self, users):
        """Auto-generate the next available user ID"""
        return max(u.user_id for u in users) + 1 if users else 1

    def get_next_movie_id(self, movies):
        """Auto-generate the next available movie ID (movie1, movie2, ...)"""
        nums = []
        for m in movies:
            part = m.id.replace("movie", "")
            if part.isdigit():
                nums.append(int(part))
        return f"movie{max(nums) + 1}" if nums else "movie1"
