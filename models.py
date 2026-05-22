"""
models.py
═════════════════════════════════════════════════
  TEAM MEMBER 1 - ketan — Data Models
  Contains: Movie class, User class (base),
            RegularUser class (inherits User),
            Admin class (inherits User)

  OOP concepts demonstrated:
    • Encapsulation  — private _role attribute with property
    • Inheritance    — RegularUser and Admin both extend User
    • Polymorphism   — each subclass overrides display()
═════════════════════════════════════════════════
"""


# ══════════════════════════════════════════════════
#  CLASS 1: Movie
#  Represents one movie in the catalog.
#  Holds all details: id, title, genre, year, rating
#
#  Data structure used: tuple for (genre, year) snapshot
#  Justification: tuples are immutable — good for read-only
#  snapshots that should never be accidentally changed.
# ══════════════════════════════════════════════════

class Movie:

    def __init__(self, id, title, genre, year=2024, rating=0.0):
        self.id     = id
        self.title  = title
        self.genre  = genre.lower()
        self.year   = year
        self.rating = rating

        # Tuple: immutable snapshot of (genre, year) — used for
        # quick comparisons without risking accidental mutation.
        self.genre_year = (self.genre, self.year)

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
#  CLASS 2: User  (BASE CLASS)
#  Represents a generic user — never instantiated
#  directly. Use RegularUser or Admin instead.
#
#  Encapsulation: _role is private; exposed via
#  the role property so subclasses can set it once
#  but external code cannot overwrite it freely.
# ══════════════════════════════════════════════════

class User:

    def __init__(self, user_id, name, liked_items=None, preferred_genres=None):
        self.user_id          = user_id
        self.name             = name
        self.liked_items      = liked_items or []        # list of movie IDs
        self.preferred_genres = preferred_genres or []   # list of genre strings
        self._role            = "user"                   # encapsulated: private

    # ── Encapsulation: read-only property ─────────
    @property
    def role(self):
        """Read-only access to the private _role attribute."""
        return self._role

    # ── Shared methods (used by all subclasses) ───

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
        """Convert User object → plain dict (for saving to JSON).
        Subclasses call super().to_dict() and add their own fields."""
        return {
            "user_id":          self.user_id,
            "name":             self.name,
            "liked_items":      self.liked_items,
            "preferred_genres": self.preferred_genres,
            "role":             self._role
        }

    # ── Polymorphism: overridden in each subclass ─
    def display(self, movies_dict=None):
        """Base display — subclasses override this for their own format."""
        print(f"\n  [{self._role.upper()}] {self.name} (ID: {self.user_id})")

    def __repr__(self):
        return f"User({self.user_id}, '{self.name}', role='{self._role}')"


# ══════════════════════════════════════════════════
#  CLASS 3: RegularUser  (inherits User)
#  A normal viewer — can like movies and get
#  recommendations. Overrides display() to show
#  liked movies and genre preferences.
# ══════════════════════════════════════════════════

class RegularUser(User):

    def __init__(self, user_id, name, liked_items=None, preferred_genres=None):
        super().__init__(user_id, name, liked_items, preferred_genres)
        self._role = "regular"   # set via inherited private attribute

    # ── POLYMORPHISM: overrides User.display() ────
    def display(self, movies_dict=None):
        """
        Show a full profile card for a regular user.
        If movies_dict is passed, show titles instead of IDs.
        """
        if movies_dict:
            liked_names = [movies_dict[mid].title
                           for mid in self.liked_items
                           if mid in movies_dict]
        else:
            liked_names = self.liked_items

        print(f"\n  👤 [{self._role}] User ID  : {self.user_id}")
        print(f"     Name              : {self.name}")
        print(f"     Preferred Genres  : {', '.join(self.preferred_genres) or 'None set'}")
        print(f"     Liked Movies      : {', '.join(liked_names) or 'Nothing yet'}")


# ══════════════════════════════════════════════════
#  CLASS 4: Admin  (inherits User)
#  A privileged user who can add/remove movies
#  and users. Overrides display() to show admin info.
#
#  Demonstrates inheritance: Admin reuses all of
#  User's methods and only adds/overrides what it needs.
# ══════════════════════════════════════════════════

class Admin(User):

    def __init__(self, user_id, name, liked_items=None, preferred_genres=None):
        super().__init__(user_id, name, liked_items, preferred_genres)
        self._role = "admin"

    def can_manage(self):
        """Admins have management privileges — regular users do not."""
        return True

    # ── POLYMORPHISM: overrides User.display() ────
    def display(self, movies_dict=None):
        """Admin display shows role badge and management status."""
        print(f"\n  🔑 [ADMIN] User ID  : {self.user_id}")
        print(f"     Name            : {self.name}")
        print(f"     Privileges      : Can add/remove movies and users")
        print(f"     Liked Movies    : {len(self.liked_items)} item(s) in list")

    def to_dict(self):
        """Extend parent to_dict with admin-specific fields."""
        base = super().to_dict()
        base["can_manage"] = True
        return base
