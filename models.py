"""
models.py
═════════════════════════════════════════════════
  TEAM MEMBER 1 — Data Models
  Contains: Movie class, User class
  These classes represent the core data objects
  used throughout the entire project.
═════════════════════════════════════════════════
"""


# ══════════════════════════════════════════════════
#  CLASS 1: Movie
#  Represents one movie in the catalog.
#  Holds all details: id, title, genre, year, rating
# ══════════════════════════════════════════════════

class Movie:

    def __init__(self, id, title, genre, year=2024, rating=0.0):
        self.id     = id
        self.title  = title
        self.genre  = genre.lower()
        self.year   = year
        self.rating = rating

    def to_dict(self):
        """Convert Movie object → plain dict (for saving to JSON)"""
        return {
            "id":     self.id,
            "title":  self.title,
            "genre":  self.genre,
            "year":   self.year,
            "rating": self.rating
        }

    def display(self):
        """Print a short summary of this movie"""
        print(f"\n    🎬 {self.title}  ({self.year})")
        print(f"       ID: {self.id}   |   Genre: {self.genre}   |   IMDb: {self.rating}")

    def __repr__(self):
        return f"Movie({self.id}, '{self.title}', {self.genre})"


# ══════════════════════════════════════════════════
#  CLASS 2: User
#  Represents one user with their preferences.
#  Holds: user_id, name, liked movie IDs, genres
# ══════════════════════════════════════════════════

class User:

    def __init__(self, user_id, name, liked_items=None, preferred_genres=None):
        self.user_id          = user_id
        self.name             = name
        self.liked_items      = liked_items or []        # list of movie IDs
        self.preferred_genres = preferred_genres or []   # list of genre strings

    def add_liked_item(self, movie_id):
        """Add a movie ID to this user's liked list (if not already there)"""
        if movie_id not in self.liked_items:
            self.liked_items.append(movie_id)
            return True
        return False  # already liked

    def has_seen(self, movie_id):
        """Check if user already liked / watched this movie"""
        return movie_id in self.liked_items

    def to_dict(self):
        """Convert User object → plain dict (for saving to JSON)"""
        return {
            "user_id":          self.user_id,
            "name":             self.name,
            "liked_items":      self.liked_items,
            "preferred_genres": self.preferred_genres
        }

    def display(self, movies_dict=None):
        """
        Print a summary card for this user.
        movies_dict is optional: pass {movie_id: Movie} to show titles instead of IDs.
        """
        # If we have the movie catalog, show titles — otherwise fall back to IDs
        if movies_dict:
            liked_names = [movies_dict[mid].title for mid in self.liked_items if mid in movies_dict]
        else:
            liked_names = self.liked_items

        print(f"\n  👤 User ID  : {self.user_id}")
        print(f"     Name     : {self.name}")
        print(f"     Genres   : {', '.join(self.preferred_genres) or 'None set'}")
        print(f"     Liked    : {', '.join(liked_names) or 'Nothing yet'}")

    def __repr__(self):
        return f"User({self.user_id}, '{self.name}')"
