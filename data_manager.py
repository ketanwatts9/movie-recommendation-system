"""
data_manager.py
═════════════════════════════════════════════════
  TEAM MEMBER 2 - Lakshay— Data Manager
  Contains: DataManager class
  Handles ALL file reading and writing.
  Loads JSON → creates Movie/RegularUser/Admin objects
  Saves objects → back to JSON

  Key decision: dict {id → object} for O(1) lookup
  instead of O(n) list scanning.
═════════════════════════════════════════════════
"""

import json
from models import Movie, RegularUser, Admin


# ══════════════════════════════════════════════════
#  CLASS: DataManager
#  Single responsibility: only reads and writes files.
#  All other classes use this to get/save data.
# ══════════════════════════════════════════════════

class DataManager:

    def __init__(self, users_file="users.json", items_file="items.json"):
        self.users_file = users_file
        self.items_file = items_file

    # ── Load Methods ──────────────────────────────

    def load_users(self):
        """Read users.json → return list of RegularUser or Admin objects.
        Role stored in JSON determines which subclass is instantiated."""
        try:
            with open(self.users_file) as f:
                raw_list = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"  ⚠️  Could not load users file: {e}")
            return []

        users = []
        for data in raw_list:
            role = data.get("role", "regular")

            # Instantiate correct subclass based on stored role
            if role == "admin":
                user = Admin(
                    user_id          = data["user_id"],
                    name             = data["name"],
                    liked_items      = data.get("liked_items", []),
                    preferred_genres = data.get("preferred_genres", [])
                )
            else:
                user = RegularUser(
                    user_id          = data["user_id"],
                    name             = data["name"],
                    liked_items      = data.get("liked_items", []),
                    preferred_genres = data.get("preferred_genres", [])
                )
            users.append(user)
        return users

    def load_movies(self):
        """Read items.json → return list of Movie objects"""
        try:
            with open(self.items_file) as f:
                raw_list = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"  ⚠️  Could not load movies file: {e}")
            return []

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
